# I-ITSM FINAL VIDEO DEMONSTRATION SCRIPT (15–18 MINUTES)
**Course:** CS F213 / MAC F212: Object-Oriented Programming (Semester-I, 2026–2027)  
**Project:** Intelligent IT Service Management & Incident Resolution System (I-ITSM)  
**Group Number:** Group 75  
**Team Members:**
- **Daksh Tamoli** (`2024B5A70797H`) — Lead Architect, React 19 UI, Clean Architecture & Admin Dynamic Config
- **Devang Mittal** (`2024B3AD0578H`) — Backend APIs, Security Architecture, 2FA OTP & Custom Exception Handlers
- **Dhruv Vadadoriya** (`2024B5AD0815H`) — Domain Modeling, 8-State Machine (State Pattern), Strategy & Observer Patterns
- **Chaitanya Somani** (`2024B3AD0571H`) — Database Architecture (Repository Pattern), DAG Topology, NLP Duplicate Engine & Test Suite

---

# 🚀 DAKSH'S QUICK-RECORD CHEAT SHEET (STANDALONE DESK GUIDE)
*Use this cheat sheet to record all Daksh's screen segments in under 6 minutes without looking at the rest of the script.*

### Pre-Flight Check (Terminal Commands Before Recording)
1. In Terminal 1: `export PATH=$PATH:/opt/homebrew/bin && npm --prefix frontend run dev` (Opens at `http://localhost:5173`)
2. In Terminal 2: `source backend/venv/bin/activate && uvicorn backend.app.main:app --port 8000 --host 0.0.0.0`
3. Ensure browser is at `http://localhost:5173`. If you need a clean slate at any time, click **"Reset & Reseed DB"** in the bottom sidebar.

---

### Segment D1: Project Introduction & High-Level Architecture (0:00 – 1:30)
- **Screen:** Show `http://localhost:5173` on the login screen.
- **Action:** 
  1. Hover cursor over the **"I-ITSM"** header and the subtitle: *"Intelligent IT Service Management & Incident Resolution System"*.
  2. Point at the role tabs: `ALL`, `EMPLOYEE`, `TECHNICIAN`, `ADMIN`.
  3. Introduce yourself and team members.
- **Daksh Spoken Lines:**
  > "Hello everyone. I am Daksh Tamoli (ID: 2024B5A70797H), lead architect for Group 75. Together with Devang Mittal, Dhruv Vadadoriya, and Chaitanya Somani, we present I-ITSM—an enterprise-grade Intelligent IT Service Management system built for CS F213 / MAC F212.
  > 
  > Our platform manages the complete lifecycle of corporate IT disruptions: from initial reporting and NLP auto-categorization to technician assignment, real-time SLA countdowns, and automated escalation. We built this strictly around Clean Architecture and formal Gang-of-Four design patterns: State, Strategy, Observer, Factory, and Repository. The backend is completely decoupled from FastAPI and SQLAlchemy, and the frontend is powered by React 19 and TypeScript with custom Glassmorphism.
  > 
  > Let me hand over to Devang to explain our authentication and security architecture."

---

### Segment D2: Workflow 1 — Employee Incident Reporting & Auto-Triage (3:00 – 6:15)
- **Screen:** `http://localhost:5173`
- **Actions:**
  1. On the login screen, click the quick-login card for **"Alice Smith (Finance)"** (`alice@company.com`). The password field auto-fills `password123`. Click **"Sign In to Workspace"**.
  2. Show Alice's Employee Dashboard. Point to the blue employee badge at the top right.
  3. Click the orange **"+ Report New Incident"** button at the top of the middle column.
  4. In the modal:
     - **Incident Title:** Type `Stripe checkout gateway 504 timeout on checkout`
     - **Affected Service:** Select `Payment Gateway (TIER_1_CRITICAL)`
     - **Impact:** Select `HIGH`
     - **Urgency:** Select `HIGH`
     - **Category:** Leave empty or set to auto-detect.
     - **Description:** Type `Multiple customers reporting credit card charge failures with HTTP 504 gateway timeout on payment bridge.`
  5. Point cursor at the live badge: note that Priority is calculated as **`P1`** and Category is auto-inferred as **`Payment`**.
  6. Click **"Submit Incident Report"**.
  7. Point at the newly created ticket at the top of the incident list:
     - Priority badge: **`P1`**
     - Status badge: **`ASSIGNED`**
     - Assigned technician: **Devon Vance (DB Specialist)**
  8. Point to the top header bell icon: show the new in-app notification count and click it to reveal *"Ticket Created: Your incident has been logged"*.
- **Daksh Spoken Lines:**
  > "Now I will demonstrate Workflow 1: Incident Reporting and Intelligent Triage from the employee perspective.
  > 
  > I log in as Alice Smith from our Finance department. Notice our role workspace immediately adapts to the employee view. Alice clicks 'Report New Incident'. She enters a critical disruption: 'Stripe checkout gateway 504 timeout on checkout' on our Payment Gateway service, marking Impact as High and Urgency as High.
  > 
  > Behind the scenes, two design patterns fire simultaneously: our **Factory Pattern** (`IncidentFactory`) constructs the incident aggregate, while our **Strategy Pattern** (`MatrixPriorityStrategy`) automatically elevates this Tier-1 critical service issue to **P1-Critical**. Additionally, our NLP engine extracts tokens and auto-classifies the category as Payment.
  > 
  > When Alice clicks 'Submit Incident Report', our **Smart Composite Assignment Strategy** instantly inspects technician skills and live workloads, assigning the ticket to Devon Vance. Simultaneously, our **Observer Pattern** triggers two distinct notification channels: an append-only entry in our immutable audit trail and a live in-app notification in Alice's notification bell.
  > 
  > Next, Dhruv will walk through Workflow 2 from the technician's workstation."

---

### Segment D3: Workflow 3 — Admin Dynamic Config & Service Topology (11:30 – 14:15)
- **Screen:** `http://localhost:5173`
- **Actions:**
  1. In the top-right header, click **"Sign Out"**.
  2. Click the quick-login card for **"Sarah Connor (IT Manager)"** (`admin@itsm.local`). Click **"Sign In to Workspace"**.
  3. Show the red Admin badge in the header.
  4. In the bottom sidebar, click **"Admin Dynamic Config"** (gear icon).
  5. Modal opens:
     - **Tab 1 (IT Services):** Fill in:
       - Name: `Hostel 5 Wi-Fi Cluster`
       - Tier: `BUSINESS_CRITICAL (Tier 2)`
       - Description: `Campus hostel wireless access points and radius authentication`
       - Dependencies: `srv-auth, srv-db`
       - Click **"Register IT Service"**. Show it appear in the Active Service Catalog below!
     - **Tab 2 (Incident Categories):** Click **"Incident Categories"** tab.
       - Category Name: `VoIP Telephony`
       - Keywords: `sip, pbx, trunk, handset, dialer`
       - Click **"Register Category"**. Show it registered under Active NLP Categories!
     - **Tab 3 (SLA Policies):** Click **"SLA Policies"** tab.
       - Select `P1 - Critical`, set Response: `4`, Resolution: `25`.
       - Click **"Save SLA Targets"**. Show updated targets in the grid!
     - **Tab 4 (Assignment Strategy):** Click **"Assignment Strategy"** tab.
       - Click **"Least-Loaded Active Ticket Assignment"**. Point out the active strategy confirmation!
     - Close modal with `X`.
  6. In the left navigation, click **"Service Topology"** (or click **"Interactive Topology Graph"** in Services tab).
  7. Show the interactive DAG:
     - Point out **Core PostgreSQL DB** (`srv-db`), **Payment Gateway** (`srv-payment`), and **SSO** (`srv-auth`).
     - Point out the status pills: Operational, Impacted, Degraded.
     - Hover over the directed dependency edges table below showing upstream/downstream consumer relationships.
  8. Close modal.
  9. In the bottom sidebar, click the red button **"Run SLA Daemon"**.
     - An alert or banner displays the daemon cycle results: Total open tickets evaluated, breaches checked, and overdue escalations!
- **Daksh Spoken Lines:**
  > "Now I will demonstrate Workflow 3: Enterprise Administration and Dynamic Runtime Configuration.
  > 
  > I log in as Sarah Connor, our IT Director. Notice the administrator capabilities unlocked in the workspace. In traditional ticketing tools, changing an SLA or adding a department requires code changes or database migrations. In I-ITSM, everything is dynamically configurable at runtime.
  > 
  > I open 'Admin Dynamic Config'. Under IT Services, I register a new campus service: 'Hostel 5 Wi-Fi Cluster' with upstream dependencies on SSO and Database. It immediately persists to our SQLite database via the **Repository Pattern**. Next, under Incident Categories, I register a dynamic NLP category: 'VoIP Telephony' with custom keyword vectors. Under SLA Policies, I update our P1 resolution target to 25 minutes. Finally, under Assignment Strategy, I switch our live routing strategy from Composite Smart to Least-Loaded—all with zero system restarts.
  > 
  > Next, I open our **Service Dependency Topology Graph**. This directed acyclic graph models failure propagation: when our Core Database experiences high load, dependent services like Payment Gateway automatically flag an `IMPACTED` operational state, giving site reliability engineers immediate root-cause visibility.
  > 
  > Finally, I click 'Run SLA Daemon'. This executes our periodic chronometry cycle: evaluating elapsed time ratios, warning technicians at 70% threshold, and auto-escalating unacknowledged P1 tickets to Level 4 management.
  > 
  > Now Chaitanya will present our analytics, audit trail, and live test suite."

---

# 🎬 FULL 4-MEMBER VIDEO DEMONSTRATION SCRIPT (15–18 MINS)

| [TIMESTAMP] & [SPEAKER] | [ON SCREEN — EXACT ACTION] | [SPEAK] (NATURAL SPOKEN LINES & OOP CALLOUTS) |
| :--- | :--- | :--- |
| **0:00 – 0:45**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Open `http://localhost:5173`<br>• Display clean login screen with I-ITSM logo and quick-login tabs.<br>• Hover cursor over the title: *"Intelligent IT Service Management & Incident Resolution System"*. | "Hello everyone. I am Daksh Tamoli (Student ID: 2024B5A70797H), lead architect for Group 75. Together with Devang Mittal, Dhruv Vadadoriya, and Chaitanya Somani, we are presenting I-ITSM—our course project for CS F213 / MAC F212 Object-Oriented Programming.<br><br>I-ITSM is an enterprise IT service management and incident resolution platform engineered strictly around formal GoF design patterns and Clean Architecture principles. It solves the critical bottlenecks of enterprise support: manual triage delays, subjective priority inflation, technician overload, and lack of verifiable audit trails." |
| **0:45 – 1:30**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Point cursor at the bottom of the login panel: highlight the quick-login roles (`EMPLOYEE`, `TECHNICIAN`, `ADMIN`).<br>• Show the responsive Glassmorphic layout. | "I led the frontend architecture and design system, built using React 19, TypeScript, and custom Vanilla Glassmorphism. On the backend, we implemented a layered Clean Architecture where domain models are completely decoupled from FastAPI and SQLAlchemy, making business logic 100% testable without database or network dependencies.<br><br>I will now hand over to Devang to explain our authentication, security, and exception architecture." |
| **1:30 – 2:15**<br>**Devang Mittal**<br>*(Security Specialist)* | • Click the **"Register New Account"** link at the bottom of the login card.<br>• Enter email: `test.user@company.com`, Full Name: `Test Engineer`, Department: `Engineering`.<br>• In Password field, type `1234` (a weak password).<br>• Click **"Request Verification Code"**.<br>• Point cursor at the red validation message that pops up. | "Hello, I am Devang Mittal (ID: 2024B3AD0578H). I spearheaded the backend REST APIs, authentication infrastructure, and security governance.<br><br>To ensure enterprise compliance, our user authentication enforces a strict 5-point password complexity rule: at least 8 characters, with uppercase, lowercase, numbers, and special symbols. As you can see, when I attempt to register with a weak password, our validation rejects it immediately with an `InvalidUserInputException` before any network or database resources are consumed." |
| **2:15 – 3:00**<br>**Devang Mittal**<br>*(Security Specialist)* | • Clear password and type a compliant strong password: `Admin#2026!Sec`<br>• Click **"Request Verification Code"**.<br>• Green message displays: *"6-digit verification code has been dispatched"*. | "When a compliant password is entered, our **Two-Factor Email OTP Lifecycle** activates. The system generates a cryptographically secure 6-digit code with a 10-minute expiry, dispatches it via real TLS SMTP with a fallback to our persistent Outbox, and salts the password using PBKDF2 with SHA-256.<br><br>Furthermore, we engineered 12 custom domain exceptions—such as `InvalidLoginException`, `UnauthorizedActionException`, and `WorkloadExceededException`—all mapped through FastAPI exception handlers to semantic HTTP status codes.<br><br>Now Daksh will demonstrate Workflow 1 from the Employee workstation." |
| **3:00 – 4:00**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Click **"Return to Sign In"**.<br>• Click the quick-login card for **"Alice Smith (Finance)"** (`alice@company.com`). Password `password123` fills automatically.<br>• Click **"Sign In to Workspace"**.<br>• Land on Alice's Employee Workspace. Point to the blue employee badge in the top-right corner. | "Thank you Devang. I am now logged in as Alice Smith from our Finance department. Notice that our UI dynamically loads the role-specific Employee Workspace, displaying only Alice's reported incidents, her SLA countdowns, and pending technician inquiries.<br><br>Let us walk through **Workflow 1: Incident Reporting, NLP Categorization, and Smart Assignment**." |
| **4:00 – 5:15**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Click orange **"+ Report New Incident"** button.<br>• In the modal, enter:<br>  - Title: `Stripe checkout gateway 504 timeout on checkout`<br>  - Service: `Payment Gateway (TIER_1_CRITICAL)`<br>  - Impact: `HIGH`<br>  - Urgency: `HIGH`<br>  - Description: `Multiple customers reporting credit card charge failures with HTTP 504 gateway timeout on payment bridge.`<br>• Point cursor at the live preview badge showing **P1** and category **Payment**.<br>• Click **"Submit Incident Report"**. | "Alice reports a critical production issue on our Payment Gateway. Behind the scenes, the **Factory Pattern** (`IncidentFactory`) constructs the incident aggregate. It invokes our **Strategy Pattern** (`MatrixPriorityStrategy`), which detects that Payment Gateway is a Tier-1 critical service and automatically elevates the priority to **P1-Critical**.<br><br>Simultaneously, our NLP categorizer scans the description tokens and auto-detects the category as 'Payment' without Alice having to guess." |
| **5:15 – 6:15**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Point at the new ticket `INC-...` created at the top of the list.<br>• Show priority **P1**, status **ASSIGNED**, and assigned technician **Devon Vance (DB Specialist)**.<br>• Click the notification bell in the top-right header: show unread badge `1` and click to view *"Ticket Created: Your incident has been logged"*. | "Upon creation, our **Composite Smart Assignment Strategy** selects Devon Vance because Devon possesses database and transaction skills and has capacity within his workload ceiling. Our **Observer Pattern** concurrently notifies two distinct channels: an immutable audit record is committed to SQLite, and an in-app alert appears in Alice's notification bell.<br><br>I will now hand over to Dhruv to walk through the technician triage workflow." |
| **6:15 – 7:30**<br>**Dhruv Vadadoriya**<br>*(OOP & Domain Architect)* | • Click **"Sign Out"**.<br>• Click quick-login card for **"Devon Vance (DB Specialist)"** (`devon@itsm.local`). Click **"Sign In"**.<br>• Point out the green Technician badge in the header.<br>• Point out the Technician Workload Capacity Meter in the left sidebar: show active load (e.g. `2 / 5 Active Tickets`). | "Hello, I am Dhruv Vadadoriya (ID: 2024B5AD0815H). I designed the core domain models, the 8-state lifecycle machine, and our Strategy and Observer pattern implementations.<br><br>I am now logged in as Devon Vance, our database and cloud support technician. Notice Devon's sidebar shows a live Workload Capacity Meter. Our domain model enforces encapsulation: if Devon were at 5 of 5 tickets, our assignment strategy would bypass him, throwing `WorkloadExceededException` to prevent technician burnout." |
| **7:30 – 8:45**<br>**Dhruv Vadadoriya**<br>*(OOP & Domain Architect)* | • Click the newly assigned P1 payment incident in the middle column.<br>• In the right details pane, point to the live SLA Countdown Timer showing response deadline (5 minutes) and resolution deadline (30 minutes).<br>• Click the blue **"Acknowledge Incident"** button. Status transitions to `ACKNOWLEDGED`. | "Devon selects the new P1 ticket. Notice our **SLA Chronometry Engine** running live countdowns: a 5-minute response SLA and a 30-minute resolution SLA.<br><br>Devon clicks 'Acknowledge Incident'. Under the hood, this executes our **State Pattern**: the ticket transitions from `ASSIGNED` to `ACKNOWLEDGED`, locking in the response time. Notice our `AcknowledgedState` records the response timestamp in the SLA tracker, ensuring the incident cannot breach its response SLA." |
| **8:45 – 9:45**<br>**Dhruv Vadadoriya**<br>*(OOP & Domain Architect)* | • In the incident action bar, click **"Request More Info"**.<br>• Textbox appears: type `Please confirm if failure affects both credit card and UPI transactions.`<br>• Click **"Send Request to Reporter"**.<br>• Point to the new entry in Investigation & Diagnostic Notes. | "To demonstrate our collaboration loop, Devon needs more diagnostic data. He clicks 'Request More Info' and submits a query to Alice. The domain model logs this directly into the ticket's investigation journal and fires an in-app notification to Alice.<br><br>Now let's examine Devon's secret weapon: our Suggested Resolution Recommender." |
| **9:45 – 11:30**<br>**Dhruv Vadadoriya**<br>*(OOP & Domain Architect)* | • Scroll down to the **"Suggested Diagnostic & Resolution Runbooks"** section in the details pane.<br>• Point to the top recommendation: show **Enterprise SOP: Payment Gateway Timeout & Webhook Idempotency Reset**.<br>• Click the green button **"Apply to Resolution"** on the recommendation.<br>• Watch the resolution text area auto-populate with the 4-step remediation plan!<br>• Click the green **"Resolve Incident"** button.<br>• Status badge updates to **`RESOLVED`**! | "Under Suggested Resolutions, our system executes TF-IDF cosine similarity against historically resolved tickets and pairs it with our offline Enterprise SRE Runbook library. The system provides Devon with a verified 4-step remediation procedure: checking upstream gateway bridge, failing over to secondary acquirer bridge, and replaying webhooks with idempotency keys.<br><br>Devon clicks 'Apply to Resolution', which populates his resolution documentation with one click, and clicks 'Resolve Incident'. The State Pattern transitions the ticket to `RESOLVED`, marks the resolution timestamp, and frees Devon's workload slot from 2 down to 1 active ticket.<br><br>Now Daksh will show how the employee verifies and closes the loop." |
| **11:30 – 12:30**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Sign out as Devon, sign back in as **Alice Smith** (`alice@company.com`).<br>• Select the resolved ticket.<br>• Point out the green banner: *"Resolution Submitted by Devon Vance — Please Verify"*.<br>• Click star rating: select **5 Stars**.<br>• In feedback box, type `Payment bridge recovered immediately. Excellent support!`<br>• Click **"Confirm & Close Incident"**.<br>• Ticket transitions to **`VERIFIED`** and then **`CLOSED`**! | "Alice logs back in and inspects the resolved ticket. I-ITSM enforces strict governance: a technician cannot unilaterally close a ticket. Only the original reporting employee or an administrator can verify the resolution.<br><br>Alice confirms checkout is functioning, gives Devon a 5-star rating, and clicks 'Confirm & Close'. The state machine transitions the ticket to `VERIFIED` and then `CLOSED`. If Alice had found that payments were still failing, clicking 'Reject & Reopen' would automatically transition the ticket back to `IN_PROGRESS` and alert Devon." |
| **12:30 – 14:00**<br>**Daksh Tamoli**<br>*(Lead Architect)* | • Sign out as Alice, sign in as **Sarah Connor (IT Manager)** (`admin@itsm.local`).<br>• Click **"Admin Dynamic Config"** in the bottom sidebar.<br>• Show all 4 tabs:<br>  - IT Services: Register new service `Hostel 5 Wi-Fi`<br>  - Categories: Register dynamic category `VoIP Telephony`<br>  - SLA Policies: Edit P1 resolution minutes<br>  - Assignment Strategy: Switch active strategy to `Least-Loaded`.<br>• Close modal.<br>• Open **"Service Topology"** from the left nav. Show the interactive DAG and failure cascade explanation. | "Now we explore **Workflow 3: Administration, Dynamic Configuration, and Service Topology**.<br><br>Logged in as Sarah Connor, our IT Director, I open 'Admin Dynamic Config'. We can dynamically register new IT services, introduce new NLP categories with custom detection keywords, update SLA target thresholds, and toggle our assignment strategy between Composite Smart, Skill-Based, Least-Loaded, and Round-Robin—all stored persistently in SQLite with zero server downtime.<br><br>Next, our **Service Dependency Topology Graph** models our infrastructure as a directed acyclic graph. When a critical database failure occurs, dependent consumer nodes like Payment Gateway cascade to an `IMPACTED` operational health state, preventing duplicate tickets and identifying root causes in seconds." |
| **14:00 – 15:30**<br>**Chaitanya Somani**<br>*(Database & QA Lead)* | • In left sidebar, click the red **"Run SLA Daemon"** button.<br>• Show banner confirming SLA cycle evaluated open tickets.<br>• In left sidebar, click **"Operations Analytics"**.<br>• Point out the KPI metrics cards: Total Incidents, Active Tickets, Critical P1, Breached SLA, and Resolution Rate.<br>• Scroll through Technician Workload Distribution table and Service Breakdown chart. | "Hello, I am Chaitanya Somani (ID: 2024B3AD0571H). I led the database persistence layer using the Repository Pattern, our duplicate correlation engine, and automated testing.<br><br>As Daksh just demonstrated, our background SLA Escalation Daemon runs periodic chronometry cycles. If any ticket approaches 70% of its SLA deadline, it triggers proactive warnings; if a P1 ticket breaches unacknowledged, it auto-escalates to Level 4 management.<br><br>On our Analytics Dashboard, management has full visibility into technician workloads, SLA compliance rates, and incident densities per service. Notice our multi-criteria search filter allows triaging by status, priority, category, service, and free-text queries simultaneously." |
| **15:30 – 17:00**<br>**Chaitanya Somani**<br>*(Database & QA Lead)* | • Select any ticket and click **"Audit Trail"** tab.<br>• Show the chronological timeline: every action, actor name, role, timestamp, and state delta from `NEW` to `CLOSED`.<br>• Switch to the terminal window.<br>• Run: `PYTHONPATH=. backend/venv/bin/pytest backend/tests -v`<br>• Show all 25 automated unit tests passing in ~0.7 seconds with green checkmarks! | "Every single transition and administrative override is permanently recorded by our `AuditObserver` in an immutable, append-only audit trail in SQLite. It captures actor ID, action name, previous state, new state, and exact UTC timestamp, fulfilling ISO-20000 and ITIL compliance.<br><br>To validate our system under academic scrutiny, we developed a comprehensive test suite of 25 automated pytest test cases covering State transitions, Strategy algorithms, Observer dispatch, Capacity exceptions, Duplicate NLP detection, and Topology cascades.<br><br>As you can see in the terminal, all 25 tests pass in under one second with 100% success rate." |
| **17:00 – 18:00**<br>**Daksh Tamoli**<br>*(Lead Architect & Closing)* | • Switch back to the web application dashboard.<br>• All 4 team members on screen / camera for final sign-off. | "In summary, Group 75 has delivered a complete, robust, full-stack IT Service Management solution. By grounding I-ITSM in formal Gang-of-Four design patterns and Clean Architecture, we have proven that object-oriented principles directly enable enterprise resilience, maintainability, and intelligent automation.<br><br>Thank you to our course instructors and evaluators. We welcome your questions." |

---

## 📋 VERIFIED DEMO LOGIN CREDENTIALS CHEAT SHEET
All demo accounts are pre-seeded in `backend/itsm.db` and ready for instant login with password **`password123`**:

| Persona | Role | Email | Password | Key Strengths & Modules to Show |
| :--- | :--- | :--- | :--- | :--- |
| **Sarah Connor** | `ADMIN` | `admin@itsm.local` | `password123` | Dynamic Admin Config, SLA Policies, Topology DAG, Run SLA Daemon |
| **Alice Smith** | `EMPLOYEE` | `alice@company.com` | `password123` | Report P1 Incident, View Bell Notifications, Verify Fix, 5-Star Rating |
| **John Doe** | `EMPLOYEE` | `john@company.com` | `password123` | Report Database issues, Respond to Info Requests |
| **Devon Vance** | `TECHNICIAN` | `devon@itsm.local` | `password123` | Database/SQL skills, Workload Meter (2/5), Apply SRE Runbooks, Resolve Ticket |
| **Maya Lin** | `TECHNICIAN` | `maya@itsm.local` | `password123` | Network/Cloud skills, Capacity (1/5), Live SLA countdown tracking |
| **Liam Gallagher**| `TECHNICIAN` | `liam@itsm.local` | `password123` | Application/Auth skills, SSO Triage |
| **Marcus Reid** | `TECHNICIAN` | `marcus@itsm.local` | `password123` | Infrastructure/SysAdmin skills, Hardware failure remediation |
