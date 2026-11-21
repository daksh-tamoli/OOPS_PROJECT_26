# Technology Selection & Architecture Specification
**Course**: CS F213 / MAC F212 — Object-Oriented Programming (OOPS)  
**Deliverable**: Option C — Full-Stack Enterprise Application Justification  

---

## 1. Official Architecture Selection

In accordance with the **Freedom of Technology Choice** guidelines provided in the course syllabus:
> *"Option C — Full-Stack Application: A team may develop both: Web/Mobile Frontend, Backend/API Layer, Business Logic, and Database... Technology selection is part of the project. Students are expected to explain why the selected technologies are appropriate rather than simply choosing a technology because it is familiar."*

Our system is engineered as an **Option C: Enterprise Full-Stack Tiered Architecture** with strict layer decoupling, Domain-Driven Design (DDD), and pure Object-Oriented Principles.

```
+--------------------------------------------------------------------------------+
|                   PRESENTATION LAYER (Web Client Single-Page App)              |
|   React 19 + TypeScript + Vite + Zed Black Vanilla CSS Design System           |
|   - Real-Time SLA Countdown Timers & Local State Machines                      |
|   - Executive Reports, PDF/Print Publication Engine                            |
|   - Live Email Dispatch Notification Center & In-App Outbox Preview            |
|   - Role-Based Dynamic Workspaces (Employee, Technician, Administrator)        |
+--------------------------------------------------------------------------------+
                                       |
                       HTTPS / RESTful JSON Contract (OpenAPI 3.0)
                                       v
+--------------------------------------------------------------------------------+
|                    APPLICATION SERVICE & API ORCHESTRATION LAYER               |
|   Python 3.13 + FastAPI + Pydantic v2                                          |
|   - REST Controller Endpoints, Input Validation & Authentication Handlers      |
|   - IncidentService, AnalyticsService, EmailService (Singleton Outbox)         |
+--------------------------------------------------------------------------------+
                                       |
                   Encapsulated Method Invocations & Domain Invariants
                                       v
+--------------------------------------------------------------------------------+
|                         CORE DOMAIN BUSINESS LOGIC LAYER                       |
|   Pure Object-Oriented Programming (Zero Framework Dependencies)               |
|   - Domain Aggregates: Incident, User, Technician, Employee, Administrator     |
|   - Design Patterns:                                                           |
|     * Factory Pattern (IncidentFactory)                                        |
|     * State Pattern (New, Acknowledged, InProgress, Resolved, Verified, Closed)|
|     * Strategy Pattern (SkillBased, LeastLoaded, RoundRobin, CompositeSmart)   |
|     * Observer Pattern (AuditObserver, NotificationObserver, EmailDispatcher)  |
|     * Rules Engines (PriorityCalculator, AutomaticEscalationEngine)            |
|     * Intelligence: TF-IDF Duplicate Detector & Keyword Categorizer           |
+--------------------------------------------------------------------------------+
                                       |
                         Repository Pattern Interface
                                       v
+--------------------------------------------------------------------------------+
|                     PERSISTENCE & DATA STORAGE LAYER                           |
|   SQLite 3 + SQLAlchemy ORM Session Factory                                    |
|   - ACID Transactional Integrity with Atomic Commits                           |
|   - Normalized Relational Tables: incidents, users, it_services, audit_logs   |
|   - Foreign Key Constraints & Capacity Enforcement Invariants                  |
+--------------------------------------------------------------------------------+
```

---

## 2. In-Depth Technology Justifications

### A. Core Business Logic & Backend: **Python 3.13**
* **Why Appropriate (Not Just Familiar)**:
  1. **First-Class OOPS Capabilities**: Python 3.13 provides native Abstract Base Classes (`abc.ABC`, `@abstractmethod`), multiple inheritance (MRO), property encapsulation (`@property`, `@setter`), and type annotations.
  2. **Encapsulation & Invariants**: Enforces class boundaries (e.g. `_current_active_load` and `_max_active_load` in `Technician`) ensuring that state mutations cannot bypass capacity validations.
  3. **Behavioral Design Pattern Fidelity**: Clean implementation of the State Pattern, Strategy Pattern, Observer Pattern, and Factory Pattern without boilerplate code.

### B. RESTful API & Transport: **FastAPI + Pydantic v2**
* **Why Appropriate for Enterprise Scale**:
  1. **Strict Type Safety & Schema Validation**: Pydantic v2 validates JSON payloads against domain schemas at compile/runtime, preventing malformed data from reaching the domain.
  2. **High Asynchronous Concurrency**: Built on `Starlette` and `uvloop`, handling high-throughput concurrent incident reporting, automated SLA polling, and live status streaming with low latency.
  3. **Auto-Generated OpenAPI Documentation**: Automatically generates interactive `/docs` (Swagger UI), allowing evaluators and frontend clients to inspect and test all API contracts.

### C. Database & Storage: **SQLite 3 + SQLAlchemy ORM (Repository Pattern)**
* **Why Appropriate**:
  1. **ACID Transactional Guarantees**: Essential for ITSM where incident audit logs must be immutable and cannot be lost during race conditions or power failures.
  2. **Zero-Configuration Portability**: Runs embedded within the project directory without requiring students, instructors, or evaluators to provision external database services (like PostgreSQL or MySQL servers).
  3. **Repository Pattern Decoupling**: Business logic interacts only with abstract repository interfaces (`IIncidentRepository`, `IUserRepository`), allowing the storage backend to be switched to PostgreSQL or cloud SQL without altering any domain code.

### D. Frontend Presentation: **React 19 + TypeScript + Vite + Vanilla CSS**
* **Why Appropriate**:
  1. **Strongly Typed UI Entities**: TypeScript interfaces (`Incident`, `AuthUser`, `ITService`) directly mirror backend Pydantic models, eliminating runtime type mismatches.
  2. **Zero Bloated CSS Frameworks**: Uses a tailored Vanilla CSS design token system (`index.css`), delivering a professional Zed Black dark mode (`#000000` / `#0c0c0c`) and instant print stylesheets (`@media print`).
  3. **Reactive State Machine Synchronization**: React handles real-time SLA countdown timers, live notification outbox updates, and dynamic role view filtering with high responsiveness.

---

## 3. Comparison with Alternative Architectures

| Architecture Option | Strengths | Weaknesses for this Project | Verdict |
| :--- | :--- | :--- | :--- |
| **Option A (Web App / Templates only)** | Simple, single server. | Clunky full-page reloads, poor live SLA timer syncing, lacks modern asynchronous notification center. | Rejected |
| **Option B (Mobile App)** | Native mobile hardware access. | Cumbersome for IT service managers managing complex matrices, rosters, and printable reports. | Rejected |
| **Option C (Enterprise Full-Stack)** | **Strict layer separation, pure OOPS domain core, real-time reactive UI, print-ready PDF export, live SMTP notification outbox.** | Requires coordinated multi-service development. | **SELECTED** |
| **Option D (Microservices)** | Extreme horizontal scaling. | Over-engineered for course evaluation, adds distributed network latency and deployment complexity. | Rejected |
