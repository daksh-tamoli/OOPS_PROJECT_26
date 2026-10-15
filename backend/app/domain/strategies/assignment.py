from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.domain.models.user import Technician
from backend.app.domain.models.incident import Incident
from backend.app.domain.exceptions import TechnicianUnavailableException


class IAssignmentStrategy(ABC):
    """Abstract Strategy interface for Technician Assignment."""

    @abstractmethod
    def select_technician(self, incident: Incident, available_technicians: List[Technician]) -> Technician:
        """Selects the most suitable technician for the incident according to the strategy."""
        pass


class SkillBasedAssignment(IAssignmentStrategy):
    """
    Selects the technician who possesses required skills matching the incident category/tags.
    Breaks ties using higher performance rating or lower load.
    """
    def select_technician(self, incident: Incident, available_technicians: List[Technician]) -> Technician:
        eligible = [t for t in available_technicians if t.can_accept_workload()]
        if not eligible:
            raise TechnicianUnavailableException("No technicians currently available with capacity.")

        required_skill = incident.category.lower()
        skilled = [t for t in eligible if t.has_skill(required_skill)]

        candidates = skilled if skilled else eligible
        # Sort by performance rating desc, current load asc
        candidates.sort(key=lambda t: (-t.performance_rating, t.current_active_load))
        return candidates[0]


class LeastLoadedAssignment(IAssignmentStrategy):
    """
    Selects the technician with the lowest active ticket count to ensure balanced workload distribution.
    """
    def select_technician(self, incident: Incident, available_technicians: List[Technician]) -> Technician:
        eligible = [t for t in available_technicians if t.can_accept_workload()]
        if not eligible:
            raise TechnicianUnavailableException("No technicians available with capacity.")

        # Sort by current active load ascending
        eligible.sort(key=lambda t: (t.current_active_load, -t.performance_rating))
        return eligible[0]


class RoundRobinAssignment(IAssignmentStrategy):
    """
    Distributes incidents evenly in sequential round-robin order.
    """
    def __init__(self):
        self._index = 0

    def select_technician(self, incident: Incident, available_technicians: List[Technician]) -> Technician:
        eligible = [t for t in available_technicians if t.can_accept_workload()]
        if not eligible:
            raise TechnicianUnavailableException("No technicians available with capacity.")

        selected = eligible[self._index % len(eligible)]
        self._index += 1
        return selected


class CompositeSmartAssignment(IAssignmentStrategy):
    """
    Advanced composite scoring strategy combining:
    - Skill match: 40%
    - Workload availability: 30%
    - Experience / Rating: 30%
    """
    def select_technician(self, incident: Incident, available_technicians: List[Technician]) -> Technician:
        eligible = [t for t in available_technicians if t.can_accept_workload()]
        if not eligible:
            raise TechnicianUnavailableException("No technicians available with capacity.")

        category = incident.category.lower()

        def compute_score(tech: Technician) -> float:
            skill_score = 10.0 if tech.has_skill(category) else 2.0
            load_factor = (tech.max_active_load - tech.current_active_load) / tech.max_active_load * 10.0
            rating_score = tech.performance_rating * 2.0  # Scale 0-5 to 0-10
            return (0.40 * skill_score) + (0.30 * load_factor) + (0.30 * rating_score)

        eligible.sort(key=compute_score, reverse=True)
        return eligible[0]
