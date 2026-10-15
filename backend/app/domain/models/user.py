from typing import List, Optional
import uuid
from backend.app.domain.models.enums import UserRole
from backend.app.domain.exceptions import TechnicianCapacityExceededException, TechnicianUnavailableException


class User:
    """Base User entity demonstrating OOP Encapsulation and Inheritance."""
    def __init__(
        self,
        email: str,
        full_name: str,
        role: UserRole,
        user_id: Optional[str] = None,
        hashed_password: str = "",
        is_active: bool = True
    ):
        self._id = user_id or str(uuid.uuid4())
        self._email = email
        self._full_name = full_name
        self._role = role
        self._hashed_password = hashed_password
        self._is_active = is_active

    @property
    def id(self) -> str:
        return self._id

    @property
    def email(self) -> str:
        return self._email

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def hashed_password(self) -> str:
        return self._hashed_password

    def has_role(self, required_role: UserRole) -> bool:
        return self._role == required_role

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id} name={self._full_name} role={self._role.value}>"


class Employee(User):
    """Employee/Customer role who reports incidents and verifies resolutions."""
    def __init__(
        self,
        email: str,
        full_name: str,
        department: str = "General",
        user_id: Optional[str] = None,
        hashed_password: str = "",
        is_active: bool = True
    ):
        super().__init__(email, full_name, UserRole.EMPLOYEE, user_id, hashed_password, is_active)
        self.department = department


class Technician(User):
    """Technician/Support Engineer role with skills, availability, and active workload."""
    def __init__(
        self,
        email: str,
        full_name: str,
        skills: Optional[List[str]] = None,
        max_active_load: int = 5,
        current_active_load: int = 0,
        is_available: bool = True,
        experience_years: float = 2.0,
        performance_rating: float = 4.5,
        user_id: Optional[str] = None,
        hashed_password: str = "",
        is_active: bool = True
    ):
        super().__init__(email, full_name, UserRole.TECHNICIAN, user_id, hashed_password, is_active)
        self.skills: List[str] = [s.lower() for s in (skills or [])]
        self.max_active_load = max_active_load
        self.current_active_load = current_active_load
        self.is_available = is_available
        self.experience_years = experience_years
        self.performance_rating = performance_rating

    def can_accept_workload(self) -> bool:
        return self.is_available and (self.current_active_load < self.max_active_load)

    def allocate_ticket(self) -> None:
        if not self.is_available:
            raise TechnicianUnavailableException(f"Technician {self.full_name} is currently unavailable.")
        if self.current_active_load >= self.max_active_load:
            raise TechnicianCapacityExceededException(
                f"Technician {self.full_name} has reached maximum workload limit ({self.max_active_load})."
            )
        self.current_active_load += 1

    def release_ticket(self) -> None:
        if self.current_active_load > 0:
            self.current_active_load -= 1

    def has_skill(self, required_skill: str) -> bool:
        return required_skill.lower() in self.skills


class Administrator(User):
    """Administrator/IT Manager with system governance capabilities."""
    def __init__(
        self,
        email: str,
        full_name: str,
        user_id: Optional[str] = None,
        hashed_password: str = "",
        is_active: bool = True
    ):
        super().__init__(email, full_name, UserRole.ADMIN, user_id, hashed_password, is_active)
