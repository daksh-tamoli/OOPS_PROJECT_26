import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from backend.app.domain.repositories.interfaces import (
    IIncidentRepository, IUserRepository, IServiceRepository
)
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.user import User, Employee, Technician, Administrator
from backend.app.domain.models.service import ITService
from backend.app.domain.models.sla import SLAPolicy, SLATarget, SLAStatusTracker
from backend.app.domain.models.audit import AuditRecord
from backend.app.domain.models.enums import (
    UserRole, IncidentStatus, Priority, Impact, Urgency, ServiceTier
)
from backend.app.domain.states.incident_state import (
    NewState, ClassifiedState, AssignedState, AcknowledgedState,
    InProgressState, ResolvedState, VerifiedState, ClosedState, IncidentState
)

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    email = Column(String(128), unique=True, nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False)
    department = Column(String(128), nullable=True)
    skills = Column(Text, nullable=True)  # JSON serialized list
    max_active_load = Column(Integer, default=5)
    current_active_load = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    experience_years = Column(Float, default=2.0)
    performance_rating = Column(Float, default=4.5)
    is_active = Column(Boolean, default=True)


class ServiceModel(Base):
    __tablename__ = "services"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    tier = Column(String(32), default=ServiceTier.TIER_2.value)
    is_active = Column(Boolean, default=True)


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    service_id = Column(String(64), ForeignKey("services.id"), nullable=False)
    reporter_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    assigned_technician_id = Column(String(64), ForeignKey("users.id"), nullable=True)
    impact = Column(String(32), default=Impact.MEDIUM.value)
    urgency = Column(String(32), default=Urgency.MEDIUM.value)
    priority = Column(String(32), default=Priority.P3.value)
    current_state = Column(String(32), default=IncidentStatus.NEW.value)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # SLA tracker fields
    response_deadline = Column(DateTime, nullable=True)
    resolution_deadline = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    is_breached = Column(Boolean, default=False)

    # Resolution & investigation details
    investigation_notes = Column(Text, nullable=True)  # JSON serialized list
    resolution_details = Column(Text, nullable=True)
    resolution_feedback = Column(Text, nullable=True)

    # Duplicate / Correlation
    parent_incident_id = Column(String(64), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(String(64), nullable=True)


class AuditModel(Base):
    __tablename__ = "audit_records"

    id = Column(String(64), primary_key=True)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False)
    actor_id = Column(String(64), nullable=False)
    actor_name = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)
    previous_state = Column(String(32), nullable=False)
    new_state = Column(String(32), nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# State resolution mapping helper
STATE_FACTORY_MAP = {
    IncidentStatus.NEW.value: NewState,
    IncidentStatus.CLASSIFIED.value: ClassifiedState,
    IncidentStatus.ASSIGNED.value: AssignedState,
    IncidentStatus.ACKNOWLEDGED.value: AcknowledgedState,
    IncidentStatus.IN_PROGRESS.value: InProgressState,
    IncidentStatus.RESOLVED.value: ResolvedState,
    IncidentStatus.VERIFIED.value: VerifiedState,
    IncidentStatus.CLOSED.value: ClosedState,
}


class SqliteIncidentRepository(IIncidentRepository):
    """Persistent SQLite implementation of IIncidentRepository using SQLAlchemy."""

    def __init__(self, session_factory, user_repo: IUserRepository, service_repo: IServiceRepository):
        self.session_factory = session_factory
        self.user_repo = user_repo
        self.service_repo = service_repo

    def save(self, incident: Incident) -> Incident:
        with self.session_factory() as session:
            model = session.query(IncidentModel).filter_by(id=incident.id).first()
            if not model:
                model = IncidentModel(id=incident.id)
                session.add(model)

            model.title = incident.title
            model.description = incident.description
            model.category = incident.category
            model.service_id = incident.service.id
            model.reporter_id = incident.reporter.id
            model.assigned_technician_id = incident.assigned_technician.id if incident.assigned_technician else None
            model.impact = incident.impact.value if hasattr(incident.impact, "value") else incident.impact
            model.urgency = incident.urgency.value if hasattr(incident.urgency, "value") else incident.urgency
            model.priority = incident.priority.value if hasattr(incident.priority, "value") else incident.priority
            model.current_state = incident.status.value
            model.created_at = incident.created_at

            # SLA
            model.response_deadline = incident.sla_tracker.response_deadline
            model.resolution_deadline = incident.sla_tracker.resolution_deadline
            model.responded_at = incident.sla_tracker.responded_at
            model.resolved_at = incident.sla_tracker.resolved_at
            model.is_breached = incident.sla_tracker.check_breach()

            # Notes
            model.investigation_notes = json.dumps(incident.investigation_notes)
            model.resolution_details = incident.resolution_details
            model.resolution_feedback = incident.resolution_feedback

            # Duplicates
            model.parent_incident_id = incident.parent_incident_id
            model.is_duplicate = incident.is_duplicate
            model.duplicate_of_id = incident.duplicate_of_id

            # Persist any new audit logs
            existing_audit_ids = {a.id for a in session.query(AuditModel.id).filter_by(incident_id=incident.id).all()}
            for audit in incident.audit_logs:
                if audit.id not in existing_audit_ids:
                    session.add(AuditModel(
                        id=audit.id,
                        incident_id=incident.id,
                        actor_id=audit.actor_id,
                        actor_name=audit.actor_name,
                        action=audit.action,
                        previous_state=audit.previous_state,
                        new_state=audit.new_state,
                        description=audit.description,
                        timestamp=audit.timestamp
                    ))

            session.commit()
            return incident

    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        with self.session_factory() as session:
            model = session.query(IncidentModel).filter_by(id=incident_id).first()
            if not model:
                return None
            return self._to_domain(model, session)

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
        with self.session_factory() as session:
            query = session.query(IncidentModel)

            if status and status.upper() != "ALL":
                query = query.filter(IncidentModel.current_state == status.upper())
            if priority and priority.upper() != "ALL":
                query = query.filter(IncidentModel.priority == priority.upper())
            if category:
                query = query.filter(IncidentModel.category.ilike(f"%{category}%"))
            if service_id:
                query = query.filter(IncidentModel.service_id == service_id)
            if technician_id:
                query = query.filter(IncidentModel.assigned_technician_id == technician_id)
            if is_sla_breached is not None:
                query = query.filter(IncidentModel.is_breached == is_sla_breached)
            if search_query:
                q = f"%{search_query.lower()}%"
                query = query.filter(
                    (IncidentModel.title.ilike(q)) |
                    (IncidentModel.description.ilike(q)) |
                    (IncidentModel.id.ilike(q))
                )

            query = query.order_by(IncidentModel.created_at.desc())
            models = query.all()
            return [self._to_domain(m, session) for m in models]

    def count(self) -> int:
        with self.session_factory() as session:
            return session.query(IncidentModel).count()

    def _to_domain(self, model: IncidentModel, session) -> Incident:
        service = self.service_repo.get_by_id(model.service_id)
        reporter = self.user_repo.get_by_id(model.reporter_id)

        target = service.sla_policy.get_target(Priority(model.priority))
        inc = Incident(
            title=model.title,
            description=model.description,
            service=service,
            reporter=reporter,
            impact=Impact(model.impact),
            urgency=Urgency(model.urgency),
            priority=Priority(model.priority),
            category=model.category,
            incident_id=model.id,
            created_at=model.created_at,
            sla_target=target
        )

        # Rehydrate State Pattern State
        state_cls = STATE_FACTORY_MAP.get(model.current_state, NewState)
        inc._state = state_cls()

        if model.assigned_technician_id:
            tech = self.user_repo.get_by_id(model.assigned_technician_id)
            if isinstance(tech, Technician):
                inc.assigned_technician = tech

        # Rehydrate SLA Tracker
        inc.sla_tracker.response_deadline = model.response_deadline
        inc.sla_tracker.resolution_deadline = model.resolution_deadline
        inc.sla_tracker.responded_at = model.responded_at
        inc.sla_tracker.resolved_at = model.resolved_at
        inc.sla_tracker.is_breached = model.is_breached

        # Rehydrate Notes & Feedback
        inc.investigation_notes = json.loads(model.investigation_notes) if model.investigation_notes else []
        inc.resolution_details = model.resolution_details or ""
        inc.resolution_feedback = model.resolution_feedback or ""
        inc.parent_incident_id = model.parent_incident_id
        inc.is_duplicate = model.is_duplicate
        inc.duplicate_of_id = model.duplicate_of_id

        # Rehydrate Audit Logs
        audit_models = session.query(AuditModel).filter_by(incident_id=model.id).order_by(AuditModel.timestamp.asc()).all()
        inc.audit_logs = [
            AuditRecord(
                incident_id=a.incident_id,
                actor_id=a.actor_id,
                actor_name=a.actor_name,
                action=a.action,
                previous_state=a.previous_state,
                new_state=a.new_state,
                description=a.description,
                record_id=a.id,
                timestamp=a.timestamp
            )
            for a in audit_models
        ]
        return inc


class SqliteUserRepository(IUserRepository):
    """Persistent SQLite user repository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save(self, user: User) -> User:
        with self.session_factory() as session:
            model = session.query(UserModel).filter_by(id=user.id).first()
            if not model:
                model = UserModel(id=user.id)
                session.add(model)

            model.email = user.email
            model.full_name = user.full_name
            model.role = user.role.value
            model.is_active = user.is_active

            if isinstance(user, Employee):
                model.department = user.department
            elif isinstance(user, Technician):
                model.skills = json.dumps(user.skills)
                model.max_active_load = user.max_active_load
                model.current_active_load = user.current_active_load
                model.is_available = user.is_available
                model.experience_years = user.experience_years
                model.performance_rating = user.performance_rating

            session.commit()
            return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self.session_factory() as session:
            model = session.query(UserModel).filter_by(id=user_id).first()
            if not model:
                return None
            return self._to_domain(model)

    def get_by_email(self, email: str) -> Optional[User]:
        with self.session_factory() as session:
            model = session.query(UserModel).filter(UserModel.email.ilike(email)).first()
            if not model:
                return None
            return self._to_domain(model)

    def get_technicians(self, available_only: bool = False) -> List[Technician]:
        with self.session_factory() as session:
            query = session.query(UserModel).filter_by(role=UserRole.TECHNICIAN.value)
            if available_only:
                query = query.filter(UserModel.is_available == True)
            models = query.all()
            techs = [self._to_domain(m) for m in models]
            if available_only:
                techs = [t for t in techs if t.can_accept_workload()]
            return techs

    def get_all(self) -> List[User]:
        with self.session_factory() as session:
            models = session.query(UserModel).all()
            return [self._to_domain(m) for m in models]

    def _to_domain(self, model: UserModel) -> User:
        role = UserRole(model.role)
        if role == UserRole.TECHNICIAN:
            skills = json.loads(model.skills) if model.skills else []
            return Technician(
                email=model.email,
                full_name=model.full_name,
                skills=skills,
                max_active_load=model.max_active_load,
                current_active_load=model.current_active_load,
                is_available=model.is_available,
                experience_years=model.experience_years,
                performance_rating=model.performance_rating,
                user_id=model.id,
                is_active=model.is_active
            )
        elif role == UserRole.ADMIN:
            return Administrator(
                email=model.email,
                full_name=model.full_name,
                user_id=model.id,
                is_active=model.is_active
            )
        else:
            return Employee(
                email=model.email,
                full_name=model.full_name,
                department=model.department or "General",
                user_id=model.id,
                is_active=model.is_active
            )


class SqliteServiceRepository(IServiceRepository):
    """Persistent SQLite IT Service repository."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save(self, service: ITService) -> ITService:
        with self.session_factory() as session:
            model = session.query(ServiceModel).filter_by(id=service.id).first()
            if not model:
                model = ServiceModel(id=service.id)
                session.add(model)

            model.name = service.name
            model.description = service.description
            model.tier = service.tier.value if hasattr(service.tier, "value") else service.tier
            model.is_active = service.is_active
            session.commit()
            return service

    def get_by_id(self, service_id: str) -> Optional[ITService]:
        with self.session_factory() as session:
            model = session.query(ServiceModel).filter_by(id=service_id).first()
            if not model:
                return None
            return ITService(
                name=model.name,
                description=model.description,
                tier=ServiceTier(model.tier),
                service_id=model.id,
                is_active=model.is_active
            )

    def get_all(self) -> List[ITService]:
        with self.session_factory() as session:
            models = session.query(ServiceModel).filter_by(is_active=True).all()
            return [
                ITService(
                    name=m.name,
                    description=m.description,
                    tier=ServiceTier(m.tier),
                    service_id=m.id,
                    is_active=m.is_active
                )
                for m in models
            ]


def init_sqlite_db(db_path: str = "sqlite:///backend/itsm.db"):
    """Initializes SQLite database and tables."""
    engine = create_engine(db_path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory
