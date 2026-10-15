import pytest
from datetime import datetime, timezone, timedelta

from backend.app.domain.models.enums import UserRole, IncidentStatus, Priority, Impact, Urgency, ServiceTier
from backend.app.domain.models.user import Employee, Technician, Administrator
from backend.app.domain.models.service import ITService
from backend.app.domain.models.sla import SLAPolicy, SLATarget
from backend.app.domain.exceptions import (
    InvalidStateTransitionException,
    TechnicianCapacityExceededException,
    UnauthorizedActionException,
    EntityNotFoundException,
)
from backend.app.domain.factories.incident_factory import IncidentFactory
from backend.app.domain.strategies.assignment import SkillBasedAssignment, LeastLoadedAssignment, CompositeSmartAssignment
from backend.app.domain.strategies.priority import WeightedCriticalityStrategy, MatrixPriorityStrategy
from backend.app.domain.intelligence.duplicate_detector import DuplicateIncidentDetector
from backend.app.domain.intelligence.categorizer import IntelligentCategorizer
from backend.app.domain.intelligence.escalation_engine import AutomaticEscalationEngine
from backend.app.domain.observers.concrete import AuditObserver, NotificationObserver
from backend.app.infrastructure.persistence.in_memory_repo import (
    InMemoryIncidentRepository, InMemoryUserRepository, InMemoryServiceRepository
)
from backend.app.services.incident_service import IncidentService


@pytest.fixture
def test_setup():
    # Repositories
    user_repo = InMemoryUserRepository()
    service_repo = InMemoryServiceRepository()
    incident_repo = InMemoryIncidentRepository()

    # Users
    emp = Employee(email="alice@company.com", full_name="Alice Smith", department="Finance")
    tech_db = Technician(
        email="bob@company.com", full_name="Bob Jones", skills=["database", "sql"],
        max_active_load=2, current_active_load=0, performance_rating=4.8
    )
    tech_net = Technician(
        email="charlie@company.com", full_name="Charlie Brown", skills=["network", "firewall"],
        max_active_load=3, current_active_load=1, performance_rating=4.2
    )
    admin = Administrator(email="admin@company.com", full_name="Admin Dave")

    user_repo.save(emp)
    user_repo.save(tech_db)
    user_repo.save(tech_net)
    user_repo.save(admin)

    # Services
    srv_payment = ITService(
        name="Payment Gateway", description="Handles financial transactions",
        tier=ServiceTier.TIER_1_CRITICAL
    )
    srv_email = ITService(
        name="Internal Email", description="Company exchange",
        tier=ServiceTier.TIER_3
    )
    service_repo.save(srv_payment)
    service_repo.save(srv_email)

    service = IncidentService(incident_repo, user_repo, service_repo)
    return {
        "service": service,
        "emp": emp,
        "tech_db": tech_db,
        "tech_net": tech_net,
        "admin": admin,
        "srv_payment": srv_payment,
        "srv_email": srv_email,
        "repos": (incident_repo, user_repo, service_repo)
    }


# ==============================================================================
# TEST CASE 01: State Pattern Transition Validation (Invalid NEW -> CLOSED)
# ==============================================================================
def test_tc01_prevent_invalid_state_transition_new_to_closed(test_setup):
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="Payment down", description="Cannot process checkout",
        service=test_setup["srv_payment"], reporter=test_setup["emp"]
    )
    assert inc.status == IncidentStatus.NEW

    with pytest.raises(InvalidStateTransitionException) as excinfo:
        inc.close(test_setup["admin"])
    assert "Cannot close an incident from current state" in str(excinfo.value)
    assert inc.status == IncidentStatus.NEW


# ==============================================================================
# TEST CASE 02: Valid Full Lifecycle Transitions (State Pattern)
# ==============================================================================
def test_tc02_complete_valid_lifecycle_transitions(test_setup):
    s = test_setup["service"]
    emp = test_setup["emp"]
    tech = test_setup["tech_db"]
    admin = test_setup["admin"]

    # 1. Report (NEW -> Auto Assigned)
    inc, _ = s.report_incident(
        title="Database lock", description="Deadlock on user ledger table",
        service_id=test_setup["srv_payment"].id, reporter_id=emp.id,
        category="Database", auto_assign=False
    )
    assert inc.status == IncidentStatus.NEW

    # 2. Classify
    inc.classify("Database", emp)
    assert inc.status == IncidentStatus.CLASSIFIED

    # 3. Assign
    inc.assign(tech, admin)
    assert inc.status == IncidentStatus.ASSIGNED
    assert inc.assigned_technician.id == tech.id

    # 4. Acknowledge
    s.acknowledge_incident(inc.id, tech.id)
    assert inc.status == IncidentStatus.ACKNOWLEDGED

    # 5. Investigate
    s.start_investigation(inc.id, tech.id, "Analyzing transaction lock logs")
    assert inc.status == IncidentStatus.IN_PROGRESS

    # 6. Resolve
    s.resolve_incident(inc.id, tech.id, "Terminated orphan query session")
    assert inc.status == IncidentStatus.RESOLVED

    # 7. Verify
    s.verify_incident(inc.id, emp.id, is_confirmed=True, feedback="Working smoothly now!")
    assert inc.status == IncidentStatus.VERIFIED

    # 8. Close
    s.close_incident(inc.id, admin.id)
    assert inc.status == IncidentStatus.CLOSED


# ==============================================================================
# TEST CASE 03: Priority Calculation Strategy (Critical Service Matrix)
# ==============================================================================
def test_tc03_priority_calculation_critical_service(test_setup):
    strat = MatrixPriorityStrategy()
    # High impact on Tier 1 service -> Priority P1
    prio = strat.calculate_priority(Impact.HIGH, Urgency.HIGH, test_setup["srv_payment"])
    assert prio == Priority.P1

    # Low impact on Tier 3 service -> Priority P4
    prio_low = strat.calculate_priority(Impact.LOW, Urgency.LOW, test_setup["srv_email"])
    assert prio_low == Priority.P4


# ==============================================================================
# TEST CASE 04: Skill-Based Technician Assignment Strategy
# ==============================================================================
def test_tc04_skill_based_technician_assignment(test_setup):
    strat = SkillBasedAssignment()
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="Postgres crash", description="Fatal connection error",
        service=test_setup["srv_payment"], reporter=test_setup["emp"], category="database"
    )
    chosen = strat.select_technician(inc, [test_setup["tech_net"], test_setup["tech_db"]])
    assert chosen.id == test_setup["tech_db"].id
    assert chosen.has_skill("database")


# ==============================================================================
# TEST CASE 05: Least-Loaded Technician Assignment Strategy
# ==============================================================================
def test_tc05_least_loaded_technician_assignment(test_setup):
    strat = LeastLoadedAssignment()
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="General issue", description="Some issue",
        service=test_setup["srv_email"], reporter=test_setup["emp"]
    )
    # tech_db has load 0, tech_net has load 1
    chosen = strat.select_technician(inc, [test_setup["tech_net"], test_setup["tech_db"]])
    assert chosen.id == test_setup["tech_db"].id
    assert chosen.current_active_load == 0


# ==============================================================================
# TEST CASE 06: Workload Boundary & Capacity Exceeded Exception
# ==============================================================================
def test_tc06_technician_capacity_exceeded_exception(test_setup):
    tech = test_setup["tech_db"]
    tech.current_active_load = 2
    tech.max_active_load = 2
    assert tech.can_accept_workload() is False

    with pytest.raises(TechnicianCapacityExceededException):
        tech.allocate_ticket()


# ==============================================================================
# TEST CASE 07: SLA Target & Deadline Calculation
# ==============================================================================
def test_tc07_sla_deadline_computation(test_setup):
    policy = SLAPolicy("Standard")
    target_p1 = policy.get_target(Priority.P1)
    # P1 targets: 5 mins response, 30 mins resolution
    assert target_p1.response_minutes == 5
    assert target_p1.resolution_minutes == 30

    now = datetime.now(timezone.utc)
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="Critical Payment Outage", description="All payments failing",
        service=test_setup["srv_payment"], reporter=test_setup["emp"],
        explicit_priority=Priority.P1
    )
    assert (inc.sla_tracker.response_deadline - inc.created_at).total_seconds() == 5 * 60
    assert (inc.sla_tracker.resolution_deadline - inc.created_at).total_seconds() == 30 * 60


# ==============================================================================
# TEST CASE 08: SLA Proactive Risk Warning Detection
# ==============================================================================
def test_tc08_sla_risk_warning_detection(test_setup):
    created_at = datetime.now(timezone.utc) - timedelta(minutes=25)
    target = SLATarget(response_minutes=5, resolution_minutes=30)
    tracker = test_setup["srv_payment"].sla_policy.get_target(Priority.P1)
    
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="Slow DB query", description="Query takes 10s",
        service=test_setup["srv_payment"], reporter=test_setup["emp"],
        explicit_priority=Priority.P1
    )
    inc.created_at = created_at
    inc.sla_tracker.created_at = created_at
    inc.sla_tracker.resolution_deadline = created_at + timedelta(minutes=30)

    # 25 mins elapsed out of 30 mins total = 83% > 70% threshold
    assert inc.sla_tracker.is_resolution_at_risk(warning_ratio=0.70) is True


# ==============================================================================
# TEST CASE 09: Automatic Escalation on Unacknowledged SLA Breach
# ==============================================================================
def test_tc09_automatic_escalation_on_unacknowledged_breach(test_setup):
    engine = AutomaticEscalationEngine()
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="Unacknowledged P1 Outage", description="Complete disruption",
        service=test_setup["srv_payment"], reporter=test_setup["emp"],
        explicit_priority=Priority.P1
    )
    # Simulate past response deadline
    simulated_future = inc.sla_tracker.response_deadline + timedelta(minutes=2)
    level = engine.evaluate_incident(inc, current_time=simulated_future)
    assert level is not None
    # Action logged in audit
    actions = [log.action for log in inc.audit_logs]
    assert "AUTO_ESCALATED" in actions


# ==============================================================================
# TEST CASE 10: Intelligent Duplicate Incident Detection (NLP & Cosine Similarity)
# ==============================================================================
def test_tc10_intelligent_duplicate_detection(test_setup):
    detector = DuplicateIncidentDetector(similarity_threshold=0.35)
    factory = IncidentFactory()

    inc1 = factory.create_incident(
        title="Payment gateway unavailable",
        description="Users cannot complete debit card transactions at checkout",
        service=test_setup["srv_payment"], reporter=test_setup["emp"]
    )
    inc2 = factory.create_incident(
        title="Payment transaction failing",
        description="Unable to process card checkout transactions in payment application",
        service=test_setup["srv_payment"], reporter=test_setup["emp"]
    )

    duplicates = detector.find_potential_duplicates(inc2, [inc1])
    assert len(duplicates) == 1
    matched_inc, score = duplicates[0]
    assert matched_inc.id == inc1.id
    assert score >= 0.40


# ==============================================================================
# TEST CASE 11: Immutable Audit Trail Logging (Observer Pattern)
# ==============================================================================
def test_tc11_immutable_audit_trail_logging(test_setup):
    audit_obs = AuditObserver()
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="Router issue", description="Packet loss on floor 2",
        service=test_setup["srv_email"], reporter=test_setup["emp"]
    )
    inc.attach_observer(audit_obs)

    inc.classify("Network", test_setup["emp"])
    inc.assign(test_setup["tech_net"], test_setup["admin"])

    # Expect initial report + 2 state transitions = 3 records
    assert len(inc.audit_logs) == 3
    assert inc.audit_logs[0].action == "REPORTED"
    assert inc.audit_logs[1].action == "STATE_TRANSITION_CLASSIFIED"
    assert inc.audit_logs[2].action == "STATE_TRANSITION_ASSIGNED"


# ==============================================================================
# TEST CASE 12: Role-Based Authorization Enforcement
# ==============================================================================
def test_tc12_unauthorized_action_exception(test_setup):
    s = test_setup["service"]
    inc, _ = s.report_incident(
        title="Server fan failure", description="High noise from rack",
        service_id=test_setup["srv_email"].id, reporter_id=test_setup["emp"].id
    )

    # An employee cannot acknowledge or resolve an incident
    with pytest.raises(UnauthorizedActionException):
        s.acknowledge_incident(inc.id, technician_id=test_setup["emp"].id)

    with pytest.raises(UnauthorizedActionException):
        s.resolve_incident(inc.id, technician_id=test_setup["emp"].id, resolution_details="Fixed")


# ==============================================================================
# TEST CASE 13: Notification Observer Dispatch Mechanism
# ==============================================================================
def test_tc13_observer_pattern_notification_dispatch(test_setup):
    notice_obs = NotificationObserver()
    factory = IncidentFactory()
    inc = factory.create_incident(
        title="VPN Gateway Down", description="All employees locked out",
        service=test_setup["srv_payment"], reporter=test_setup["emp"]
    )
    inc.attach_observer(notice_obs)
    inc.classify("Network", test_setup["admin"])

    assert len(notice_obs.dispatched_notifications) == 1
    sent = notice_obs.dispatched_notifications[0]
    assert sent["type"] == "STATE_CHANGE"
    assert "CLASSIFIED" in sent["title"]


# ==============================================================================
# TEST CASE 14: Intelligent Category Inference
# ==============================================================================
def test_tc14_intelligent_categorizer_text_inference():
    categorizer = IntelligentCategorizer()
    cat_db = categorizer.suggest_category(
        title="PostgreSQL deadlock detected",
        description="SQL queries on table transactions are hanging indefinitely"
    )
    assert cat_db.value == "Database"

    cat_auth = categorizer.suggest_category(
        title="SSO login failure",
        description="Users cannot login with their password or MFA token"
    )
    assert cat_auth.value == "Authentication"


# ==============================================================================
# TEST CASE 15: Resolution Rejection & Re-open Lifecycle Feedback
# ==============================================================================
def test_tc15_resolution_verification_and_reopen_feedback(test_setup):
    s = test_setup["service"]
    inc, _ = s.report_incident(
        title="Slow checkout", description="Takes 45 seconds",
        service_id=test_setup["srv_payment"].id, reporter_id=test_setup["emp"].id,
        auto_assign=True
    )
    tech = inc.assigned_technician
    s.acknowledge_incident(inc.id, tech.id)
    s.start_investigation(inc.id, tech.id, "Investigating redis cache")
    s.resolve_incident(inc.id, tech.id, "Flushed redis cache")
    assert inc.status == IncidentStatus.RESOLVED

    # Employee rejects resolution -> must return to IN_PROGRESS
    s.verify_incident(inc.id, test_setup["emp"].id, is_confirmed=False, feedback="Still timing out!")
    assert inc.status == IncidentStatus.IN_PROGRESS
    assert "Still timing out!" in inc.resolution_feedback
