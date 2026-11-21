class DomainException(Exception):
    """Base exception for all domain-level business rule violations."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# 1. Invalid login
class InvalidLoginException(DomainException):
    """Raised when authentication fails due to invalid credentials, incorrect password, or inactive account."""
    pass


# 2. Unauthorized operation
class UnauthorizedActionException(DomainException):
    """Raised when a user attempts an operation their role does not permit."""
    pass

UnauthorizedOperationException = UnauthorizedActionException


class EntityNotFoundException(DomainException):
    """Raised when a requested entity (User, Incident, Service) cannot be found."""
    pass


# 3. Invalid incident
class InvalidIncidentException(EntityNotFoundException):
    """Raised when an incident is malformed, has invalid parameters, or cannot be found."""
    pass


# 4. Invalid state transition
class InvalidStateTransitionException(DomainException):
    """Raised when an incident is commanded to transition into an invalid lifecycle state."""
    def __init__(self, from_state: str, to_state: str, reason: str = ""):
        msg = f"Invalid state transition from '{from_state}' to '{to_state}'."
        if reason:
            msg += f" Reason: {reason}"
        super().__init__(msg)
        self.from_state = from_state
        self.to_state = to_state


# 5. Technician unavailable
class TechnicianUnavailableException(DomainException):
    """Raised when an assigned technician is off-duty, offline, or unavailable."""
    pass


# 6. Workload exceeded
class WorkloadExceededException(DomainException):
    """Raised when a technician is at maximum concurrent active ticket capacity."""
    pass

TechnicianCapacityExceededException = WorkloadExceededException


# 7. Service not found
class ServiceNotFoundException(EntityNotFoundException):
    """Raised when a requested IT service does not exist in the service catalog."""
    pass


# 8. Missing SLA config
class MissingSLAConfigException(DomainException):
    """Raised when an IT service or priority tier lacks an associated SLA target policy."""
    pass


# 9. Duplicate incident
class DuplicateIncidentException(DomainException):
    """Raised when a duplicate incident report is detected."""
    pass


# 10. Database failure
class DatabaseFailureException(DomainException):
    """Raised when a database connection or query execution failure occurs."""
    pass


# 11. Network failure
class NetworkFailureException(DomainException):
    """Raised when an external network service (e.g. SMTP or API) fails to connect."""
    pass


# 12. Invalid user input
class InvalidUserInputException(DomainException):
    """Raised when user input fails structural, length, or boundary validation rules."""
    pass


# Additional security & lifecycle exceptions
class SLABreachException(DomainException):
    """Raised when an SLA response or resolution deadline has expired."""
    pass


class WeakPasswordException(DomainException):
    """Raised when a password fails the enterprise security strength policy."""
    pass


class InvalidVerificationCodeException(DomainException):
    """Raised when an email verification code is invalid, mismatched, or expired."""
    pass
