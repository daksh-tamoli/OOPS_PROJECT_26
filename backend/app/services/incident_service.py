from typing import List, Optional, Tuple, Dict, Any
from backend.app.domain.repositories.interfaces import IIncidentRepository, IUserRepository, IServiceRepository
from backend.app.domain.factories.incident_factory import IncidentFactory
from backend.app.domain.strategies.assignment import (
    IAssignmentStrategy, SkillBasedAssignment, LeastLoadedAssignment, RoundRobinAssignment, CompositeSmartAssignment
)
from backend.app.domain.strategies.priority import MatrixPriorityStrategy, WeightedCriticalityStrategy
from backend.app.domain.intelligence.duplicate_detector import DuplicateIncidentDetector
from backend.app.domain.intelligence.escalation_engine import AutomaticEscalationEngine
from backend.app.domain.observers.concrete import AuditObserver, NotificationObserver
from backend.app.domain.exceptions import EntityNotFoundException, UnauthorizedActionException
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.enums import UserRole, Impact, Urgency, Priority


class IncidentService:
    """
    Application Service orchestrating Domain Aggregates, Design Patterns,
    Intelligence modules, and Repositories.
    """
    def __init__(
        self,
        incident_repo: IIncidentRepository,
        user_repo: IUserRepository,
        service_repo: IServiceRepository
    ):
        self.incident_repo = incident_repo
        self.user_repo = user_repo
        self.service_repo = service_repo

        # Factories & Intelligence
        self.factory = IncidentFactory(priority_strategy=WeightedCriticalityStrategy())
        self.duplicate_detector = DuplicateIncidentDetector()
        self.escalation_engine = AutomaticEscalationEngine()

        # Assignment Strategies lookup (Strategy Pattern)
        self.assignment_strategies: Dict[str, IAssignmentStrategy] = {
            "skill": SkillBasedAssignment(),
            "load": LeastLoadedAssignment(),
            "round_robin": RoundRobinAssignment(),
            "smart": CompositeSmartAssignment(),
        }

        # Global Observers
        self.audit_observer = AuditObserver()
        self.notification_observer = NotificationObserver()

    def report_incident(
        self,
        title: str,
        description: str,
        service_id: str,
        reporter_id: str,
        impact: Impact = Impact.MEDIUM,
        urgency: Urgency = Urgency.MEDIUM,
        category: Optional[str] = None,
        auto_assign: bool = True,
        assignment_strategy: str = "smart"
    ) -> Tuple[Incident, List[Tuple[Incident, float]]]:
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise EntityNotFoundException(f"Service with ID '{service_id}' not found.")

        reporter = self.user_repo.get_by_id(reporter_id)
        if not reporter:
            raise EntityNotFoundException(f"User with ID '{reporter_id}' not found.")

        # Factory creates incident
        incident = self.factory.create_incident(
            title=title,
            description=description,
            service=service,
            reporter=reporter,
            impact=impact,
            urgency=urgency,
            category=category
        )

        # Attach observers
        incident.attach_observer(self.audit_observer)
        incident.attach_observer(self.notification_observer)

        # Notify initial creation
        self.notification_observer.on_incident_created(incident)

        # Intelligent feature 1: Check for duplicates
        existing_incidents = self.incident_repo.get_all()
        potential_duplicates = self.duplicate_detector.find_potential_duplicates(incident, existing_incidents)
        if potential_duplicates:
            top_dup, top_score = potential_duplicates[0]
            incident.parent_incident_id = top_dup.id
            incident.record_action(
                actor=reporter,
                action="DUPLICATE_FLAGGED",
                description=f"Potential duplicate of {top_dup.id} (Similarity: {top_score * 100:.1f}%)"
            )

        # Auto-assignment if requested
        if auto_assign:
            try:
                available_techs = self.user_repo.get_technicians(available_only=True)
                if available_techs:
                    strat = self.assignment_strategies.get(assignment_strategy, self.assignment_strategies["smart"])
                    chosen_tech = strat.select_technician(incident, available_techs)
                    incident.assign(chosen_tech, reporter)
                    self.user_repo.save(chosen_tech)
            except Exception as e:
                incident.record_action(reporter, "ASSIGNMENT_PENDING", f"Auto-assignment skipped: {str(e)}")

        self.incident_repo.save(incident)
        return incident, potential_duplicates

    def assign_technician(
        self,
        incident_id: str,
        actor_id: str,
        technician_id: Optional[str] = None,
        strategy_name: str = "skill"
    ) -> Incident:
        incident = self.get_incident(incident_id)
        actor = self.user_repo.get_by_id(actor_id)
        if not actor:
            raise EntityNotFoundException("Actor not found.")

        if technician_id:
            tech = self.user_repo.get_by_id(technician_id)
            if not tech or tech.role != UserRole.TECHNICIAN:
                raise EntityNotFoundException(f"Technician '{technician_id}' not found.")
            chosen_tech = tech
        else:
            available_techs = self.user_repo.get_technicians(available_only=True)
            strategy = self.assignment_strategies.get(strategy_name, self.assignment_strategies["skill"])
            chosen_tech = strategy.select_technician(incident, available_techs)

        incident.assign(chosen_tech, actor)
        self.user_repo.save(chosen_tech)
        self.incident_repo.save(incident)
        return incident

    def acknowledge_incident(self, incident_id: str, technician_id: str) -> Incident:
        incident = self.get_incident(incident_id)
        tech = self.user_repo.get_by_id(technician_id)
        if not tech or tech.role != UserRole.TECHNICIAN:
            raise UnauthorizedActionException("Only a technician can acknowledge an incident.")

        incident.acknowledge(tech)
        self.incident_repo.save(incident)
        return incident

    def start_investigation(self, incident_id: str, technician_id: str, notes: str) -> Incident:
        incident = self.get_incident(incident_id)
        tech = self.user_repo.get_by_id(technician_id)
        if not tech or tech.role != UserRole.TECHNICIAN:
            raise UnauthorizedActionException("Only a technician can start an investigation.")

        incident.start_investigation(notes, tech)
        self.incident_repo.save(incident)
        return incident

    def resolve_incident(self, incident_id: str, technician_id: str, resolution_details: str) -> Incident:
        incident = self.get_incident(incident_id)
        tech = self.user_repo.get_by_id(technician_id)
        if not tech or tech.role != UserRole.TECHNICIAN:
            raise UnauthorizedActionException("Only a technician can resolve an incident.")

        incident.resolve(resolution_details, tech)
        if incident.assigned_technician:
            self.user_repo.save(incident.assigned_technician)
        self.incident_repo.save(incident)
        return incident

    def verify_incident(self, incident_id: str, actor_id: str, is_confirmed: bool, feedback: str = "") -> Incident:
        incident = self.get_incident(incident_id)
        actor = self.user_repo.get_by_id(actor_id)
        if not actor:
            raise EntityNotFoundException("Actor not found.")

        incident.verify(is_confirmed, actor, feedback)
        self.incident_repo.save(incident)
        return incident

    def close_incident(self, incident_id: str, actor_id: str) -> Incident:
        incident = self.get_incident(incident_id)
        actor = self.user_repo.get_by_id(actor_id)
        if not actor:
            raise EntityNotFoundException("Actor not found.")

        incident.close(actor)
        self.incident_repo.save(incident)
        return incident

    def get_incident(self, incident_id: str) -> Incident:
        inc = self.incident_repo.get_by_id(incident_id)
        if not inc:
            raise EntityNotFoundException(f"Incident '{incident_id}' not found.")
        # Ensure observers are hooked up
        inc.attach_observer(self.audit_observer)
        inc.attach_observer(self.notification_observer)
        return inc

    def run_sla_and_escalation_cycle(self) -> Dict[str, Any]:
        """Periodic SLA checker and automatic escalation engine runner."""
        all_incidents = self.incident_repo.get_all()
        escalated = []
        breached = []
        at_risk = []

        for inc in all_incidents:
            if inc.status.value in ("RESOLVED", "VERIFIED", "CLOSED"):
                continue

            # Check breach status
            if inc.sla_tracker.check_breach():
                breached.append(inc.id)

            # Check risk status
            if inc.sla_tracker.is_resolution_at_risk():
                at_risk.append(inc.id)

            # Evaluate automatic escalation
            esc_level = self.escalation_engine.evaluate_incident(inc)
            if esc_level:
                escalated.append({"incident_id": inc.id, "escalated_to": esc_level})
                self.incident_repo.save(inc)

        return {
            "total_open": len([i for i in all_incidents if i.status.value not in ("VERIFIED", "CLOSED")]),
            "breached_count": len(breached),
            "at_risk_count": len(at_risk),
            "escalated_incidents": escalated
        }

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Generates operational reports and metrics (Page 9 of PDF)."""
        incidents = self.incident_repo.get_all()
        technicians = self.user_repo.get_technicians()

        total = len(incidents)
        open_count = len([i for i in incidents if i.status.value not in ("CLOSED", "VERIFIED")])
        critical = len([i for i in incidents if i.priority == Priority.P1])
        resolved = len([i for i in incidents if i.status.value in ("RESOLVED", "VERIFIED", "CLOSED")])
        sla_violations = len([i for i in incidents if i.sla_tracker.check_breach()])

        tech_workload = [
            {
                "id": t.id,
                "name": t.full_name,
                "active_incidents": t.current_active_load,
                "max_capacity": t.max_active_load,
                "rating": t.performance_rating,
                "skills": t.skills
            }
            for t in technicians
        ]

        service_breakdown = {}
        category_breakdown = {}
        for inc in incidents:
            s_name = inc.service.name
            service_breakdown[s_name] = service_breakdown.get(s_name, 0) + 1
            cat = inc.category
            category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

        return {
            "total_incidents": total,
            "open_incidents": open_count,
            "critical_incidents": critical,
            "resolved_incidents": resolved,
            "sla_violations": sla_violations,
            "technician_workload": tech_workload,
            "service_analysis": service_breakdown,
            "category_analysis": category_breakdown
        }
