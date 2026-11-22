"""Database cleanup and realistic dummy data seeder for I-ITSM."""
import sqlite3
from datetime import datetime, timezone, timedelta
from backend.app.domain.models.user import User, Employee, Technician, Administrator
from backend.app.domain.models.service import ITService
from backend.app.domain.models.enums import ServiceTier, Priority, Impact, Urgency
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.audit import AuditRecord
from backend.app.domain.states.incident_state import (
    NewState, ClassifiedState, AssignedState, AcknowledgedState,
    InProgressState, ResolvedState, VerifiedState, ClosedState
)


def reset_and_seed_database(db_path: str = "backend/itsm.db"):
    """Completely resets database, clears email outbox, and seeds realistic dummy users, services, and incidents."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Clear tables
    cur.execute("DELETE FROM audit_records;")
    cur.execute("DELETE FROM incidents;")
    cur.execute("DELETE FROM users;")
    cur.execute("DELETE FROM services;")
    conn.commit()
    conn.close()

    from backend.app.infrastructure.persistence.sqlite_repo import (
        SqliteUserRepository, SqliteServiceRepository, SqliteIncidentRepository, init_sqlite_db
    )
    from backend.app.infrastructure.email.smtp_service import EmailService

    # Clear email outbox
    EmailService().clear_outbox()

    session_factory = init_sqlite_db(f"sqlite:///{db_path}")
    user_repo = SqliteUserRepository(session_factory)
    service_repo = SqliteServiceRepository(session_factory)
    incident_repo = SqliteIncidentRepository(session_factory, user_repo, service_repo)

    # 1. Services
    services = [
        ITService(
            service_id="srv-payment",
            name="Payment Gateway",
            description="Processes credit cards, UPI, and campus POS transactions",
            tier=ServiceTier.TIER_1_CRITICAL,
            dependencies=["srv-db", "srv-auth"]
        ),
        ITService(
            service_id="srv-auth",
            name="Single Sign-On (SSO)",
            description="Central authentication and LDAP identity provider",
            tier=ServiceTier.TIER_1_CRITICAL,
            dependencies=["srv-db"]
        ),
        ITService(
            service_id="srv-db",
            name="Core PostgreSQL DB",
            description="Primary organizational relational database clusters",
            tier=ServiceTier.TIER_1_CRITICAL,
            dependencies=[]
        ),
        ITService(
            service_id="srv-cloud",
            name="Cloud Storage & CDN",
            description="S3 buckets and media delivery assets",
            tier=ServiceTier.TIER_2,
            dependencies=["srv-auth"]
        ),
        ITService(
            service_id="srv-email",
            name="Internal Mail Exchange",
            description="Corporate messaging, relays, and Exchange SMTP gateway",
            tier=ServiceTier.TIER_3,
            dependencies=["srv-cloud"]
        ),
    ]
    for s in services:
        service_repo.save(s)

    # 2. Realistic Dummy Users (all initialized with standard password: password123)
    default_hash = User.hash_password("password123")

    admin = Administrator(
        user_id="user-admin-1",
        email="admin@itsm.local",
        full_name="Sarah Connor (IT Manager)",
        hashed_password=default_hash
    )

    tech_devon = Technician(
        user_id="tech-101",
        email="devon@itsm.local",
        full_name="Devon Vance (DB Specialist)",
        skills=["database", "sql", "storage", "postgres"],
        max_active_load=5,
        current_active_load=0,
        experience_years=5.0,
        performance_rating=4.9,
        hashed_password=default_hash
    )
    tech_maya = Technician(
        user_id="tech-102",
        email="maya@itsm.local",
        full_name="Maya Lin (Network & Cloud)",
        skills=["network", "cloud", "security", "vpn"],
        max_active_load=5,
        current_active_load=0,
        experience_years=4.0,
        performance_rating=4.8,
        hashed_password=default_hash
    )
    tech_liam = Technician(
        user_id="tech-103",
        email="liam@itsm.local",
        full_name="Liam Gallagher (App & Auth)",
        skills=["application", "authentication", "software", "sso"],
        max_active_load=4,
        current_active_load=0,
        experience_years=3.2,
        performance_rating=4.6,
        hashed_password=default_hash
    )
    tech_marcus = Technician(
        user_id="tech-104",
        email="marcus@itsm.local",
        full_name="Marcus Reid (Infrastructure & SysAdmin)",
        skills=["hardware", "infrastructure", "linux", "systems"],
        max_active_load=5,
        current_active_load=0,
        experience_years=4.5,
        performance_rating=4.7,
        hashed_password=default_hash
    )

    emp_alice = Employee(
        user_id="user-emp-1",
        email="alice@company.com",
        full_name="Alice Smith (Finance)",
        department="Finance",
        hashed_password=default_hash
    )
    emp_john = Employee(
        user_id="user-emp-2",
        email="john@company.com",
        full_name="John Doe (Engineering)",
        department="Engineering",
        hashed_password=default_hash
    )
    emp_carol = Employee(
        user_id="user-emp-3",
        email="carol@company.com",
        full_name="Carol Danvers (Operations)",
        department="Operations",
        hashed_password=default_hash
    )

    all_users = [admin, tech_devon, tech_maya, tech_liam, tech_marcus, emp_alice, emp_john, emp_carol]
    for u in all_users:
        user_repo.save(u)

    now = datetime.now(timezone.utc)

    # 3. Clean Diverse Incidents (across different statuses, priorities, services)
    # Incident 1: P1 Critical - IN_PROGRESS
    inc1 = Incident(
        incident_id="INC-1001",
        title="Stripe payment gateway deadlocked — checkout 504 errors",
        description="Campus store and tuition debit payments failing across all terminals with postgres connection timeouts.",
        service=services[0],
        reporter=emp_alice,
        priority=Priority.P1,
        category="Payment",
        impact=Impact.CRITICAL,
        urgency=Urgency.CRITICAL,
        created_at=now - timedelta(minutes=18),
    )
    inc1.assigned_technician = tech_devon
    inc1._state = InProgressState()
    inc1.sla_tracker.response_deadline = now - timedelta(minutes=13)
    inc1.sla_tracker.resolution_deadline = now + timedelta(minutes=12)
    inc1.sla_tracker.responded_at = now - timedelta(minutes=15)
    inc1.investigation_notes = [
        "Inspected active locks in pg_stat_activity.",
        "Identified lock contention on settlement ledger batch job."
    ]
    inc1.audit_logs = [
        AuditRecord("aud-101", inc1.id, emp_alice.id, emp_alice.full_name, "REPORT", "NONE", "NEW", "Incident logged via portal", now - timedelta(minutes=18)),
        AuditRecord("aud-102", inc1.id, admin.id, admin.full_name, "ASSIGN", "NEW", "ASSIGNED", f"Assigned to {tech_devon.full_name} via Skill-Based Strategy", now - timedelta(minutes=17)),
        AuditRecord("aud-103", inc1.id, tech_devon.id, tech_devon.full_name, "ACKNOWLEDGE", "ASSIGNED", "ACKNOWLEDGED", "Technician acknowledged ticket triage", now - timedelta(minutes=15)),
        AuditRecord("aud-104", inc1.id, tech_devon.id, tech_devon.full_name, "INVESTIGATE", "ACKNOWLEDGED", "IN_PROGRESS", "Started root-cause analysis on connection pool", now - timedelta(minutes=10))
    ]

    # Incident 2: P2 High - ACKNOWLEDGED
    inc2 = Incident(
        incident_id="INC-1002",
        title="Campus VPN gateway dropouts in Engineering Lab 3",
        description="Engineering workstations losing WireGuard tunnel connectivity intermittently during compile jobs.",
        service=services[1],
        reporter=emp_john,
        priority=Priority.P2,
        category="Network",
        impact=Impact.HIGH,
        urgency=Urgency.HIGH,
        created_at=now - timedelta(minutes=45),
    )
    inc2.assigned_technician = tech_maya
    inc2._state = AcknowledgedState()
    inc2.sla_tracker.response_deadline = now - timedelta(minutes=30)
    inc2.sla_tracker.resolution_deadline = now + timedelta(minutes=75)
    inc2.sla_tracker.responded_at = now - timedelta(minutes=32)
    inc2.investigation_notes = ["Testing MTU 1420 fragmentation across gateway tunnels."]
    inc2.audit_logs = [
        AuditRecord("aud-201", inc2.id, emp_john.id, emp_john.full_name, "REPORT", "NONE", "NEW", "Incident reported by user", now - timedelta(minutes=45)),
        AuditRecord("aud-202", inc2.id, admin.id, admin.full_name, "ASSIGN", "NEW", "ASSIGNED", f"Assigned to {tech_maya.full_name}", now - timedelta(minutes=40)),
        AuditRecord("aud-203", inc2.id, tech_maya.id, tech_maya.full_name, "ACKNOWLEDGE", "ASSIGNED", "ACKNOWLEDGED", "Ticket acknowledged by network lead", now - timedelta(minutes=32))
    ]

    # Incident 3: P3 Medium - ASSIGNED
    inc3 = Incident(
        incident_id="INC-1003",
        title="Cloud Storage media upload latency spike",
        description="Asset library uploads taking >45 seconds for images above 5MB.",
        service=services[3],
        reporter=emp_carol,
        priority=Priority.P3,
        category="Cloud",
        impact=Impact.MEDIUM,
        urgency=Urgency.LOW,
        created_at=now - timedelta(minutes=10),
    )
    inc3.assigned_technician = tech_marcus
    inc3._state = AssignedState()
    inc3.sla_tracker.response_deadline = now + timedelta(minutes=50)
    inc3.sla_tracker.resolution_deadline = now + timedelta(minutes=470)
    inc3.audit_logs = [
        AuditRecord("aud-301", inc3.id, emp_carol.id, emp_carol.full_name, "REPORT", "NONE", "NEW", "Report logged via Web UI", now - timedelta(minutes=10)),
        AuditRecord("aud-302", inc3.id, admin.id, admin.full_name, "ASSIGN", "NEW", "ASSIGNED", f"Assigned to {tech_marcus.full_name} via Least-Loaded Strategy", now - timedelta(minutes=8))
    ]

    # Incident 4: P2 High - RESOLVED
    inc4 = Incident(
        incident_id="INC-1004",
        title="Single Sign-On LDAP authentication sync timeout",
        description="Employee portal throwing 500 internal server error during OAuth token renewal.",
        service=services[1],
        reporter=emp_alice,
        priority=Priority.P2,
        category="Authentication",
        impact=Impact.HIGH,
        urgency=Urgency.HIGH,
        created_at=now - timedelta(hours=3),
    )
    inc4.assigned_technician = tech_liam
    inc4._state = ResolvedState()
    inc4.sla_tracker.response_deadline = now - timedelta(hours=2, minutes=45)
    inc4.sla_tracker.resolution_deadline = now - timedelta(hours=1)
    inc4.sla_tracker.responded_at = now - timedelta(hours=2, minutes=50)
    inc4.sla_tracker.resolved_at = now - timedelta(minutes=20)
    inc4.resolution_details = "Rotated expired SAML signing certificate and flushed Redis authentication token cache."
    inc4.resolution_feedback = "Single Sign-On authentication restored and verified operational."
    inc4.investigation_notes = ["Re-issued 2048-bit RSA token signing cert.", "Flushed stale sessions."]
    inc4.audit_logs = [
        AuditRecord("aud-401", inc4.id, emp_alice.id, emp_alice.full_name, "REPORT", "NONE", "NEW", "SSO failure logged", now - timedelta(hours=3)),
        AuditRecord("aud-402", inc4.id, tech_liam.id, tech_liam.full_name, "RESOLVE", "IN_PROGRESS", "RESOLVED", "Resolution deployed: rotated SAML certificate", now - timedelta(minutes=20))
    ]

    # Incident 5: P4 Low - CLOSED
    inc5 = Incident(
        incident_id="INC-1005",
        title="Internal mail relay rate limit warning",
        description="Postfix outgoing queue exceeding 5,000 messages during monthly newsletter dispatch.",
        service=services[4],
        reporter=emp_john,
        priority=Priority.P4,
        category="Application",
        impact=Impact.LOW,
        urgency=Urgency.LOW,
        created_at=now - timedelta(days=1),
    )
    inc5.assigned_technician = tech_liam
    inc5._state = ClosedState()
    inc5.sla_tracker.response_deadline = now - timedelta(hours=20)
    inc5.sla_tracker.resolution_deadline = now - timedelta(hours=8)
    inc5.sla_tracker.responded_at = now - timedelta(hours=22)
    inc5.sla_tracker.resolved_at = now - timedelta(hours=10)
    inc5.resolution_details = "Increased Postfix queue concurrency rate limit from 20 to 50 threads."
    inc5.audit_logs = [
        AuditRecord("aud-501", inc5.id, emp_john.id, emp_john.full_name, "REPORT", "NONE", "NEW", "Rate limit ticket logged", now - timedelta(days=1)),
        AuditRecord("aud-502", inc5.id, admin.id, admin.full_name, "CLOSE", "VERIFIED", "CLOSED", "Ticket officially verified and closed", now - timedelta(hours=8))
    ]

    # Incident 6: P2 High - Correlated Duplicate of INC-1001 (gives demonstration for duplicate detection & cleanup)
    inc6 = Incident(
        incident_id="INC-1006",
        title="Payment terminal gateway connection refused",
        description="Point-of-sale checkout registers reporting payment gateway unavailable.",
        service=services[0],
        reporter=emp_carol,
        priority=Priority.P2,
        category="Payment",
        impact=Impact.HIGH,
        urgency=Urgency.HIGH,
        created_at=now - timedelta(minutes=12),
    )
    inc6.assigned_technician = tech_devon
    inc6._state = AssignedState()
    inc6.parent_incident_id = "INC-1001"
    inc6.is_duplicate = True
    inc6.duplicate_of_id = "INC-1001"
    inc6.sla_tracker.response_deadline = now + timedelta(minutes=3)
    inc6.sla_tracker.resolution_deadline = now + timedelta(minutes=108)
    inc6.audit_logs = [
        AuditRecord("aud-601", inc6.id, emp_carol.id, emp_carol.full_name, "REPORT", "NONE", "NEW", "Reported by POS terminal operator", now - timedelta(minutes=12)),
        AuditRecord("aud-602", inc6.id, emp_carol.id, emp_carol.full_name, "DUPLICATE_FLAGGED", "NEW", "ASSIGNED", "Potential duplicate of INC-1001 (Similarity: 68.4%)", now - timedelta(minutes=11))
    ]

    for inc in [inc1, inc2, inc3, inc4, inc5, inc6]:
        incident_repo.save(inc)

    # Set accurate technician active loads
    tech_devon.current_active_load = 2  # inc1 and inc6
    tech_maya.current_active_load = 1   # inc2
    tech_marcus.current_active_load = 1 # inc3
    tech_liam.current_active_load = 0   # inc4 is resolved, inc5 is closed
    user_repo.save(tech_devon)
    user_repo.save(tech_maya)
    user_repo.save(tech_marcus)
    user_repo.save(tech_liam)

    print("Successfully reset and seeded clean dummy database!")


if __name__ == "__main__":
    reset_and_seed_database()
