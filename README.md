# I-ITSM — Intelligent IT Service Management & Incident Resolution System

Course project for **CS F213 / MAC F212 (Object-Oriented Programming)**, Semester-I, 2026–2027.  
**Group 75**
- **Daksh Tamoli** (`2024B5A70797H`)
- **Devang Mittal** (`2024B3AD0578H`)
- **Dhruv Vadadoriya** (`2024B5AD0815H`)
- **Chaitanya Somani** (`2024B3AD0571H`)

---

## Overview

I-ITSM is a full-stack IT incident management application that handles the complete lifecycle of service disruptions:

$$\text{NEW} \longrightarrow \text{CLASSIFIED} \longrightarrow \text{ASSIGNED} \longrightarrow \text{ACKNOWLEDGED} \longrightarrow \text{IN\_PROGRESS} \longrightarrow \text{RESOLVED} \longrightarrow \text{VERIFIED} \longrightarrow \text{CLOSED}$$

The backend uses a layered architecture (Domain, Application, Infrastructure, and API layers) to keep the core OOP domain models independent of FastAPI and SQLAlchemy.

---

## Features

- **Role-Based Workspaces:** Separate dashboards and permissions for Employees (report tickets, track SLAs, reply to info requests, verify/reopen fixes, rate resolutions), Technicians (triage assigned tickets, track active workload, request info, apply suggested resolutions), and Administrators (manage services, categories, SLA policies, and assignment strategies at runtime; view analytics and audit logs).
- **SLA Engine & Auto-Escalation:** Computes response and resolution deadlines per priority (`P1`–`P4`), renders live countdowns, flags at-risk tickets past 70% elapsed time, and escalates unacknowledged breaches (`Technician -> Team Lead -> SysAdmin -> IT Manager`).
- **Dual Notification Channels:** Dispatches alerts through SMTP email (with a local outbox fallback when credentials are not configured) and an in-app notification center with unread tracking.
- **Duplicate Detection & Auto-Categorization:** Uses TF-IDF cosine similarity and Jaccard token overlap to flag related active incidents and infer categories from ticket descriptions.
- **Suggested Resolutions:** Recommends fixes using historical resolved incidents alongside built-in SRE runbooks (with optional Gemini API support).
- **Service Dependency Graph:** Models upstream/downstream dependencies between IT services and marks downstream services as `IMPACTED` when a core dependency goes critical.
- **Audit Trail:** Append-only history recording timestamp, actor, action, previous state, new state, and notes for every lifecycle event.

---

## OOP Design Patterns

- **State Pattern** (`backend/app/domain/states/incident_state.py`): Enforces valid transitions across 8 state classes (`NewState` through `ClosedState`) and raises `InvalidStateTransitionException` on illegal jumps (such as `NEW -> CLOSED`). Rejecting a resolution transitions a ticket from `RESOLVED` back to `IN_PROGRESS`.
- **Strategy Pattern** (`backend/app/domain/strategies/`):
  - *Technician Assignment (`IAssignmentStrategy`):* `SkillBasedAssignment`, `LeastLoadedAssignment`, `RoundRobinAssignment`, and `CompositeSmartAssignment`.
  - *Priority Calculation (`IPriorityStrategy`):* `MatrixPriorityStrategy` (ITIL Impact x Urgency matrix with Tier-1 override) and `WeightedCriticalityStrategy`.
- **Observer Pattern** (`backend/app/domain/observers/`): `AuditObserver`, `NotificationObserver` (SMTP/outbox), and `InAppNotificationObserver` listen to incident lifecycle and SLA events.
- **Factory Pattern** (`backend/app/domain/factories/incident_factory.py`): `IncidentFactory` handles ticket creation, category inference, priority calculation, and SLA binding.
- **Repository Pattern** (`backend/app/domain/repositories/interfaces.py`): Separates domain logic from SQLite/SQLAlchemy 2.0 persistence.

---

## Tech Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn, SQLAlchemy 2.0, SQLite, scikit-learn, NumPy, Pytest
- **Frontend:** React 19, TypeScript, Vite, Lucide React

---

## Local Setup

### 1. Environment Configuration
Copy `.env.example` to `.env` if you want to configure live SMTP or Gemini API credentials. Both are optional—the app runs offline-safe using the local outbox and built-in runbooks if left blank.

### 2. Run the Backend
```bash
source backend/venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```
Interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
The application runs at [http://localhost:5173](http://localhost:5173).

---

## Running Tests

The test suite (`backend/tests/test_oops_requirements.py`) contains 25 automated Pytest cases covering state transitions, assignment and priority strategies, SLA deadlines and escalations, NLP duplicate detection and categorization, RBAC and authentication, dual notification channels, suggested resolutions, service topology cascades, and all 12 custom domain exceptions.

```bash
source backend/venv/bin/activate
PYTHONPATH=. pytest backend/tests/test_oops_requirements.py -v
```

---

## Documentation & Deliverables

Full problem analysis, priority algorithm specification, architecture and UML diagrams (Use Case, Class, ER), database schema, security architecture, technology justification, and the 25-case test matrix are documented in the comprehensive project technical report (`I-ITSM Group 75 Comprehensive Technical Report.pdf`).
