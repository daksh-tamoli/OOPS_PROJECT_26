# Intelligent IT Service Management & Incident Resolution System (I-ITSM)
**Course:** CS F213 / MAC F212 Object-Oriented Programming (OOP), Semester-I, 2026–2027  
**Total Marks:** 120 Marks | **Deadline:** November 22, 2026  

---

## 🚀 Overview

The **I-ITSM** platform is an enterprise-grade incident management software system designed to manage the complete lifecycle of IT service disruptions:
$$\text{Report} \longrightarrow \text{Classify} \longrightarrow \text{Prioritize} \longrightarrow \text{Assign} \longrightarrow \text{Investigate} \longrightarrow \text{Resolve} \longrightarrow \text{Verify} \longrightarrow \text{Close}$$

The system is architected around pure **Object-Oriented Programming (OOP) principles**, standard design patterns, and intelligent features including NLP duplicate detection and automated SLA escalation.

---

## 🏛️ Object-Oriented Architecture & Design Patterns

### 1. State Pattern (`backend/app/domain/states/incident_state.py`)
Encapsulates incident lifecycle state transitions and prevents illegal transitions (e.g. `NEW` $\to$ `CLOSED` directly):
* **States:** `NewState` $\to$ `ClassifiedState` $\to$ `AssignedState` $\to$ `AcknowledgedState` $\to$ `InProgressState` $\to$ `ResolvedState` $\to$ `VerifiedState` $\to$ `ClosedState`.
* If user resolution verification fails, transitions back from `RESOLVED` $\to$ `IN_PROGRESS`.

### 2. Strategy Pattern (`backend/app/domain/strategies/`)
* **Technician Assignment Strategies (`IAssignmentStrategy`):**
  - `SkillBasedAssignment`: Matches ticket category against technician certification & skills.
  - `LeastLoadedAssignment`: Selects available technician with minimum active tickets.
  - `RoundRobinAssignment`: Rotates assignments sequentially.
  - `CompositeSmartAssignment`: Weighted scoring combining skills (40%), load (30%), and performance rating (30%).
* **Priority Calculation Strategies (`IPriorityStrategy`):**
  - `MatrixPriorityStrategy`: Standard ITIL Impact $\times$ Urgency matrix with service criticality override.
  - `WeightedCriticalityStrategy`: Mathematical weighted score formula.

### 3. Observer Pattern (`backend/app/domain/observers/`)
* `AuditObserver`: Logs every state transition into an immutable audit history with timestamp, actor, previous state, new state, and description.
* `NotificationObserver`: Dispatches simulated In-App, Email, and Dashboard alerts to reporters and technicians.

### 4. Factory Pattern (`backend/app/domain/factories/incident_factory.py`)
* `IncidentFactory`: Encapsulates object instantiation, auto-calculates priority, determines applicable SLA target, and auto-infers category via NLP keyword classification.

### 5. Repository Pattern (`backend/app/domain/repositories/interfaces.py`)
* Completely decouples business domain entities from database drivers and persistence mechanics.

---

## 🤖 Intelligent Features (Innovation Showcase)

1. **Duplicate Incident Detection (`DuplicateIncidentDetector`):**
   - Combines TF-IDF semantic cosine similarity + Jaccard token overlap + service boosting.
   - Proactively flags similar concurrent incident reports with confidence percentage.
2. **Predictive SLA Risk & Hierarchical Escalation (`AutomaticEscalationEngine`):**
   - Monitors response and resolution deadlines in the background.
   - Evaluates $>70\%$ elapsed time warning and automatically elevates unacknowledged P1 tickets:  
     $\text{Technician} \longrightarrow \text{Team Lead} \longrightarrow \text{System Administrator} \longrightarrow \text{IT Manager}$.
3. **Automated Incident Categorizer (`IntelligentCategorizer`):**
   - Natural language classification inferring categories (`Database`, `Network`, `Authentication`, `Payment`, `Cloud`, etc.).

---

## 🧪 Comprehensive Test Suite (15 Test Cases)

To run the complete automated test suite verifying all course requirements:

```bash
source backend/venv/bin/activate
PYTHONPATH=. pytest backend/tests/test_oops_requirements.py -v
```

### Test Case Coverage Matrix:
| Test ID | Category | Verified Requirement |
| :--- | :--- | :--- |
| **TC-01** | State Pattern | Disallows invalid direct transition `NEW` $\to$ `CLOSED` (`InvalidStateTransitionException`) |
| **TC-02** | State Pattern | Full valid 8-step lifecycle progression (`NEW` through `CLOSED`) |
| **TC-03** | Strategy Pattern | Priority calculation on Tier 1 Critical Service $\to$ `P1` |
| **TC-04** | Strategy Pattern | Skill-based technician allocation matching incident category |
| **TC-05** | Strategy Pattern | Least-loaded technician allocation |
| **TC-06** | Exception Handling| Workload limit reached $\to$ `TechnicianCapacityExceededException` |
| **TC-07** | SLA Management | Strict response (5 min) and resolution (30 min) deadline calculations for P1 |
| **TC-08** | Intelligence | Proactive warning detection when elapsed time exceeds 70% threshold |
| **TC-09** | Escalation | Automatic hierarchical escalation on unacknowledged SLA breach |
| **TC-10** | Intelligence | NLP Duplicate Incident Detection over concurrent payment failures |
| **TC-11** | Observer Pattern | Immutable chronological audit trail recording all lifecycle actions |
| **TC-12** | Authorization | Role-Based Access Control blocking unauthorized operations |
| **TC-13** | Observer Pattern | Notification dispatch on lifecycle events |
| **TC-14** | Intelligence | Automated NLP text categorization inference |
| **TC-15** | State Pattern | Customer rejects resolution $\to$ reverts from `RESOLVED` back to `IN_PROGRESS` |

---

## 🖥️ Running the Application Locally

### 1. Start the Backend API (FastAPI)
```bash
source backend/venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```
* **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

### 2. Start the Frontend Dashboard (React + TypeScript)
```bash
cd frontend
npm run dev
```
* **Web App URL:** [http://localhost:5173](http://localhost:5173)

---

## 📹 Video Demonstration Workflows (15–20 Mins)

1. **Workflow 1: Employee Incident Report & Auto-Assignment**
   - Switch role to **Employee (Alice)**.
   - Click **Report Incident**, enter a payment disruption.
   - Observe automatic P1 priority calculation and assignment to **Devon Vance (DB Specialist)**.
2. **Workflow 2: Technician Investigation & SLA Countdown**
   - Switch role to **Technician (Devon)**.
   - Acknowledge ticket, view live SLA countdown, add investigation notes, and resolve ticket.
   - Switch back to **Employee (Alice)** and verify resolution.
3. **Workflow 3: Duplicate Incident Detection & Automatic Escalation**
   - Switch to **Employee (Alice)**, report another payment incident with similar wording.
   - Observe immediate Intelligent Duplicate Warning alert banner.
   - Switch to **Admin (Sarah)**, click **Run SLA Daemon** to trigger automated hierarchical escalation.
