from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.user import User, Technician
from backend.app.domain.models.service import ITService


class IIncidentRepository(ABC):
    """Repository Pattern interface for Incident persistence."""

    @abstractmethod
    def save(self, incident: Incident) -> Incident:
        pass

    @abstractmethod
    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class IUserRepository(ABC):
    """Repository Pattern interface for User & Technician persistence."""

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_technicians(self, available_only: bool = False) -> List[Technician]:
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass


class IServiceRepository(ABC):
    """Repository Pattern interface for IT Services."""

    @abstractmethod
    def save(self, service: ITService) -> ITService:
        pass

    @abstractmethod
    def get_by_id(self, service_id: str) -> Optional[ITService]:
        pass

    @abstractmethod
    def get_all(self) -> List[ITService]:
        pass
