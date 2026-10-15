from typing import Optional
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.user import User
from backend.app.domain.models.service import ITService
from backend.app.domain.models.enums import Impact, Urgency, Priority
from backend.app.domain.strategies.priority import IPriorityStrategy, MatrixPriorityStrategy
from backend.app.domain.intelligence.categorizer import IntelligentCategorizer


class IncidentFactory:
    """
    Factory Pattern for constructing Incident aggregates with consistent initialization,
    automatic priority calculation, and category inference.
    """
    def __init__(
        self,
        priority_strategy: Optional[IPriorityStrategy] = None,
        categorizer: Optional[IntelligentCategorizer] = None
    ):
        self.priority_strategy = priority_strategy or MatrixPriorityStrategy()
        self.categorizer = categorizer or IntelligentCategorizer()

    def create_incident(
        self,
        title: str,
        description: str,
        service: ITService,
        reporter: User,
        impact: Impact = Impact.MEDIUM,
        urgency: Urgency = Urgency.MEDIUM,
        category: Optional[str] = None,
        explicit_priority: Optional[Priority] = None
    ) -> Incident:
        # Inferred category if none supplied
        resolved_category = category or self.categorizer.suggest_category(title, description).value

        # Calculate priority using strategy if not manually overridden
        resolved_priority = explicit_priority or self.priority_strategy.calculate_priority(impact, urgency, service)

        # Obtain SLA target from service policy
        sla_target = service.sla_policy.get_target(resolved_priority)

        incident = Incident(
            title=title,
            description=description,
            service=service,
            reporter=reporter,
            impact=impact,
            urgency=urgency,
            priority=resolved_priority,
            category=resolved_category,
            sla_target=sla_target
        )
        return incident
