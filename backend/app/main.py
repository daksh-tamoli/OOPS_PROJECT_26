import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.domain.models.enums import UserRole, IncidentStatus, Priority, Impact, Urgency, ServiceTier
from backend.app.domain.models.user import Employee, Technician, Administrator, User
from backend.app.domain.models.service import ITService
from backend.app.domain.exceptions import DomainException, EntityNotFoundException, InvalidStateTransitionException
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        tier=ServiceTier.TIER_1_CRITICAL
    )
    srv_auth = ITService(
        service_id="srv-auth",
        name="Single Sign-On (SSO)",
        description="Central authentication and LDAP service",
        tier=ServiceTier.TIER_1_CRITICAL
    )
    srv_db = ITService(
        service_id="srv-db",
        name="Core PostgreSQL DB",
        description="Primary organizational relational database clusters",
        tier=ServiceTier.TIER_1_CRITICAL
    )
    srv_cloud = ITService(
        service_id="srv-cloud",
        name="Cloud Storage & CDN",
        description="S3 buckets and media delivery assets",
        tier=ServiceTier.TIER_2
    )
    srv_email = ITService(
        service_id="srv-email",
        name="Internal Mail Exchange",
        description="Corporate messaging and communication",
        tier=ServiceTier.TIER_3
    )

    for s in [srv_payment, srv_auth, srv_db, srv_cloud, srv_email]:
        service_repo.save(s)

    # 2. Users
    admin = Administrator(
        user_id="user-admin-1",
        email="admin@itsm.local",
        full_name="Sarah Connor (IT Manager)"
    )
    emp1 = Employee(
        user_id="user-emp-1",
        email="alice@company.com",
        full_name="Alice Smith (Finance)",
        department="Finance"
    )
    emp2 = Employee(
        user_id="user-emp-2",
        email="john@company.com",
        full_name="John Doe (Engineering)",
        department="Engineering"
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
        performance_rating=4.9
    )
    tech2 = Technician(
        user_id="tech-102",
        email="maya@itsm.local",
        full_name="Maya Lin (Network & Cloud)",
        skills=["network", "cloud", "security"],
        max_active_load=5,
        current_active_load=0,
        experience_years=4.0,
        performance_rating=4.7
    )
    tech3 = Technician(
        user_id="tech-103",
        email="liam@itsm.local",
        full_name="Liam Gallagher (App & Auth)",
        skills=["application", "authentication", "software"],
        max_active_load=3,
        current_active_load=0,
        experience_years=3.2,
        performance_rating=4.5
    )

    for u in [admin, emp1, emp2, tech1, tech2, tech3]:
        user_repo.save(u)


seed_data()


# ==============================================================================
# Pydantic Request / Response Schemas
# ==============================================================================
class IncidentCreateRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    service_id: str
    reporter_id: str
    impact: Impact = Impact.MEDIUM
    urgency: Urgency = Urgency.MEDIUM
    category: Optional[str] = None
    assignment_strategy: str = "smart"
    auto_assign: bool = True


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
        "created_at": inc.created_at.isoformat(),
        "sla": {
            "response_deadline": inc.sla_tracker.response_deadline.isoformat(),
            "resolution_deadline": inc.sla_tracker.resolution_deadline.isoformat(),
            "responded_at": inc.sla_tracker.responded_at.isoformat() if inc.sla_tracker.responded_at else None,
            "resolved_at": inc.sla_tracker.resolved_at.isoformat() if inc.sla_tracker.resolved_at else None,
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
    return {"status": "healthy", "service": "I-ITSM Platform"}


@app.get("/api/services")
def get_services():
    services = service_repo.get_all()
    return [{"id": s.id, "name": s.name, "description": s.description, "tier": s.tier.value} for s in services]


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


@app.post("/api/incidents", status_code=status.HTTP_201_CREATED)
def report_incident(req: IncidentCreateRequest):
    try:
        inc, duplicates = incident_service.report_incident(
            title=req.title,
            description=req.description,
            service_id=req.service_id,
            reporter_id=req.reporter_id,
            impact=req.impact,
            urgency=req.urgency,
            category=req.category,
            auto_assign=req.auto_assign,
            assignment_strategy=req.assignment_strategy
        )
        return {
            "incident": serialize_incident(inc),
            "duplicates_detected": [
                {"id": d[0].id, "title": d[0].title, "similarity": d[1]} for d in duplicates
            ]
        }
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))


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


@app.post("/api/sla/trigger-cycle")
def trigger_sla_cycle():
    """Manual trigger to execute SLA monitoring cycle and auto-escalation."""
    summary = incident_service.run_sla_and_escalation_cycle()
    return summary


@app.get("/api/analytics")
def get_analytics():
    return incident_service.get_analytics_summary()


@app.get("/api/notifications")
def get_notifications():
    return incident_service.notification_observer.dispatched_notifications
