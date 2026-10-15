from typing import List, Optional, Dict
from backend.app.domain.repositories.interfaces import IIncidentRepository, IUserRepository, IServiceRepository
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.user import User, Technician
from backend.app.domain.models.service import ITService


class InMemoryIncidentRepository(IIncidentRepository):
    """In-memory implementation of IIncidentRepository for fast testing and local prototyping."""
    def __init__(self):
        self._storage: Dict[str, Incident] = {}

    def save(self, incident: Incident) -> Incident:
        self._storage[incident.id] = incident
        return incident

    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        return self._storage.get(incident_id)

    def get_all(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        service_id: Optional[str] = None,
        technician_id: Optional[str] = None,
        search_query: Optional[str] = None,
        is_sla_breached: Optional[bool] = None
    ) -> List[Incident]:
        results = list(self._storage.values())

        if status:
            results = [inc for inc in results if inc.status.value.lower() == status.lower()]
        if priority:
            results = [inc for inc in results if inc.priority.value.lower() == priority.lower()]
        if category:
            results = [inc for inc in results if inc.category.lower() == category.lower()]
        if service_id:
            results = [inc for inc in results if inc.service.id == service_id]
        if technician_id:
            results = [inc for inc in results if inc.assigned_technician and inc.assigned_technician.id == technician_id]
        if is_sla_breached is not None:
            results = [inc for inc in results if inc.sla_tracker.check_breach() == is_sla_breached]
        if search_query:
            q = search_query.lower()
            results = [inc for inc in results if q in inc.title.lower() or q in inc.description.lower() or q in inc.id.lower()]

        # Sort newest first
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results

    def count(self) -> int:
        return len(self._storage)


class InMemoryUserRepository(IUserRepository):
    """In-memory user and technician repository."""
    def __init__(self):
        self._storage: Dict[str, User] = {}

    def save(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._storage.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        for u in self._storage.values():
            if u.email.lower() == email.lower():
                return u
        return None

    def get_technicians(self, available_only: bool = False) -> List[Technician]:
        techs = [u for u in self._storage.values() if isinstance(u, Technician)]
        if available_only:
            techs = [t for t in techs if t.can_accept_workload()]
        return techs

    def get_all(self) -> List[User]:
        return list(self._storage.values())


class InMemoryServiceRepository(IServiceRepository):
    """In-memory service repository."""
    def __init__(self):
        self._storage: Dict[str, ITService] = {}

    def save(self, service: ITService) -> ITService:
        self._storage[service.id] = service
        return service

    def get_by_id(self, service_id: str) -> Optional[ITService]:
        return self._storage.get(service_id)

    def get_all(self) -> List[ITService]:
        return list(self._storage.values())
