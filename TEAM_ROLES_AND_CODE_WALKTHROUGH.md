# I-ITSM: Team Member Roles, Codebase Guide & Defense Manual
**Course:** CS F213 / MAC F212 Object-Oriented Programming (OOP)  
**Semester:** Semester-I, 2026–2027  
**System Name:** Intelligent IT Service Management & Incident Resolution System (I-ITSM)  
**GitHub Repository:** https://github.com/daksh-tamoli/OOPS_PROJECT_26  
**Submission Deadline:** November 22, 2026 (Hard Deadline)  

---

## 📋 Table of Contents
1. [Executive Summary: What Has Been Done vs. What Is Left To Do](#1-executive-summary)
2. [High-Level System Architecture & Design Philosophy](#2-high-level-system-architecture)
3. [Participant Roles, Code Ownership & Video Speaking Scripts](#3-participant-roles--video-scripts)
   - [Student 1: UI/UX & Frontend Integration Lead](#student-1-uiux--frontend-lead)
   - [Student 2: Backend Architecture & REST API Lead](#student-2-backend-architecture--rest-api-lead)
   - [Student 3: Domain Modeling & Core OOP Design Patterns Lead](#student-3-domain-modeling--core-oop-patterns-lead)
   - [Student 4: Database, Persistence & SLA Engine Lead](#student-4-database-persistence--sla-engine-lead)
   - [Student 5: Intelligent Features & Testing / QA Lead](#student-5-intelligent-features--testing-lead)
4. [In-Depth Codebase Walkthrough (File-by-File)](#4-in-depth-codebase-walkthrough)
   - [Domain Entities & Models](#domain-entities--models)
   - [Design Pattern 1: State Pattern](#design-pattern-1-state-pattern)
   - [Design Pattern 2: Strategy Pattern](#design-pattern-2-strategy-pattern)
   - [Design Pattern 3: Observer Pattern](#design-pattern-3-observer-pattern)
   - [Design Pattern 4: Factory Pattern](#design-pattern-4-factory-pattern)
   - [Design Pattern 5: Repository Pattern](#design-pattern-5-repository-pattern)
   - [Intelligent & Automated Features](#intelligent--automated-features)
   - [Application Service Layer](#application-service-layer)
   - [REST API Layer](#rest-api-layer)
   - [Frontend Dashboard](#frontend-dashboard)
   - [15 Automated Test Cases](#15-automated-test-cases)
5. [Demonstration Video Guide (15–20 Minutes Checklist)](#5-demonstration-video-guide)
6. [Faculty Viva / Defense Questions & Answers](#6-faculty-viva--defense-questions--answers)

---

## 1. Executive Summary

### What Has Been Done (100% of Software & Code Completed):
- **Core OOP Domain Model:** Fully encapsulated domain models (`User`, `Employee`, `Technician`, `Administrator`, `Incident`, `ITService`, `SLAPolicy`, `AuditRecord`).
- **5 Gang-of-Four Design Patterns:**
  1. *State Pattern:* 8 discrete lifecycle states enforcing valid transitions and disallowing illegal leaps.
  2. *Strategy Pattern:* 4 technician assignment strategies + 2 priority calculation strategies.
  3. *Observer Pattern:* Immutable event audit trail logging + multi-channel notification dispatches.
  4. *Factory Pattern:* Centralized instantiation, SLA binding, and automatic category inference.
  5. *Repository Pattern:* Complete storage decoupling with both in-memory and SQLite implementations.
- **Intelligent Features (Innovation Showcase):**
  1. *NLP Duplicate Detection:* TF-IDF Cosine Similarity + Jaccard token overlap + service boosting.
  2. *Automatic Hierarchical Escalation:* Detects unacknowledged SLA breaches and elevates tickets.
  3. *Intelligent Categorizer:* Heuristic keyword classification mapping descriptions to services.
- **Persistence Layer:** Persistent SQLite database (`backend/itsm.db`) via SQLAlchemy 2.0 ORM.
- **Automated Verification:** 15 comprehensive unit & integration test cases (`pytest`) covering all boundary conditions, capacity limits, and custom exceptions. All 15 pass cleanly in 0.7s.
- **Frontend Application:** Interactive React 19 + TypeScript + Vite web interface with real-time SLA countdowns, role switcher (Employee, Technician, Admin), duplicate warnings, and audit log history.
- **Academic Project Report:** Full comprehensive academic report (`PROJECT_REPORT.md`) addressing all 9 faculty questions and 7 required deliverables.
- **Version Control:** Clean repository on GitHub: [daksh-tamoli/OOPS_PROJECT_26](https://github.com/daksh-tamoli/OOPS_PROJECT_26).

### What Is Left To Do (Human Deliverables & Presentation):
1. **Assign Group Names:** Fill in your group members' names in the role table below.
2. **Convert `PROJECT_REPORT.md` to PDF:** Name the PDF `<GroupNo>_OOP_S1_2025-2026_Project.pdf` (e.g. `1_OOP_S1_2025-2026_Project.pdf`).
3. **Record the 15–20 Minute Demo Video:** Use the script and workflows outlined in Section 5. Every member must introduce themselves and speak on their module.
4. **Submit Links:** Share the GitHub repository and demo video link in the course spreadsheet before **November 22, 2026**.

---

## 2. High-Level System Architecture

I-ITSM follows **Clean Layered Architecture (Domain-Driven Design)**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                              │
│    React 19 + TypeScript + Vite Dashboard (Glassmorphic Dark UI)       │
│    Role Switcher: Employee (Alice) | Tech (Devon) | Admin (Sarah)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON REST APIs
┌───────────────────────────────────▼────────────────────────────────────┐
│                        APPLICATION API LAYER                           │
│    FastAPI Endpoints (main.py) + IncidentService Coordinator           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Pure Python Object Calls
┌───────────────────────────────────▼────────────────────────────────────┐
│                          DOMAIN OOP LAYER                              │
│  • State Pattern: Incident State Lifecycle (New ➔ Closed)              │
│  • Strategy Pattern: Tech Assignment (Skill/Load/Smart) & Priority     │
│  • Observer Pattern: Audit Logger & Notification Dispatchers           │
│  • Factory Pattern: Incident Creation & SLA Binding                    │
│  • Intelligence: TF-IDF Duplicate Detector & Auto-Escalation Engine   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ IRepository Interfaces
┌───────────────────────────────────▼────────────────────────────────────┐
│                        INFRASTRUCTURE LAYER                            │
│    SQLAlchemy 2.0 ORM Models ➔ SQLite Database (backend/itsm.db)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Participant Roles & Video Scripts

The course evaluation rubric explicitly looks for individual member contribution across software modules. Below is the 5-member allocation:

```
┌─────────────┬──────────────────────────┬──────────────────────────────────────┐
│ Member      │ Specialization           │ Key Code Files Owned                 │
├─────────────┼──────────────────────────┼──────────────────────────────────────┤
│ Student 1   │ UI/UX & Frontend Lead    │ frontend/src/App.tsx, index.css      │
│ Student 2   │ Backend & API Lead       │ backend/app/main.py, start.sh        │
│ Student 3   │ Domain & OOP Architect   │ models/, states/, strategies/        │
│ Student 4   │ Database & SLA Lead      │ persistence/sqlite_repo.py, sla.py   │
│ Student 5   │ Intelligence & QA Lead   │ intelligence/, tests/                │
└─────────────┴──────────────────────────┴──────────────────────────────────────┘
```

---

### Student 1: UI/UX & Frontend Lead
- **Primary Responsibility:** Design of the responsive web interface, role switching mechanism, lifecycle visualizer, real-time SLA badges, and duplicate incident alert banner.
- **Key Code Files:**
  - [`frontend/src/App.tsx`](file:///Users/dakshtamoli/Documents/OOPS%20Project/frontend/src/App.tsx)
  - [`frontend/src/index.css`](file:///Users/dakshtamoli/Documents/OOPS%20Project/frontend/src/index.css)
- **Technical Explanation:**
  - Built with **React 19 and TypeScript** for strict typing that mirrors the backend schema.
  - Implemented role-based contextual rendering:
    - *Employee View:* Shows the "Report Incident" modal and "Verify Resolution" options.
    - *Technician View:* Shows the "Acknowledge", "Add Investigation Notes", and "Resolve" workflows.
    - *Admin View:* Displays the live technician capacity roster, SLA daemon runner, and closure controls.
  - Custom glassmorphic CSS using CSS variables, glowing badges for priority tiers (P1 = rose, P2 = amber, P3 = blue), and pulsing indicator for active investigation.
- **Speaking Script for Video Demo (3–4 Mins):**
  > *"Hello everyone, I am [Student 1 Name], responsible for the User Interface and Frontend User Experience of the I-ITSM platform. As required by our project specification, an enterprise system must accommodate different user profiles without overwhelming them. In `App.tsx`, we built role-tailored perspectives for Employees, Technicians, and IT Administrators. Notice our State Machine visualizer: when an incident is selected, you can immediately trace its position across the 8 lifecycle states. I also built our proactive SLA risk indicators that highlight when a ticket enters critical breach status. During ticket creation, if our backend NLP engine detects a duplicate, the UI intercepts submission with a real-time similarity alert banner."*

---

### Student 2: Backend Architecture & REST API Lead
- **Primary Responsibility:** REST API layer design, serialization, request/response DTO schemas, and lifecycle application orchestration.
- **Key Code Files:**
  - [`backend/app/main.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/main.py)
  - [`backend/app/services/incident_service.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/services/incident_service.py)
  - [`start.sh`](file:///Users/dakshtamoli/Documents/OOPS%20Project/start.sh)
- **Technical Explanation:**
  - Built with **FastAPI** using asynchronous routing and Pydantic v2 schemas for strict input validation.
  - Coordinates the `IncidentService` aggregate coordinator, connecting incoming HTTP actions directly into domain method calls (`acknowledge()`, `resolve()`, `verify()`).
  - Implements CORS middleware and seeds the organizational hierarchy (Payment, SSO, DB services; Alice, Devon, Maya, Sarah users).
- **Speaking Script for Video Demo (3–4 Mins):**
  > *"Hi, I am [Student 2 Name], and I architected the Backend API and Application Service layer. In `main.py` and `incident_service.py`, we adopted the Clean Architecture approach. The API endpoints do not contain messy database queries or raw state mutations; instead, they parse typed Pydantic payloads and delegate operations to our `IncidentService`. For example, when a technician acknowledges a ticket via `POST /api/incidents/{id}/acknowledge`, the service verifies user permissions, starts the response SLA timer, and triggers the State pattern transition. We also exposed automatic OpenAPI Swagger docs at `/docs` and provided a single `start.sh` runner."*

---

### Student 3: Domain Modeling & Core OOP Design Patterns Lead
- **Primary Responsibility:** Pure object-oriented domain modeling, encapsulation, inheritance hierarchy, and implementation of the **State**, **Strategy**, **Observer**, and **Factory** patterns.
- **Key Code Files:**
  - [`backend/app/domain/models/incident.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/incident.py)
  - [`backend/app/domain/models/user.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/user.py)
  - [`backend/app/domain/states/incident_state.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/states/incident_state.py)
  - [`backend/app/domain/strategies/assignment.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/strategies/assignment.py)
  - [`backend/app/domain/strategies/priority.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/strategies/priority.py)
  - [`backend/app/domain/observers/concrete.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/observers/concrete.py)
- **Technical Explanation:**
  - **Inheritance:** `User` base class inherited by `Employee`, `Technician`, and `Administrator`.
  - **Encapsulation:** Private variables (e.g. `_state`, `_id`) exposed via read-only `@property` getters; mutation occurs solely through domain methods.
  - **State Pattern:** Concrete state classes (`NewState`, `AssignedState`, etc.) implement `IncidentState`. Illegal calls raise custom `InvalidStateTransitionException`.
  - **Strategy Pattern:** `IAssignmentStrategy` defines `select_technician()`, implemented by `SkillBasedAssignment`, `LeastLoadedAssignment`, and `CompositeSmartAssignment`.
  - **Observer Pattern:** `IIncidentObserver` registered on `Incident`; `AuditObserver` logs transitions while `NotificationObserver` sends alerts.
- **Speaking Script for Video Demo (4–5 Mins):**
  > *"Hello, I am [Student 3 Name], and I designed the Object-Oriented Domain Model and Design Patterns. As an OOP course, our primary goal was demonstrating how patterns solve real enterprise problems. In `incident_state.py`, we used the State Pattern: an incident starts in `NewState` and can only progress through valid steps. If anyone tries to transition a new ticket directly to `Closed`, our state machine intercepts it and throws an `InvalidStateTransitionException`. For technician assignment, we used the Strategy Pattern under `assignment.py`. We can switch at runtime between Skill-based matching, Least-Loaded balancing, or our Composite Smart algorithm. Finally, using the Observer Pattern, our `Incident` notifies `AuditObserver` on every transition, producing an immutable audit trail."*

---

### Student 4: Database, Persistence & SLA Engine Lead
- **Primary Responsibility:** Relational database schema, Repository Pattern persistence, and Service Level Agreement (SLA) calculations and compliance tracking.
- **Key Code Files:**
  - [`backend/app/infrastructure/persistence/sqlite_repo.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/infrastructure/persistence/sqlite_repo.py)
  - [`backend/app/domain/repositories/interfaces.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/repositories/interfaces.py)
  - [`backend/app/domain/models/sla.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/sla.py)
- **Technical Explanation:**
  - **Repository Pattern:** `IIncidentRepository`, `IUserRepository`, and `IServiceRepository` decouple domain logic from database drivers.
  - **SQLAlchemy 2.0 ORM:** Maps domain entities to relational tables (`incidents`, `users`, `services`, `audit_records`) in SQLite (`backend/itsm.db`).
  - **SLA Calculation:** Computes strict response (P1: 5m, P2: 15m, P3: 60m) and resolution (P1: 30m, P2: 2h, P3: 8h) deadlines.
  - **Timezone Normalization:** Handles UTC conversion across persisted datetimes to ensure reliable risk evaluations.
- **Speaking Script for Video Demo (3–4 Mins):**
  > *"Hello, I am [Student 4 Name], responsible for Persistence and the SLA Management Engine. In `sqlite_repo.py`, we implemented the Repository Pattern using SQLAlchemy. This means our core business domain doesn't depend on SQL statements or database tables directly. When an incident is saved, our repository serializes the domain aggregate, its assigned technician, and its audit history into SQLite. In `sla.py`, we model our Service Level Agreements. When a P1 ticket is created, it calculates a 5-minute response target and a 30-minute resolution target. Our `is_resolution_at_risk()` method proactively detects when 70% of the SLA window has expired, giving support teams early warning before a penalty occurs."*

---

### Student 5: Intelligent Features & Testing / QA Lead
- **Primary Responsibility:** Machine learning / NLP duplicate detection, automatic hierarchical escalation engine, and the 15-test-case validation suite.
- **Key Code Files:**
  - [`backend/app/domain/intelligence/duplicate_detector.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/intelligence/duplicate_detector.py)
  - [`backend/app/domain/intelligence/escalation_engine.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/intelligence/escalation_engine.py)
  - [`backend/app/domain/intelligence/categorizer.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/intelligence/categorizer.py)
  - [`backend/tests/test_oops_requirements.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/tests/test_oops_requirements.py)
- **Technical Explanation:**
  - **Duplicate Detection:** Employs TF-IDF Vectorization (`scikit-learn`) and Cosine Similarity, blended with Jaccard token overlap and service metadata boosting to flag similar tickets.
  - **Automatic Escalation:** Evaluates unacknowledged tickets. If a critical ticket breaches response SLA, it elevates:  
    $$\text{Technician} \longrightarrow \text{Team Lead} \longrightarrow \text{System Admin} \longrightarrow \text{IT Manager}$$
  - **Test Suite:** 15 pytest test cases verifying state transition boundaries, capacity limits, SLA computations, duplicate detection, and security exceptions.
- **Speaking Script for Video Demo (3–4 Mins):**
  > *"Hi everyone, I am [Student 5 Name], and I led the Intelligent Features and Automated Testing. For our innovation component, we developed `duplicate_detector.py` using TF-IDF text vectorization and cosine similarity. In a large company, when a payment service goes down, hundreds of users file similar reports. Our detector identifies this in real time, calculating confidence scores and correlating duplicate tickets under a parent outage. We also built `escalation_engine.py`, which monitors tickets in the background and automatically escalates unacknowledged P1 tickets up the chain of command to the IT Manager. Finally, I authored our test suite in `test_oops_requirements.py`, which validates 15 distinct business scenarios with 100% pass rate."*

---

## 4. In-Depth Codebase Walkthrough

### Domain Entities & Models
- **[`user.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/user.py):**
  - Base class `User` encapsulates `_id`, `_email`, `_full_name`, and `_role`.
  - `Technician(User)` extends `User` with `skills`, `max_active_load`, `current_active_load`, and workload capacity methods `allocate_ticket()` and `release_ticket()`. Throws `TechnicianCapacityExceededException` when full.
  - `Employee(User)` and `Administrator(User)` provide specialized role identities.
- **[`incident.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/incident.py):**
  - Aggregate root encapsulating ticket attributes.
  - Serves as the **Context** for the State Pattern (`self._state: IncidentState`).
  - Serves as the **Subject** for the Observer Pattern (`self._observers: List[IIncidentObserver]`).
- **[`sla.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/sla.py):**
  - `SLAPolicy`: Defines targets per priority tier (P1: 5m/30m, P2: 15m/2h, P3: 1h/8h, P4: 4h/24h).
  - `SLAStatusTracker`: Tracks `response_deadline`, `resolution_deadline`, records `responded_at`, `resolved_at`, and detects breaches with timezone-normalized comparisons.
- **[`audit.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/models/audit.py):**
  - `AuditRecord`: Immutable value object recording `incident_id`, `actor_name`, `action`, `previous_state`, `new_state`, and `timestamp`.

---

### Design Pattern 1: State Pattern
- **File:** [`backend/app/domain/states/incident_state.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/states/incident_state.py)
- **Concept:** Replaces fragile `if/else` checks with polymorphic state classes.
- **Hierarchy:**
  ```
               ┌───────────────────────┐
               │ IncidentState (ABC)   │
               └───────────┬───────────┘
     ┌─────────────┬───────┴──────┬─────────────┐
     ▼             ▼              ▼             ▼
  NewState   AssignedState   ResolvedState  ClosedState ...
  ```
- **Key Method Invariant:**
  Calling `incident.close()` while in `NewState` triggers `NewState.close()`, which executes:
  ```python
  raise InvalidStateTransitionException(self.status.value, IncidentStatus.CLOSED.value, "Cannot close from current state.")
  ```
- **Resolution Rejection:**
  In `ResolvedState.verify()`, if the user sets `is_confirmed=False`, the incident transitions back to `InProgressState` with user feedback appended.

---

### Design Pattern 2: Strategy Pattern
- **Files:**
  - [`assignment.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/strategies/assignment.py)
  - [`priority.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/strategies/priority.py)
- **Concept:** Encapsulates algorithms into interchangeable classes conforming to a common contract.
- **Technician Assignment Strategies:**
  1. `SkillBasedAssignment`: Filters technicians by skill match matching incident category, ranking by performance rating.
  2. `LeastLoadedAssignment`: Selects candidate with lowest `current_active_load`.
  3. `RoundRobinAssignment`: Rotates assignments sequentially.
  4. `CompositeSmartAssignment`: Computes weighted suitability:
     $$\text{Score} = (0.40 \times \text{Skill}) + (0.30 \times \text{Available Capacity}) + (0.30 \times \text{Rating})$$
- **Priority Calculation Strategies:**
  1. `MatrixPriorityStrategy`: Standard ITIL Risk Matrix (High/Med/Low) with Tier-1 service criticality override.
  2. `WeightedCriticalityStrategy`: Mathematical formula calculating numerical priority thresholds.

---

### Design Pattern 3: Observer Pattern
- **Files:**
  - [`interface.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/observers/interface.py)
  - [`concrete.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/observers/concrete.py)
- **Concept:** Decouples event generation from side-effects.
- **Implementation:**
  - `Incident` maintains a list of `IIncidentObserver` subscribers.
  - When state changes, `incident.notify_state_changed()` triggers:
    - `AuditObserver.on_state_changed()`: Appends record to immutable audit log.
    - `NotificationObserver.on_state_changed()`: Dispatches simulated in-app and email notifications.

---

### Design Pattern 4: Factory Pattern
- **File:** [`backend/app/domain/factories/incident_factory.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/factories/incident_factory.py)
- **Concept:** Centralizes aggregate creation logic and guarantees valid initial state.
- **Functionality:**
  - Auto-infers category via NLP if not supplied.
  - Calculates priority via configured priority strategy.
  - Retrieves service SLA policy and constructs the initialized `Incident` aggregate with `NewState`.

---

### Design Pattern 5: Repository Pattern
- **Files:**
  - [`interfaces.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/repositories/interfaces.py)
  - [`sqlite_repo.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/infrastructure/persistence/sqlite_repo.py)
  - [`in_memory_repo.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/infrastructure/persistence/in_memory_repo.py)
- **Concept:** Mediates between domain and data mapping layers using collection-like interfaces.
- **Benefit:** `IncidentService` interacts only with `IIncidentRepository`. It can run against `InMemoryIncidentRepository` for lightning-fast testing, or `SqliteIncidentRepository` for production persistence, without changing a single line of domain code.

---

### Intelligent & Automated Features
- **Duplicate Detection ([`duplicate_detector.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/intelligence/duplicate_detector.py)):**
  - Extracts text from open tickets.
  - Generates TF-IDF vectors using `scikit-learn` and computes Cosine Similarity.
  - Combines with Jaccard word-level overlap and applies a 30% boost for identical services.
- **Hierarchical Escalation Engine ([`escalation_engine.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/intelligence/escalation_engine.py)):**
  - Triggered periodically or on-demand by IT Administrators.
  - Identifies unacknowledged critical tickets past response deadline and logs formal escalation audit records.
- **Intelligent Categorizer ([`categorizer.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/app/domain/intelligence/categorizer.py)):**
  - Keyword density mapping for `Database`, `Network`, `Authentication`, `Cloud`, `Payment`, and `Hardware`.

---

### 15 Automated Test Cases
Located in [`backend/tests/test_oops_requirements.py`](file:///Users/dakshtamoli/Documents/OOPS%20Project/backend/tests/test_oops_requirements.py):

| Test ID | Test Function | What It Validates |
| :--- | :--- | :--- |
| **TC-01** | `test_tc01_prevent_invalid_state_transition_new_to_closed` | State Pattern rejects illegal direct transition `NEW` $\to$ `CLOSED`. |
| **TC-02** | `test_tc02_complete_valid_lifecycle_transitions` | Full sequential 8-step lifecycle walkthrough from `NEW` to `CLOSED`. |
| **TC-03** | `test_tc03_priority_calculation_critical_service` | Matrix strategy computes `P1` for High Impact on Tier-1 critical service. |
| **TC-04** | `test_tc04_skill_based_technician_assignment` | Skill strategy routes Database ticket to technician with DB skills. |
| **TC-05** | `test_tc05_least_loaded_technician_assignment` | Load strategy routes ticket to technician with lowest active load. |
| **TC-06** | `test_tc06_technician_capacity_exceeded_exception` | Technician throws capacity exception when `current_active_load >= max`. |
| **TC-07** | `test_tc07_sla_deadline_computation` | P1 incident automatically calculates 5m response and 30m resolution deadlines. |
| **TC-08** | `test_tc08_sla_risk_warning_detection` | Proactive warning flag triggers when elapsed time exceeds 70% of SLA. |
| **TC-09** | `test_tc09_automatic_escalation_on_unacknowledged_breach` | Unacknowledged P1 breach triggers auto-escalation to IT Manager. |
| **TC-10** | `test_tc10_intelligent_duplicate_detection` | NLP engine matches concurrent payment failures with confidence score. |
| **TC-11** | `test_tc11_immutable_audit_trail_logging` | Observer logs immutable audit history across consecutive state transitions. |
| **TC-12** | `test_tc12_unauthorized_action_exception` | RBAC blocks employees from acknowledging or resolving technician tickets. |
| **TC-13** | `test_tc13_observer_pattern_notification_dispatch` | Observer dispatches simulated alerts upon state transitions. |
| **TC-14** | `test_tc14_intelligent_categorizer_text_inference` | NLP categorizer correctly classifies "deadlock" as `Database`. |
| **TC-15** | `test_tc15_resolution_verification_and_reopen_feedback` | Rejection of resolution reverts status from `RESOLVED` back to `IN_PROGRESS`. |

---

## 5. Demonstration Video Guide (15–20 Minutes Checklist)

Per syllabus page 17, the demo video must be uploaded to the shared folder and named:  
`<GroupNo>_OOP_S1_2025-2026_Project.mp4`

### Recommended Video Structure:
1. **Introduction (0:00 – 2:30):**
   - All group members appear on camera, state their name, and explain their role/module.
   - Screen shares the GitHub repository and high-level architecture diagram.
2. **Workflow 1: Incident Creation & Auto-Assignment (2:30 – 7:30):**
   - Switch role to **Employee (Alice)**.
   - Fill the "Report Incident" form with a payment failure ("Payment Gateway down, users unable to transact").
   - Demonstrate:
     - Factory pattern auto-calculates Priority as **P1 - Critical**.
     - System auto-assigns **Devon Vance (DB Specialist)** using Composite Smart Strategy.
     - In-app notification and audit trail log are generated.
3. **Workflow 2: Technician Triage & Resolution Verification (7:30 – 12:30):**
   - Switch role to **Technician (Devon)**.
   - Acknowledge ticket $\to$ state becomes `ACKNOWLEDGED`, response SLA is marked.
   - Add investigation notes $\to$ state becomes `IN_PROGRESS`.
   - Provide resolution details and resolve $\to$ state becomes `RESOLVED`.
   - Switch role back to **Employee (Alice)** $\to$ show verification confirmation.
4. **Workflow 3: Duplicate Incident Detection & Auto-Escalation (12:30 – 17:00):**
   - As Employee, report another similar payment ticket.
   - Show the **NLP Duplicate Warning Alert Banner** with similarity percentage.
   - Switch to **Admin (Sarah)** $\to$ click **Run SLA Daemon** $\to$ show alert dialog confirming evaluation of overdue tickets and auto-escalation.
5. **Testing & Code Walkthrough (17:00 – 19:30):**
   - Run `pytest backend/tests/test_oops_requirements.py -v` in terminal to show 15/15 tests passing.
   - Show SQLite database persistence by restarting server and showing tickets persist.

---

## 6. Faculty Viva / Defense Questions & Answers

### Q1: Why did you use the State Pattern instead of a simple `status` string?
> **Answer:** *"A simple status string allows illegal transitions like `NEW` directly to `CLOSED`, bypassing investigation and verification. In our State Pattern (`incident_state.py`), each lifecycle phase is a separate class implementing `IncidentState`. State transition logic and permitted operations are encapsulated inside each state. Any illegal transition raises an `InvalidStateTransitionException`, protecting business invariant rules."*

### Q2: How does your system satisfy the Open/Closed Principle?
> **Answer:** *"Our Strategy and Repository patterns embody the Open/Closed Principle. If we want to add a new technician assignment algorithm (e.g. AI-based latency assignment), we simply write a new class implementing `IAssignmentStrategy` without modifying existing domain code. Similarly, adding a new database engine only requires implementing `IIncidentRepository`."*

### Q3: How is encapsulation demonstrated in your domain models?
> **Answer:** *"In `Incident` and `User`, internal state attributes such as `_state`, `_id`, and `_current_active_load` are private. External callers cannot directly overwrite these values. Instead, they must call validated domain methods like `assign()`, `allocate_ticket()`, or `transition_to()`, which validate constraints, record audit logs, and notify observers."*

### Q4: How does your duplicate detection algorithm work?
> **Answer:** *"In `duplicate_detector.py`, we combine TF-IDF (Term Frequency-Inverse Document Frequency) vectorization with Cosine Similarity. We compute n-gram term weights across active incident descriptions and calculate the angle between vector representations. We complement this with word token Jaccard overlap and apply a 30% boost if tickets belong to the same IT service."*

### Q5: How do you handle Service Level Agreement (SLA) violations?
> **Answer:** *"In `sla.py`, each service tier has predefined response and resolution targets. `SLAStatusTracker` computes exact deadlines and has an `is_resolution_at_risk()` method that triggers warnings when 70% of the allocated time has elapsed. When deadlines expire on unacknowledged tickets, our `AutomaticEscalationEngine` escalates the incident to higher management tiers and records an immutable escalation audit entry."*
