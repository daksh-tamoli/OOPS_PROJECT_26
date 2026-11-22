from typing import List, Optional, Tuple, Dict, Any
from backend.app.domain.repositories.interfaces import IIncidentRepository, IUserRepository, IServiceRepository
from backend.app.domain.factories.incident_factory import IncidentFactory
from backend.app.domain.strategies.assignment import (
    IAssignmentStrategy, SkillBasedAssignment, LeastLoadedAssignment, RoundRobinAssignment, CompositeSmartAssignment
)
from backend.app.domain.strategies.priority import MatrixPriorityStrategy, WeightedCriticalityStrategy
from backend.app.domain.intelligence.duplicate_detector import DuplicateIncidentDetector
from backend.app.domain.intelligence.escalation_engine import AutomaticEscalationEngine
from backend.app.domain.intelligence.resolution_recommender import ResolutionRecommender
from backend.app.domain.observers.concrete import AuditObserver, NotificationObserver, InAppNotificationObserver
from backend.app.domain.exceptions import (
    EntityNotFoundException,
    ServiceNotFoundException,
    InvalidIncidentException,
    UnauthorizedActionException,
    WorkloadExceededException,
    MissingSLAConfigException
)
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
        self.resolution_recommender = ResolutionRecommender()

        # Dynamic Default Assignment Strategy Configurable by Admin
        self.default_assignment_strategy: str = "smart"

        # Assignment Strategies lookup (Strategy Pattern)
        self.assignment_strategies: Dict[str, IAssignmentStrategy] = {
            "skill": SkillBasedAssignment(),
            "load": LeastLoadedAssignment(),
            "round_robin": RoundRobinAssignment(),
            "smart": CompositeSmartAssignment(),
        }

        # Global Observers: Distinct Channels (Email Outbox + In-App Notification Center)
        self.audit_observer = AuditObserver()
        self.notification_observer = NotificationObserver()
        self.in_app_notification_observer = InAppNotificationObserver()

    def set_default_assignment_strategy(self, strategy: str) -> None:
        """Admin dynamic configuration: switch the active assignment strategy."""
        normalized = strategy.lower().replace("-", "_")
        if normalized not in self.assignment_strategies:
            normalized = "smart"
        self.default_assignment_strategy = normalized

    def get_default_assignment_strategy(self) -> str:
        return self.default_assignment_strategy


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
            raise ServiceNotFoundException(f"Service with ID '{service_id}' not found.")

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

        # Attach observers (Distinct Channels: Audit, External Email, In-App Center)
        incident.attach_observer(self.audit_observer)
        incident.attach_observer(self.notification_observer)
        incident.attach_observer(self.in_app_notification_observer)

        # Notify initial creation
        self.notification_observer.on_incident_created(incident)
        self.in_app_notification_observer.on_incident_created(incident)

        # Intelligent feature 1: Check for duplicates
        existing_incidents = self.incident_repo.get_all()
        potential_duplicates = self.duplicate_detector.find_potential_duplicates(incident, existing_incidents)
        if potential_duplicates:
            top_dup, top_score = potential_duplicates[0]
            if getattr(self, "enforce_duplicate_prevention", False) and top_score >= 0.90:
                from backend.app.domain.exceptions import DuplicateIncidentException
                raise DuplicateIncidentException(f"Exact duplicate incident already active: '{top_dup.id}' ({top_dup.title}).")
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
        if not is_confirmed and not (feedback and feedback.strip()):
            from backend.app.domain.exceptions import InvalidUserInputException
            raise InvalidUserInputException("Reopening an incident requires explanatory feedback.")

        incident.verify(is_confirmed, actor, feedback)
        self.incident_repo.save(incident)
        return incident

    def link_duplicate(self, incident_id: str, parent_id: str, actor_id: str) -> Incident:
        """Explicitly links an incident as duplicate of another incident."""
        if incident_id == parent_id:
            from backend.app.domain.exceptions import DuplicateIncidentException
            raise DuplicateIncidentException("Cannot link incident as a duplicate of itself.")
        incident = self.get_incident(incident_id)
        parent = self.get_incident(parent_id)
        actor = self.user_repo.get_by_id(actor_id)
        if not actor:
            raise EntityNotFoundException("Actor not found.")
        incident.parent_incident_id = parent.id
        incident.is_duplicate = True
        incident.duplicate_of_id = parent.id
        incident.record_action(
            actor=actor,
            action="DUPLICATE_LINKED",
            description=f"Manually linked as duplicate of parent incident '{parent.id}'"
        )
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
            raise InvalidIncidentException(f"Incident '{incident_id}' not found.")
        # Ensure observers are hooked up
        inc.attach_observer(self.audit_observer)
        inc.attach_observer(self.notification_observer)
        inc.attach_observer(self.in_app_notification_observer)
        return inc

    def request_additional_info(self, incident_id: str, technician_id: str, question: str) -> Incident:
        """Technician requests additional clarification or diagnostic information from reporter."""
        incident = self.get_incident(incident_id)
        tech = self.user_repo.get_by_id(technician_id)
        if not tech or tech.role != UserRole.TECHNICIAN:
            raise UnauthorizedActionException("Only an assigned technician can request additional info.")
        formatted_note = f"[INFO REQUESTED by {tech.full_name}]: {question}"
        incident.investigation_notes.append(formatted_note)
        incident.record_action(tech, "INFO_REQUESTED", formatted_note)
        self.incident_repo.save(incident)
        return incident

    def add_additional_info(self, incident_id: str, actor_id: str, info_text: str) -> Incident:
        """Reporter or Employee adds additional info or responds to technician questions."""
        incident = self.get_incident(incident_id)
        actor = self.user_repo.get_by_id(actor_id)
        if not actor:
            raise EntityNotFoundException("Actor not found.")
        formatted_note = f"[ADDITIONAL INFO from {actor.full_name}]: {info_text}"
        incident.investigation_notes.append(formatted_note)
        incident.record_action(actor, "INFO_PROVIDED", formatted_note)
        self.incident_repo.save(incident)
        return incident

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

    def get_suggested_resolutions(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves suggested resolutions for an incident (Feature G & Innovation Pillar).
        Leverages NLP matching against historical resolved incidents and expert SOP runbooks.
        """
        incident = self.get_incident(incident_id)
        all_incidents = self.incident_repo.get_all()
        return self.resolution_recommender.get_recommendations(incident, all_incidents)

    def get_service_topology(self) -> Dict[str, Any]:
        """
        Builds live service dependency topology graph and operational health status.
        Demonstrates Incident Correlation & Service Dependency Graph (Innovation Pillar).
        """
        services = self.service_repo.get_all()
        incidents = self.incident_repo.get_all()

        active_per_service: Dict[str, List[Incident]] = {}
        for inc in incidents:
            if inc.status.value not in ("RESOLVED", "VERIFIED", "CLOSED"):
                s_id = inc.service.id
                if s_id not in active_per_service:
                    active_per_service[s_id] = []
                active_per_service[s_id].append(inc)

        nodes = []
        edges = []

        for s in services:
            active_list = active_per_service.get(s.id, [])
            critical_count = len([i for i in active_list if i.priority.value == "P1"])
            open_count = len(active_list)

            if critical_count > 0:
                health = "CRITICAL"
            elif open_count > 0:
                health = "DEGRADED"
            else:
                health = "OPERATIONAL"

            nodes.append({
                "id": s.id,
                "name": s.name,
                "tier": s.tier.value if hasattr(s.tier, "value") else str(s.tier),
                "description": s.description,
                "health": health,
                "active_incidents": open_count,
                "critical_incidents": critical_count,
                "dependencies": s.dependencies
            })

            for dep_id in s.dependencies:
                edges.append({
                    "from": s.id,
                    "to": dep_id,
                    "label": "depends_on"
                })

        service_map = {n["id"]: n for n in nodes}
        for n in nodes:
            if n["health"] == "OPERATIONAL":
                for dep_id in n["dependencies"]:
                    dep_node = service_map.get(dep_id)
                    if dep_node and dep_node["health"] == "CRITICAL":
                        n["health"] = "IMPACTED"
                        n["cascade_reason"] = f"Upstream dependency '{dep_node['name']}' is CRITICAL"
                        break

        return {
            "nodes": nodes,
            "edges": edges,
            "total_services": len(nodes),
            "degraded_services": len([n for n in nodes if n["health"] in ("CRITICAL", "DEGRADED", "IMPACTED")]),
            "operational_services": len([n for n in nodes if n["health"] == "OPERATIONAL"])
        }

    def delete_incident(self, incident_id: str) -> bool:
        """Deletes an incident and decrements assigned technician workload if active."""
        inc = self.incident_repo.get_by_id(incident_id)
        if not inc:
            return False

        # Release active technician workload if applicable
        if inc.assigned_technician and inc.status.value in ("ASSIGNED", "ACKNOWLEDGED", "IN_PROGRESS"):
            tech = self.user_repo.get_by_id(inc.assigned_technician.id)
            if tech and hasattr(tech, "release_ticket"):
                tech.release_ticket()
                self.user_repo.save(tech)

        return self.incident_repo.delete(incident_id)

    def batch_delete_incidents(self, incident_ids: List[str]) -> Dict[str, Any]:
        """Deletes multiple incidents by ID."""
        deleted = []
        for inc_id in incident_ids:
            if self.delete_incident(inc_id):
                deleted.append(inc_id)
        return {"deleted_count": len(deleted), "deleted_ids": deleted}

    def cleanup_duplicates(self) -> Dict[str, Any]:
        """
        Cleans up redundant duplicate incidents in the system.
        Keeps one primary ticket per group of duplicates and deletes the redundant copies.
        """
        all_incidents = self.incident_repo.get_all()
        to_delete = set()

        # 1. Any explicitly marked duplicate whose duplicate_of_id or parent_incident_id exists
        for inc in all_incidents:
            if inc.is_duplicate and inc.duplicate_of_id:
                to_delete.add(inc.id)
            elif inc.parent_incident_id and inc.id != inc.parent_incident_id:
                to_delete.add(inc.id)

        # 2. Correlated identical title + service duplicates
        from collections import defaultdict
        groups = defaultdict(list)
        for inc in all_incidents:
            if inc.id not in to_delete:
                norm_title = (inc.title or "").strip().lower()
                srv_id = inc.service.id if inc.service else ""
                groups[(norm_title, srv_id)].append(inc)

        status_ranks = {
            "CLOSED": 6, "VERIFIED": 5, "RESOLVED": 4,
            "IN_PROGRESS": 3, "ACKNOWLEDGED": 2, "ASSIGNED": 1, "NEW": 0
        }
        for (norm_title, srv_id), inc_list in groups.items():
            if len(inc_list) > 1:
                # Sort best candidate first (highest progression, then earliest created)
                inc_list.sort(
                    key=lambda x: (
                        status_ranks.get(x.status.value if hasattr(x.status, "value") else str(x.status), 0),
                        -x.created_at.timestamp() if x.created_at else 0
                    ),
                    reverse=True
                )
                # Keep inc_list[0], delete remaining copies
                for dup in inc_list[1:]:
                    to_delete.add(dup.id)

        deleted = []
        for inc_id in to_delete:
            if self.delete_incident(inc_id):
                deleted.append(inc_id)

        return {"cleaned_count": len(deleted), "deleted_ids": deleted}

