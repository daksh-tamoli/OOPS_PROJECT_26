import os
import asyncio
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.domain.models.enums import UserRole, IncidentStatus, Priority, Impact, Urgency, ServiceTier
from backend.app.domain.models.user import Employee, Technician, Administrator, User
from backend.app.domain.models.service import ITService
from backend.app.domain.models.sla import SLAStatusTracker, SLAPolicy, SLATarget
from backend.app.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    ServiceNotFoundException,
    InvalidIncidentException,
    InvalidStateTransitionException,
    InvalidLoginException,
    UnauthorizedActionException,
    TechnicianUnavailableException,
    WorkloadExceededException,
    MissingSLAConfigException,
    DuplicateIncidentException,
    DatabaseFailureException,
    NetworkFailureException,
    InvalidUserInputException
)
from backend.app.infrastructure.persistence.in_memory_repo import (
    InMemoryIncidentRepository, InMemoryUserRepository, InMemoryServiceRepository
)
from backend.app.services.incident_service import IncidentService


# Initialize FastAPI App
app = FastAPI(
    title="Intelligent IT Service Management (I-ITSM) API",
    description="CS F213/MAC F212 OOP Project - REST API Layer",
    version="1.0.0"
)

from fastapi.responses import JSONResponse

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Domain Exception Handlers (Mapping All 12 Custom Exceptions to Clean HTTP Responses)
# ==============================================================================

@app.exception_handler(InvalidLoginException)
def invalid_login_handler(request, exc: InvalidLoginException):
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message, "error_type": "InvalidLoginException"}
    )

@app.exception_handler(UnauthorizedActionException)
def unauthorized_action_handler(request, exc: UnauthorizedActionException):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message, "error_type": "UnauthorizedActionException"}
    )

@app.exception_handler(ServiceNotFoundException)
def service_not_found_handler(request, exc: ServiceNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "error_type": "ServiceNotFoundException"}
    )

@app.exception_handler(InvalidIncidentException)
def invalid_incident_handler(request, exc: InvalidIncidentException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "error_type": "InvalidIncidentException"}
    )

@app.exception_handler(EntityNotFoundException)
def entity_not_found_handler(request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "error_type": exc.__class__.__name__}
    )

@app.exception_handler(InvalidStateTransitionException)
def invalid_state_transition_handler(request, exc: InvalidStateTransitionException):
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "error_type": "InvalidStateTransitionException",
            "from_state": getattr(exc, "from_state", ""),
            "to_state": getattr(exc, "to_state", "")
        }
    )

@app.exception_handler(TechnicianUnavailableException)
def tech_unavailable_handler(request, exc: TechnicianUnavailableException):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "error_type": "TechnicianUnavailableException"}
    )

@app.exception_handler(WorkloadExceededException)
def workload_exceeded_handler(request, exc: WorkloadExceededException):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "error_type": "WorkloadExceededException"}
    )

@app.exception_handler(DuplicateIncidentException)
def duplicate_incident_handler(request, exc: DuplicateIncidentException):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "error_type": "DuplicateIncidentException"}
    )

@app.exception_handler(MissingSLAConfigException)
def missing_sla_config_handler(request, exc: MissingSLAConfigException):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message, "error_type": "MissingSLAConfigException"}
    )

@app.exception_handler(InvalidUserInputException)
def invalid_user_input_handler(request, exc: InvalidUserInputException):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message, "error_type": "InvalidUserInputException"}
    )

@app.exception_handler(DatabaseFailureException)
def database_failure_handler(request, exc: DatabaseFailureException):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message, "error_type": "DatabaseFailureException"}
    )

@app.exception_handler(NetworkFailureException)
def network_failure_handler(request, exc: NetworkFailureException):
    return JSONResponse(
        status_code=502,
        content={"detail": exc.message, "error_type": "NetworkFailureException"}
    )

@app.exception_handler(DomainException)
def domain_exception_handler(request, exc: DomainException):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_type": exc.__class__.__name__}
    )

# Repositories & Services with SQLite Persistent Storage (Repository Pattern)
from backend.app.infrastructure.persistence.sqlite_repo import (
    init_sqlite_db, SqliteUserRepository, SqliteServiceRepository, SqliteIncidentRepository
)

session_factory = init_sqlite_db("sqlite:///backend/itsm.db")
user_repo = SqliteUserRepository(session_factory)
service_repo = SqliteServiceRepository(session_factory)
incident_repo = SqliteIncidentRepository(session_factory, user_repo, service_repo)
incident_service = IncidentService(incident_repo, user_repo, service_repo)


# ==============================================================================
# Seed Initial Data (IT Services, Technicians, Employees, Admin)
# ==============================================================================
def seed_data():
    # 1. Services
    srv_payment = ITService(
        service_id="srv-payment",
        name="Payment Gateway",
        description="Processes credit cards, UPI, and banking transactions",
        tier=ServiceTier.TIER_1_CRITICAL,
        dependencies=["srv-db", "srv-auth"]
    )
    srv_auth = ITService(
        service_id="srv-auth",
        name="Single Sign-On (SSO)",
        description="Central authentication and LDAP service",
        tier=ServiceTier.TIER_1_CRITICAL,
        dependencies=["srv-db"]
    )
    srv_db = ITService(
        service_id="srv-db",
        name="Core PostgreSQL DB",
        description="Primary organizational relational database clusters",
        tier=ServiceTier.TIER_1_CRITICAL,
        dependencies=[]
    )
    srv_cloud = ITService(
        service_id="srv-cloud",
        name="Cloud Storage & CDN",
        description="S3 buckets and media delivery assets",
        tier=ServiceTier.TIER_2,
        dependencies=["srv-auth"]
    )
    srv_email = ITService(
        service_id="srv-email",
        name="Internal Mail Exchange",
        description="Corporate messaging and communication",
        tier=ServiceTier.TIER_3,
        dependencies=["srv-cloud"]
    )

    for s in [srv_payment, srv_auth, srv_db, srv_cloud, srv_email]:
        service_repo.save(s)


    # 2. Users (all seeded with password: password123)
    default_hash = User.hash_password("password123")
    admin = Administrator(
        user_id="user-admin-1",
        email="admin@itsm.local",
        full_name="Sarah Connor (IT Manager)",
        hashed_password=default_hash
    )
    emp1 = Employee(
        user_id="user-emp-1",
        email="alice@company.com",
        full_name="Alice Smith (Finance)",
        department="Finance",
        hashed_password=default_hash
    )
    emp2 = Employee(
        user_id="user-emp-2",
        email="john@company.com",
        full_name="John Doe (Engineering)",
        department="Engineering",
        hashed_password=default_hash
    )

    # Technicians with specialized skills & loads
    tech1 = Technician(
        user_id="tech-101",
        email="devon@itsm.local",
        full_name="Devon Vance (DB Specialist)",
        skills=["database", "sql", "storage"],
        max_active_load=4,
        current_active_load=0,
        experience_years=5.0,
        performance_rating=4.9,
        hashed_password=default_hash
    )
    tech2 = Technician(
        user_id="tech-102",
        email="maya@itsm.local",
        full_name="Maya Lin (Network & Cloud)",
        skills=["network", "cloud", "security"],
        max_active_load=5,
        current_active_load=0,
        experience_years=4.0,
        performance_rating=4.7,
        hashed_password=default_hash
    )
    tech3 = Technician(
        user_id="tech-103",
        email="liam@itsm.local",
        full_name="Liam Gallagher (App & Auth)",
        skills=["application", "authentication", "software"],
        max_active_load=3,
        current_active_load=0,
        experience_years=3.2,
        performance_rating=4.5,
        hashed_password=default_hash
    )

    for u in [admin, emp1, emp2, tech1, tech2, tech3]:
        user_repo.save(u)


seed_data()


# ==============================================================================
# Pydantic Request / Response Schemas
# ==============================================================================
class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    full_name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=4)
    department: str = "General"
    role: str = "EMPLOYEE"


class SendVerificationRequest(BaseModel):
    email: str = Field(..., min_length=3)
    full_name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=4)
    department: str = "General"
    role: str = "EMPLOYEE"


class VerifyRegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    code: str = Field(..., min_length=4, max_length=10)


class ResendCodeRequest(BaseModel):
    email: str = Field(..., min_length=3)


# In-memory storage for pending email verifications {email: {code, expires_at, full_name, hashed_password, department, role}}
pending_verifications: Dict[str, dict] = {}


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=3)
    new_password: str = Field(..., min_length=4)


class PriorityOverrideRequest(BaseModel):
    new_priority: Priority
    reason: str = Field(..., min_length=3)
    admin_id: str


class TestEmailRequest(BaseModel):
    to_email: str = Field(..., min_length=3)
    subject: str = "Test Email from I-ITSM"
    message: str = "This confirms real email notification dispatch functionality on the Enterprise I-ITSM platform."


class IncidentCreateRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=1)
    service_id: str
    reporter_id: str
    impact: Impact = Impact.MEDIUM
    urgency: Urgency = Urgency.MEDIUM
    category: Optional[str] = None
    assignment_strategy: str = "smart"
    auto_assign: bool = True


class DuplicateCheckRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    service_id: Optional[str] = None


class BatchDeleteRequest(BaseModel):
    incident_ids: List[str]


class AssignTechnicianRequest(BaseModel):
    actor_id: str
    technician_id: Optional[str] = None
    strategy: str = "skill"


class ActionNoteRequest(BaseModel):
    technician_id: str
    notes: str


class ResolveRequest(BaseModel):
    technician_id: str
    resolution_details: str


class VerifyRequest(BaseModel):
    actor_id: str
    is_confirmed: bool
    feedback: str = ""


class ServiceCreateOrUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    description: str = Field(..., min_length=5)
    tier: str = "BUSINESS_CRITICAL"
    dependencies: List[str] = []
    admin_id: Optional[str] = None


class AssignmentStrategyChangeRequest(BaseModel):
    strategy: str
    admin_id: Optional[str] = None


class SLAPolicyUpdateRequest(BaseModel):
    priority: str
    response_minutes: int
    resolution_minutes: int
    admin_id: Optional[str] = None


class CategoryCreateRequest(BaseModel):
    name: str
    keywords: List[str]
    admin_id: Optional[str] = None


class RequestInfoRequest(BaseModel):
    technician_id: str
    question: str


class AddInfoRequest(BaseModel):
    actor_id: str
    info_text: str


def format_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat()


# Serializer helper
def serialize_incident(inc) -> dict:
    return {
        "id": inc.id,
        "title": inc.title,
        "description": inc.description,
        "status": inc.status.value,
        "priority": inc.priority.value,
        "category": inc.category,
        "service": {
            "id": inc.service.id,
            "name": inc.service.name,
            "tier": inc.service.tier.value
        },
        "reporter": {
            "id": inc.reporter.id,
            "name": inc.reporter.full_name,
            "email": inc.reporter.email
        },
        "assigned_technician": {
            "id": inc.assigned_technician.id,
            "name": inc.assigned_technician.full_name,
            "email": inc.assigned_technician.email
        } if inc.assigned_technician else None,
        "created_at": format_iso_utc(inc.created_at),
        "sla": {
            "response_deadline": format_iso_utc(inc.sla_tracker.response_deadline),
            "resolution_deadline": format_iso_utc(inc.sla_tracker.resolution_deadline),
            "responded_at": format_iso_utc(inc.sla_tracker.responded_at),
            "resolved_at": format_iso_utc(inc.sla_tracker.resolved_at),
            "is_breached": inc.sla_tracker.check_breach(),
            "is_at_risk": inc.sla_tracker.is_resolution_at_risk()
        },
        "investigation_notes": inc.investigation_notes,
        "resolution_details": inc.resolution_details,
        "resolution_feedback": inc.resolution_feedback,
        "parent_incident_id": inc.parent_incident_id,
        "audit_logs": [log.to_dict() for log in inc.audit_logs]
    }


# ==============================================================================
# API Endpoints
# ==============================================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "I-ITSM Platform",
        "system_time": format_iso_utc(datetime.now(timezone.utc))
    }


# ==============================================================================
# Authentication & User Management (Page 4, 13)
# ==============================================================================

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = user_repo.get_by_email(req.email)
    if not user:
        raise InvalidLoginException("Invalid login: No account found with this corporate email address.")
    if not user.is_active:
        raise UnauthorizedActionException("Account is inactive or suspended. Contact IT administrator.")
    if not user.verify_password(req.password):
        raise InvalidLoginException("Invalid login: Incorrect password entered.")
    return {
        "status": "authenticated",
        "token": f"token-{user.id}-{uuid.uuid4().hex[:8]}",
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "role": user.role.value,
            "department": getattr(user, "department", "General"),
            "skills": getattr(user, "skills", [])
        }
    }


@app.post("/api/auth/send-verification")
def send_verification(req: SendVerificationRequest):
    norm_email = req.email.strip().lower()
    existing = user_repo.get_by_email(norm_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration Error: An account with this corporate email already exists."
        )
    # Enforce strict enterprise password strength
    is_strong, msg = User.validate_password_strength(req.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Weak Password Rejected: {msg}"
        )
    # Generate secure 6-digit OTP code
    code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    pending_verifications[norm_email] = {
        "code": code,
        "expires_at": expires_at,
        "full_name": req.full_name.strip(),
        "email": norm_email,
        "department": req.department.strip() or "General",
        "role": req.role.strip().upper(),
        "hashed_password": User.hash_password(req.password)
    }

    # Dispatch real email via SMTP service (and recorded in outbox)
    try:
        from backend.app.infrastructure.email.smtp_service import EmailService
        EmailService().send_verification_code_email(
            email=norm_email,
            code=code,
            full_name=req.full_name.strip()
        )
    except Exception as e:
        print(f"Warning: Failed to send verification email: {e}")

    return {
        "status": "code_sent",
        "message": f"6-digit verification code has been dispatched to {norm_email}.",
        "email": norm_email,
        "expires_in_minutes": 10,
        "demo_otp": code if not EmailService().smtp_configured else None
    }


@app.post("/api/auth/verify-and-register", status_code=status.HTTP_201_CREATED)
def verify_and_register(req: VerifyRegisterRequest):
    norm_email = req.email.strip().lower()
    code_entered = req.code.strip()

    entry = pending_verifications.get(norm_email)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending verification found for this email. Please request a new verification code."
        )

    if datetime.now(timezone.utc) > entry["expires_at"]:
        pending_verifications.pop(norm_email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired (valid for 10 minutes). Please request a new code."
        )

    if entry["code"] != code_entered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 6-digit verification code. Please check your email inbox and enter the correct code."
        )

    # Verification successful: pop and instantiate user
    pending_verifications.pop(norm_email, None)
    user_id = f"user-{uuid.uuid4().hex[:6]}"

    if entry["role"] == "ADMIN":
        new_user = Administrator(
            email=entry["email"],
            full_name=entry["full_name"],
            user_id=user_id,
            hashed_password=entry["hashed_password"]
        )
    elif entry["role"] == "TECHNICIAN":
        new_user = Technician(
            email=entry["email"],
            full_name=entry["full_name"],
            user_id=user_id,
            hashed_password=entry["hashed_password"]
        )
    else:
        new_user = Employee(
            email=entry["email"],
            full_name=entry["full_name"],
            department=entry["department"],
            user_id=user_id,
            hashed_password=entry["hashed_password"]
        )

    user_repo.save(new_user)

    # Dispatch Real Welcome Email
    try:
        from backend.app.infrastructure.email.smtp_service import EmailService
        EmailService().send_welcome_email(
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.value,
            department=getattr(new_user, "department", "General")
        )
    except Exception:
        pass

    return {
        "status": "authenticated",
        "token": f"token-{new_user.id}-{uuid.uuid4().hex[:8]}",
        "message": "Email verified! Account created and logged in successfully.",
        "user": {
            "id": new_user.id,
            "name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role.value,
            "department": getattr(new_user, "department", "General"),
            "skills": getattr(new_user, "skills", [])
        }
    }


@app.post("/api/auth/resend-code")
def resend_verification_code(req: ResendCodeRequest):
    norm_email = req.email.strip().lower()
    entry = pending_verifications.get(norm_email)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending registration found for this email. Please fill the registration form first."
        )
    new_code = f"{secrets.randbelow(900000) + 100000}"
    entry["code"] = new_code
    entry["expires_at"] = datetime.now(timezone.utc) + timedelta(minutes=10)

    try:
        from backend.app.infrastructure.email.smtp_service import EmailService
        EmailService().send_verification_code_email(
            email=norm_email,
            code=new_code,
            full_name=entry["full_name"]
        )
    except Exception as e:
        print(f"Warning: Failed to resend verification email: {e}")

    return {
        "status": "code_resent",
        "message": f"A new 6-digit verification code has been dispatched to {norm_email}.",
        "demo_otp": new_code if not EmailService().smtp_configured else None
    }


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    norm_email = req.email.strip().lower()
    existing = user_repo.get_by_email(norm_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration error: An account with this corporate email already exists."
        )
    # Enforce password strength policy
    is_strong, msg = User.validate_password_strength(req.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Weak Password Rejected: {msg}"
        )
    hashed = User.hash_password(req.password)
    user_id = f"user-{uuid.uuid4().hex[:6]}"

    if req.role.upper() == "ADMIN":
        new_user = Administrator(
            email=norm_email,
            full_name=req.full_name.strip(),
            user_id=user_id,
            hashed_password=hashed
        )
    elif req.role.upper() == "TECHNICIAN":
        new_user = Technician(
            email=norm_email,
            full_name=req.full_name.strip(),
            user_id=user_id,
            hashed_password=hashed
        )
    else:
        new_user = Employee(
            email=norm_email,
            full_name=req.full_name.strip(),
            department=req.department.strip() or "General",
            user_id=user_id,
            hashed_password=hashed
        )

    user_repo.save(new_user)

    # Dispatch Real Welcome Email
    try:
        from backend.app.infrastructure.email.smtp_service import EmailService
        EmailService().send_welcome_email(
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.value,
            department=getattr(new_user, "department", "General")
        )
    except Exception:
        pass

    return {
        "status": "registered",
        "message": "User registered successfully.",
        "user": {
            "id": new_user.id,
            "name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role.value,
            "department": getattr(new_user, "department", "General")
        }
    }


@app.post("/api/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    user = user_repo.get_by_email(req.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No registered user found with this corporate email address."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or suspended. Cannot reset password."
        )
    is_strong, msg = User.validate_password_strength(req.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Weak Password Rejected: {msg}"
        )
    user.set_password(req.new_password)
    user_repo.save(user)
    return {
        "status": "success",
        "message": f"Password for {user.email} has been updated. You can now sign in."
    }


@app.get("/api/services")
def get_services():
    services = service_repo.get_all()
    return [{
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "tier": s.tier.value,
        "dependencies": getattr(s, "dependencies", [])
    } for s in services]


@app.post("/api/services", status_code=status.HTTP_201_CREATED)
def create_service(req: ServiceCreateOrUpdateRequest):
    if req.admin_id:
        user = user_repo.get_by_id(req.admin_id)
        if user and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unauthorized: Only Administrators can create IT services.")
    try:
        tier_enum = ServiceTier[req.tier.upper()]
    except KeyError:
        tier_enum = ServiceTier.BUSINESS_CRITICAL
    new_srv = ITService(
        name=req.name,
        description=req.description,
        tier=tier_enum,
        dependencies=req.dependencies
    )
    service_repo.save(new_srv)
    return {
        "id": new_srv.id,
        "name": new_srv.name,
        "description": new_srv.description,
        "tier": new_srv.tier.value,
        "dependencies": new_srv.dependencies
    }


@app.put("/api/services/{service_id}")
def update_service(service_id: str, req: ServiceCreateOrUpdateRequest):
    if req.admin_id:
        user = user_repo.get_by_id(req.admin_id)
        if user and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unauthorized: Only Administrators can edit IT services.")
    srv = service_repo.get_by_id(service_id)
    if not srv:
        raise HTTPException(status_code=404, detail=f"Service with ID '{service_id}' not found.")
    try:
        tier_enum = ServiceTier[req.tier.upper()]
    except KeyError:
        tier_enum = srv.tier
    srv.name = req.name
    srv.description = req.description
    srv.tier = tier_enum
    srv.dependencies = req.dependencies
    service_repo.save(srv)
    return {
        "id": srv.id,
        "name": srv.name,
        "description": srv.description,
        "tier": srv.tier.value,
        "dependencies": srv.dependencies
    }


@app.get("/api/admin/config")
def get_admin_config():
    from backend.app.domain.intelligence.categorizer import IntelligentCategorizer
    services = service_repo.get_all()
    sample_policy = services[0].sla_policy if services else None
    targets = sample_policy.to_dict()["targets"] if sample_policy else {}
    return {
        "active_assignment_strategy": incident_service.get_default_assignment_strategy(),
        "available_strategies": ["smart", "skill", "load", "round_robin"],
        "sla_targets": targets,
        "categories": IntelligentCategorizer.get_all_categories()
    }


@app.post("/api/admin/assignment-strategy")
def set_assignment_strategy(req: AssignmentStrategyChangeRequest):
    if req.admin_id:
        user = user_repo.get_by_id(req.admin_id)
        if user and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unauthorized: Only Administrators can switch assignment strategy.")
    incident_service.set_default_assignment_strategy(req.strategy)
    return {
        "status": "success",
        "active_assignment_strategy": incident_service.get_default_assignment_strategy(),
        "message": f"Active technician assignment strategy updated to '{req.strategy}'."
    }


@app.put("/api/admin/sla-policy")
def update_sla_policy(req: SLAPolicyUpdateRequest):
    if req.admin_id:
        user = user_repo.get_by_id(req.admin_id)
        if user and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unauthorized: Only Administrators can update SLA policy.")
    try:
        p_enum = Priority[req.priority.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid priority tier: {req.priority}")
    services = service_repo.get_all()
    for s in services:
        s.sla_policy.update_target(p_enum, req.response_minutes, req.resolution_minutes)
        service_repo.save(s)
    return {
        "status": "success",
        "priority": req.priority.upper(),
        "response_minutes": req.response_minutes,
        "resolution_minutes": req.resolution_minutes,
        "message": f"SLA policy for {req.priority.upper()} updated ({req.response_minutes}m response / {req.resolution_minutes}m resolution)."
    }


@app.post("/api/admin/categories")
def add_or_update_category(req: CategoryCreateRequest):
    if req.admin_id:
        user = user_repo.get_by_id(req.admin_id)
        if user and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unauthorized: Only Administrators can add categories.")
    from backend.app.domain.intelligence.categorizer import IntelligentCategorizer
    IntelligentCategorizer.add_or_update_category(req.name, req.keywords)
    return {
        "status": "success",
        "category": req.name,
        "keywords": req.keywords,
        "message": f"Category '{req.name}' successfully registered with {len(req.keywords)} detection keywords."
    }


@app.get("/api/users")
def get_users(role: Optional[str] = None):
    users = user_repo.get_all()
    if role:
        users = [u for u in users if u.role.value == role.upper()]
    return [
        {
            "id": u.id,
            "name": u.full_name,
            "email": u.email,
            "role": u.role.value,
            "skills": getattr(u, "skills", []),
            "load": getattr(u, "current_active_load", 0),
            "max_load": getattr(u, "max_active_load", 0)
        }
        for u in users
    ]


@app.get("/api/incidents")
def list_incidents(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    service_id: Optional[str] = None,
    technician_id: Optional[str] = None,
    search: Optional[str] = None,
    is_breached: Optional[bool] = None
):
    incidents = incident_repo.get_all(
        status=status,
        priority=priority,
        category=category,
        service_id=service_id,
        technician_id=technician_id,
        search_query=search,
        is_sla_breached=is_breached
    )
    return [serialize_incident(inc) for inc in incidents]


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    try:
        inc = incident_service.get_incident(incident_id)
        return serialize_incident(inc)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/incidents/check-duplicates")
def check_incident_duplicates(req: DuplicateCheckRequest):
    service = service_repo.get_by_id(req.service_id) if req.service_id else None
    if not service:
        services = service_repo.get_all()
        service = services[0] if services else None

    if not service:
        return {"duplicates_detected": []}

    existing_incidents = incident_repo.get_all()
    from backend.app.domain.models.incident import Incident
    from backend.app.domain.models.sla import SLATarget
    reporter = user_repo.get_by_id("user-emp-1") or (user_repo.get_all()[0] if user_repo.get_all() else None)
    if not reporter:
        return {"duplicates_detected": []}

    temp_inc = Incident(
        title=req.title.strip(),
        description=req.description.strip() if req.description else req.title.strip(),
        service=service,
        reporter=reporter,
        priority=Priority.P3,
        sla_target=SLATarget(60, 480)
    )
    duplicates = incident_service.duplicate_detector.find_potential_duplicates(temp_inc, existing_incidents)
    return {
        "duplicates_detected": [
            {"id": d[0].id, "title": d[0].title, "similarity": d[1]} for d in duplicates
        ]
    }


@app.post("/api/incidents", status_code=status.HTTP_201_CREATED)
def report_incident(req: IncidentCreateRequest):
    inc, duplicates = incident_service.report_incident(
        title=req.title,
        description=req.description,
        service_id=req.service_id,
        reporter_id=req.reporter_id,
        impact=req.impact,
        urgency=req.urgency,
        category=req.category,
        auto_assign=req.auto_assign,
        assignment_strategy=req.assignment_strategy if req.assignment_strategy != "smart" else incident_service.get_default_assignment_strategy()
    )
    return {
        "incident": serialize_incident(inc),
        "duplicates_detected": [
            {"id": d[0].id, "title": d[0].title, "similarity": d[1]} for d in duplicates
        ]
    }


@app.delete("/api/incidents/{incident_id}")
def delete_incident(incident_id: str):
    success = incident_service.delete_incident(incident_id)
    if not success:
        raise InvalidIncidentException(f"Incident {incident_id} not found")
    return {"message": f"Incident {incident_id} deleted successfully", "deleted": True}


@app.post("/api/incidents/batch-delete")
def batch_delete_incidents(req: BatchDeleteRequest):
    res = incident_service.batch_delete_incidents(req.incident_ids)
    return res


@app.post("/api/incidents/cleanup-duplicates")
def cleanup_duplicates():
    res = incident_service.cleanup_duplicates()
    return res


@app.post("/api/incidents/{incident_id}/assign")
def assign_technician(incident_id: str, req: AssignTechnicianRequest):
    try:
        inc = incident_service.assign_technician(
            incident_id=incident_id,
            actor_id=req.actor_id,
            technician_id=req.technician_id,
            strategy_name=req.strategy
        )
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/acknowledge")
def acknowledge_incident(incident_id: str, technician_id: str = Query(...)):
    try:
        inc = incident_service.acknowledge_incident(incident_id, technician_id)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/investigate")
def add_investigation_note(incident_id: str, req: ActionNoteRequest):
    try:
        inc = incident_service.start_investigation(incident_id, req.technician_id, req.notes)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str, req: ResolveRequest):
    try:
        inc = incident_service.resolve_incident(incident_id, req.technician_id, req.resolution_details)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/verify")
def verify_incident(incident_id: str, req: VerifyRequest):
    try:
        inc = incident_service.verify_incident(incident_id, req.actor_id, req.is_confirmed, req.feedback)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/close")
def close_incident(incident_id: str, actor_id: str = Query(...)):
    try:
        inc = incident_service.close_incident(incident_id, actor_id)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/request-info")
def request_additional_info(incident_id: str, req: RequestInfoRequest):
    try:
        inc = incident_service.request_additional_info(incident_id, req.technician_id, req.question)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/incidents/{incident_id}/add-info")
def add_additional_info(incident_id: str, req: AddInfoRequest):
    try:
        inc = incident_service.add_additional_info(incident_id, req.actor_id, req.info_text)
        return serialize_incident(inc)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sla/trigger-cycle")
def trigger_sla_cycle():
    """Manual trigger to execute SLA monitoring cycle and auto-escalation."""
    summary = incident_service.run_sla_and_escalation_cycle()
    return summary


@app.get("/api/analytics")
def get_analytics():
    return incident_service.get_analytics_summary()


@app.get("/api/notifications")
def get_notifications(recipient: Optional[str] = None):
    try:
        from backend.app.infrastructure.email.smtp_service import EmailService
        svc = EmailService()
        emails = svc.get_all(recipient)
        smtp_configured = svc.smtp_configured
    except Exception:
        emails = []
        smtp_configured = False
    return {
        "emails": emails,
        "smtp_configured": smtp_configured,
        "observer_dispatches": incident_service.notification_observer.dispatched_notifications
    }


@app.get("/api/in-app-notifications")
def get_in_app_notifications(user_id: Optional[str] = None, unread_only: bool = False):
    """Channel 2: In-App / Dashboard Notification Center."""
    return incident_service.in_app_notification_observer.get_user_notifications(user_id, unread_only)


@app.post("/api/in-app-notifications/{notification_id}/read")
def mark_in_app_notification_read(notification_id: str):
    success = incident_service.in_app_notification_observer.mark_as_read(notification_id)
    return {"status": "success" if success else "not_found", "notification_id": notification_id}


@app.post("/api/in-app-notifications/mark-all-read")
def mark_all_in_app_notifications_read(user_id: str = Query(...)):
    count = incident_service.in_app_notification_observer.mark_all_read(user_id)
    return {"status": "success", "marked_read_count": count}


@app.post("/api/notifications/test-email")
def send_test_email(req: TestEmailRequest):
    from backend.app.infrastructure.email.smtp_service import EmailService
    svc = EmailService()
    html = f"""
    <div style='font-family:-apple-system,BlinkMacSystemFont,sans-serif;padding:24px;background:#0c0c0c;color:#f5f5f5;border:1px solid #262626;border-radius:12px;'>
        <div style='border-bottom:1px solid #262626;padding-bottom:12px;margin-bottom:16px;'>
            <span style='color:#f97316;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;'>I-ITSM Live Notification Test</span>
            <h2 style='color:#ffffff;margin:6px 0 0 0;'>{req.subject}</h2>
        </div>
        <p style='font-size:14px;color:#d4d4d4;line-height:1.6;'>{req.message}</p>
        <div style='background:#171717;border:1px solid #262626;border-radius:8px;padding:12px;margin-top:16px;font-size:12px;color:#a3a3a3;'>
            <div>Recipient: <strong style='color:#ffffff;'>{req.to_email}</strong></div>
            <div>Timestamp: <strong style='color:#f97316;'>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</strong></div>
        </div>
    </div>
    """
    res = svc.send_email([req.to_email], req.subject, html, req.message, "TEST_EMAIL")
    return {
        "status": "success",
        "notification": res.to_dict(),
        "delivery_status": res.status,
        "smtp_configured": svc.smtp_configured,
        "smtp_error": res.smtp_error
    }


@app.post("/api/notifications/clear-outbox")
def clear_outbox():
    """Clears all dispatched emails from the internal outbox repository."""
    from backend.app.infrastructure.email.smtp_service import EmailService
    count = EmailService().clear_outbox()
    return {"cleared_count": count, "message": "Email outbox cleared successfully"}


@app.post("/api/admin/reset-database")
def reset_database():
    """Resets database and clears outbox, reseeding with clean realistic dummy records."""
    from backend.app.infrastructure.persistence.reseed import reset_and_seed_database
    reset_and_seed_database("backend/itsm.db")
    return {"message": "Database and outbox reset and reseeded with clean dummy records successfully"}


@app.post("/api/incidents/{incident_id}/override-priority")
def override_priority(incident_id: str, req: PriorityOverrideRequest):
    inc = incident_repo.get_by_id(incident_id)
    if not inc:
        raise InvalidIncidentException(f"Incident with ID '{incident_id}' not found.")
    admin = user_repo.get_by_id(req.admin_id)
    if not admin or admin.role != UserRole.ADMIN:
        raise UnauthorizedActionException("Unauthorized: Only Administrators can manually override incident priority.")

    old_p = inc.priority.value
    inc.priority = req.new_priority
    target = inc.service.sla_policy.get_target(req.new_priority)
    inc.sla_tracker = SLAStatusTracker(created_at=inc.created_at, target=target)
    inc.record_action(
        actor=admin,
        action="PRIORITY_OVERRIDDEN",
        description=f"Priority manually overridden from {old_p} to {req.new_priority.value}. Reason: {req.reason}"
    )
    incident_repo.save(inc)
    return {
        "status": "success",
        "message": f"Incident priority changed from {old_p} to {req.new_priority.value}.",
        "new_priority": req.new_priority.value
    }


@app.get("/api/reports/executive-summary")
def get_executive_summary():
    analytics = incident_service.get_analytics_summary()
    all_incidents = incident_repo.get_all()
    all_services = service_repo.get_all()
    all_techs = user_repo.get_technicians()

    service_breakdown = []
    for s in all_services:
        s_incs = [i for i in all_incidents if i.service and i.service.id == s.id]
        p1_count = sum(1 for i in s_incs if i.priority == Priority.P1)
        breached_count = sum(1 for i in s_incs if getattr(i.sla_tracker, "is_breached", False))
        service_breakdown.append({
            "service_id": s.id,
            "name": s.name,
            "tier": s.tier.value,
            "total_incidents": len(s_incs),
            "critical_p1": p1_count,
            "sla_breached": breached_count,
            "availability_status": "DEGRADED" if p1_count > 0 else "OPERATIONAL"
        })

    tech_roster = []
    for t in all_techs:
        tech_roster.append({
            "id": t.id,
            "name": t.full_name,
            "skills": getattr(t, "skills", []),
            "current_load": t.current_active_load,
            "max_load": t.max_active_load,
            "utilization_pct": round((t.current_active_load / t.max_active_load * 100), 1) if t.max_active_load else 0
        })

    return {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "kpis": analytics,
        "services": service_breakdown,
        "technicians": tech_roster,
        "total_incident_records": len(all_incidents)
    }


@app.get("/api/incidents/{incident_id}/suggested-resolutions")
def get_suggested_resolutions(incident_id: str):
    """
    Retrieves intelligent resolution recommendations for an incident (Feature G & Innovation Challenge).
    Combines historical resolution NLP pattern matching with standard operating procedure runbooks.
    """
    try:
        recommendations = incident_service.get_suggested_resolutions(incident_id)
        return {
            "incident_id": incident_id,
            "total_suggestions": len(recommendations),
            "recommendations": recommendations
        }
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch suggested resolutions: {str(e)}")


@app.get("/api/services/topology")
def get_service_topology():
    """
    Retrieves live organizational IT service dependency topology graph and operational health states.
    Fulfills Innovation Challenge: Service Dependency Graph & Incident Correlation.
    """
    try:
        return incident_service.get_service_topology()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute service topology: {str(e)}")


class AIRunbookRequest(BaseModel):
    incident_id: str
    custom_context: Optional[str] = None


@app.post("/api/ai/generate-resolution-runbook")
def generate_ai_runbook(req: AIRunbookRequest):
    """
    Generative AI Runbook Generator (Innovation Pillar).
    If GEMINI_API_KEY / Google API is set, invokes Gemini; otherwise provides smart context runbook.
    """
    try:
        incident = incident_service.get_incident(req.incident_id)
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # If Gemini API Key is available in the environment, attempt real Gemini call
        if api_key:
            try:
                import urllib.request
                import json as json_lib
                prompt = (
                    f"You are a Principal Site Reliability Engineer. Provide an exact 4-step diagnostic and "
                    f"resolution runbook for this enterprise IT incident:\n"
                    f"Title: {incident.title}\n"
                    f"Description: {incident.description}\n"
                    f"Service: {incident.service.name}\n"
                    f"Priority: {incident.priority.value}\n"
                    f"Category: {incident.category}\n"
                    f"Return concise, actionable technical CLI commands and verification steps."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                data = json_lib.dumps({
                    "contents": [{"parts": [{"text": prompt}]}]
                }).encode("utf-8")
                req_obj = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req_obj, timeout=8) as response:
                    res_json = json_lib.loads(response.read().decode("utf-8"))
                    generated_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "incident_id": req.incident_id,
                        "source": "GOOGLE_GEMINI_AI",
                        "runbook": generated_text,
                        "powered_by": "Gemini 1.5 Flash API"
                    }
            except Exception:
                pass  # Fall through to deterministic expert system runbook

        # Deterministic Expert SRE Runbook Generator
        cat = incident.category.lower() if incident.category else "general"
        expert_runbook = (
            f"### [Automated Diagnostic Runbook - {incident.category.upper()}]\n"
            f"**Target System:** {incident.service.name} ({incident.service.tier.value})\n"
            f"**Severity Tier:** {incident.priority.value}\n\n"
            f"**Step 1: Rapid Telemetry & Fault Isolation**\n"
            f"- Verify service responsiveness and HTTP/gRPC ingress metrics.\n"
            f"- Inspect error rate spikes for keyword '{incident.category}'.\n\n"
            f"**Step 2: State Rollback or Safe Restart**\n"
            f"- Drain in-flight sessions and trigger graceful rolling pod/service restart.\n"
            f"- Check connection pools and clear stale socket locks.\n\n"
            f"**Step 3: Root Cause Correction**\n"
            f"- Apply schema patch / rotate expired security credentials if authentication related.\n"
            f"- Validate CPU/Memory pressure stabilizes below 60% threshold.\n\n"
            f"**Step 4: Verification & SLA Closure**\n"
            f"- Submit probe transaction to `{incident.service.name}` and confirm HTTP 200 response.\n"
            f"- Notify {incident.reporter.full_name} and record audit postmortem."
        )
        return {
            "incident_id": req.incident_id,
            "source": "AI_EXPERT_SRE_ENGINE",
            "runbook": expert_runbook,
            "powered_by": "I-ITSM Intelligent SRE Engine"
        }
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating runbook: {str(e)}")


