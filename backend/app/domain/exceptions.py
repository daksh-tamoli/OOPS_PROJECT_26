class DomainException(Exception):
    """Base exception for all domain-level business rule violations."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidStateTransitionException(DomainException):
    """Raised when an incident is commanded to transition into an invalid lifecycle state."""
    def __init__(self, from_state: str, to_state: str, reason: str = ""):
        msg = f"Invalid state transition from '{from_state}' to '{to_state}'."
        if reason:
            msg += f" Reason: {reason}"
        super().__init__(msg)
        self.from_state = from_state
        self.to_state = to_state


class UnauthorizedActionException(DomainException):
    """Raised when a user attempts an operation their role does not permit."""
    pass


class TechnicianUnavailableException(DomainException):
    """Raised when an assigned technician is off-duty or unavailable."""
    pass


class TechnicianCapacityExceededException(DomainException):
    """Raised when a technician is at maximum concurrent active ticket capacity."""
    pass


class SLABreachException(DomainException):
    """Raised when an SLA response or resolution deadline has expired."""
    pass


class EntityNotFoundException(DomainException):
    """Raised when a requested entity cannot be found."""
    pass


class DuplicateIncidentException(DomainException):
    """Raised when a duplicate incident report is detected."""
    pass
