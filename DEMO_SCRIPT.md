# I-ITSM Video Demonstration Script (15–20 Minutes)
**Course:** CS F213 / MAC F212 Object-Oriented Programming (OOP)  
**Project:** Intelligent IT Service Management & Incident Resolution System (I-ITSM)  
**Group Number:** Group 75  
**Team Roster:**
- **Daksh Tamoli** (`2024B5A70797H`) — Lead Architect & Full-Stack Engineer
- **Devang Mittal** (`2024B3AD0578H`) — Backend APIs & Security Specialist
- **Dhruv Vadadoriya** (`2024B5AD0815H`) — Domain Modeling & OOP Architect
- **Chaitanya Somani** (`2024B3AD0571H`) — Database, Intelligence & QA Lead

---

## 🎬 Pre-Recording Checklist
1. **Backend Server Running:** `http://localhost:8000` (FastAPI Swagger at `/docs`).
2. **Frontend Running:** `http://localhost:5173` (Open in Google Chrome or Arc, full screen, 100% zoom).
3. **Terminal Window Ready:** Split or second window cd'd into `/Users/dakshtamoli/Documents/OOPS Project` with virtualenv activated.
4. **Database State Clean:** Pre-seeded with sample technicians (Devon Vance, Marcus Reid), services, and SLA policies.
5. **Screen Recording:** Record at 1080p, 60fps or 30fps with system audio + microphone enabled.

---

## ⏱️ Timeline & Scene Breakdown

```mermaid
gantt
    title Video Demo Timeline (Total: 19:30)
    dateFormat  m:s
    axisFormat  %M:%S
    section Scene 1
    Intro, Architecture & Security      :s1, 00:00, 03:00
    section Scene 2
    Domain OOP Patterns & Lifecycle     :s2, 03:00, 06:30
    section Scene 3
    Employee Flow & Duplicate NLP       :s3, 06:30, 09:30
    section Scene 4
    Technician Triage & AI Runbooks     :s4, 09:30, 12:30
    section Scene 5
    Dual Notifications & Verification   :s5, 12:30, 14:30
    section Scene 6
    Service Topology & Dynamic Admin    :s6, 14:30, 17:30
    section Scene 7
    25-Case Pytest Suite & Defense      :s7, 17:30, 19:30
```

---

## 🎙️ Verbatim Speaking Script & Stage Directions

---

### SCENE 1: Introduction, Architecture & Security (0:00 – 3:00)
**Primary Speakers:** Daksh Tamoli & Devang Mittal  
**Screen Display:** Landing page / Login modal at `http://localhost:5173` $\to$ Swagger Docs at `http://localhost:8000/docs`

#### [0:00 – 0:45] Project Welcome & Roster
**[ACTION: Show the I-ITSM Dashboard landing page with Group 75 header visible]**

> **DAKSH:**  
> "Hello everyone, and welcome to the project demonstration of **I-ITSM — the Intelligent IT Service Management and Incident Resolution System**, developed for **CS F213 / MAC F212 Object-Oriented Programming** by **Group 75**.  
> 
> My name is **Daksh Tamoli (2024B5A70797H)**, Lead Architect and Full-Stack Engineer for this project. With me today are my co-engineers:  
> - **Devang Mittal (2024B3AD0578H)**, who spearheaded our Backend APIs and Security Architecture;  
> - **Dhruv Vadadoriya (2024B5AD0815H)**, who designed our core Domain Object Model and GoF Design Patterns; and  
> - **Chaitanya Somani (2024B3AD0571H)**, our Database, Machine Intelligence, and QA Lead.  
> 
> Modern enterprise operations face complex IT disruptions across databases, payment bridges, and network relays. I-ITSM was engineered from the ground up using **Clean Architecture** and strict **Object-Oriented design principles** to automate the entire incident lifecycle from detection to resolution."

#### [0:45 – 1:45] Clean Architecture & Layer Decoupling
**[ACTION: Switch to IDE or architecture diagram in PROJECT_REPORT.md Section 3]**

> **DEVANG:**  
> "Thank you, Daksh. Looking at our architectural blueprint, I-ITSM strictly separates concerns across four distinct tiers:  
> 1. At the core is the **Domain Layer**, containing pure business entities—`Incident`, `ITService`, `Technician`, and `SLAPolicy`—completely decoupled from external frameworks and database drivers.  
> 2. The **Application Service Layer** orchestrates business transactions using the Repository and Factory patterns.  
> 3. The **Infrastructure Layer** implements persistence via SQLAlchemy 2.0 and SQLite, alongside real SMTP email dispatch.  
> 4. And finally, the **API Layer** exposes asynchronous FastAPI endpoints with OpenAPI 3.1 documentation, backed by a modern React 19 and TypeScript frontend."

#### [1:45 – 3:00] Security Architecture, 5-Point Password Complexity & 2FA Email OTP
**[ACTION: Bring up the Registration Modal on the web app UI]**

> **DEVANG:**  
> "Security is a foundational pillar of I-ITSM:  
> - **Zero Plaintext Storage:** Passwords are never stored raw. We implement **PBKDF2 with SHA-256** key derivation and unique per-user cryptographically random salts.  
> - **5-Point Password Complexity:** As you can see in the registration dialog, our client and backend enforce: minimum 8 characters, at least one uppercase letter, one lowercase letter, one numeric digit, and one special symbol. If any criteria fail, the registration is rejected with custom validation feedback.  
> - **2-Factor Email OTP Lifecycle:** When a new user registers, our system generates a cryptographically secure 6-digit numeric OTP with a 10-minute TTL. The OTP is dispatched via SMTP over TLS to the user's registered corporate email, and user creation is blocked until the matching OTP is submitted.  
> - Now, I'll hand over to Dhruv to walk us through the object-oriented design patterns that power our domain model."

---

### SCENE 2: Domain OOP Patterns & Lifecycle Machine (3:00 – 6:30)
**Primary Speaker:** Dhruv Vadadoriya  
**Screen Display:** UML Class Diagram in report or code editor opening `backend/app/domain/states/incident_state.py`

#### [3:00 – 4:30] State Pattern: 8-State Lifecycle Machine & Transition Guards
**[ACTION: Open `backend/app/domain/states/incident_state.py` in VS Code]**

> **DHRUV:**  
> "Thank you, Devang. The core requirement of this project is modeling a rigorous, tamper-resistant incident lifecycle. Instead of using messy, fragile `if-else` conditionals, we implemented the classic **GoF State Pattern**.  
> 
> As you can see in `incident_state.py`, we define an abstract base class `IncidentState` with transition methods: `classify()`, `assign()`, `acknowledge()`, `investigate()`, `resolve()`, `verify()`, and `close()`.  
> 
> We implement **eight concrete state classes**:  
> `NewState`, `ClassifiedState`, `AssignedState`, `AcknowledgedState`, `InProgressState`, `ResolvedState`, `VerifiedState`, and `ClosedState`.  
> 
> Every state encapsulates its own validation guards:  
> - If an unauthorized user attempts an illegal transition—for example, trying to jump directly from `NEW` to `CLOSED`—the active state raises our custom `InvalidStateTransitionException`, and the ticket remains unchanged.  
> - Furthermore, if an employee rejects a technician's resolution during the verification stage, `ResolvedState.verify(confirmed=False)` transitions the incident cleanly back from `RESOLVED` to `IN_PROGRESS`."

#### [4:30 – 5:30] Strategy Pattern: Dynamic Assignment & Priority Matrices
**[ACTION: Switch to `backend/app/domain/strategies/` in the code editor]**

> **DHRUV:**  
> "Next, we implemented the **Strategy Pattern** across two critical business dimensions:  
> 1. **Technician Assignment Strategies:** Through the `IAssignmentStrategy` interface, we support multiple interchangeable routing algorithms:  
>    - `SkillBasedAssignment`, matching incident categories to technician skillsets;  
>    - `LeastLoadedAssignment`, balancing active technician ticket capacity;  
>    - `RoundRobinAssignment`, for equitable sequential distribution; and  
>    - `CompositeSmartAssignment`, our flagship heuristic weighting skills (40%), workload capacity (30%), and performance rating (30%).  
> 
> 2. **Priority Calculation Strategies:** Using `IPriorityStrategy`, we provide:  
>    - `MatrixPriorityStrategy`, which maps ITIL Impact and Urgency levels with an automatic Tier-1 Critical Service override to guaranteed `P1`; and  
>    - `WeightedCriticalityStrategy`, calculating a mathematical float score."

#### [5:30 – 6:30] Factory & Observer Patterns
**[ACTION: Briefly show `incident_factory.py` and `backend/app/domain/observers/concrete.py`]**

> **DHRUV:**  
> "To complete our design pattern suite:  
> - Our **Factory Pattern** (`IncidentFactory`) encapsulates complex object creation. It takes raw user inputs, invokes our NLP categorizer to infer missing categories, applies the active priority strategy, computes response and resolution deadlines from the active SLA policy, and binds initial audit state.  
> - Our **Observer Pattern** implements decoupled event notification. The `Incident` entity acts as the Subject. Whenever its state changes, it notifies registered observers:  
>   - `AuditObserver`, which writes immutable audit log entries;  
>   - `NotificationObserver`, which dispatches multi-part HTML emails via SMTP; and  
>   - `InAppNotificationObserver`, which delivers live alerts to the frontend bell notification center.  
> 
> Now, Chaitanya and Daksh will demonstrate these patterns live in the running application."

---

### SCENE 3: Employee Incident Reporting & NLP Duplicate Detection (6:30 – 9:30)
**Primary Speakers:** Chaitanya Somani & Daksh Tamoli  
**Screen Display:** React UI logged in as **Alice Chen (Employee)** at `http://localhost:5173`

#### [6:30 – 8:00] Reporting Flow & Automatic Categorization
**[ACTION: Daksh selects 'Employee (Alice Chen)' from role dropdown, clicks '+ Report Incident']**

> **DAKSH:**  
> "Now let's see the application in action. I am logged in as **Alice Chen**, a corporate employee in the Finance department.  
> 
> I'll click **'Report Incident'**. Notice that as an employee, the interface gives me a clean, intuitive form without technical jargon. Let's simulate a critical infrastructure outage.  
> 
> In the title, I'll type:  
> *'Stripe payment gateway deadlocked — checkout 504 errors'*  
> And in the description:  
> *'Campus store and tuition debit payments failing across all terminals with postgres connection timeouts.'*  
> 
> Notice that I'll leave the Category set to **'Auto-Detect'** and select our **Payment Processing Bridge** service."

**[ACTION: Click 'Submit Incident Report'. Show the created incident card appearing at the top of the list]**

> **CHAITANYA:**  
> "Notice what happened the moment Daksh submitted the form:  
> 1. Our **Intelligent NLP Categorizer** extracted diagnostic keywords (`stripe`, `payment`, `checkout`) and automatically classified the ticket as **`Payment`**.  
> 2. Our **Priority Matrix Strategy** recognized that the **Payment Processing Bridge** is a **Tier-1 Critical Service**. Even if the user selected moderate urgency, the Tier-1 policy triggered an immediate elevation to **`P1 - Critical`**.  
> 3. Our **SLA Engine** bound strict enterprise deadlines: a **5-minute response target** and a **30-minute resolution target**, starting our real-time countdown timer."

#### [8:00 – 9:30] NLP Duplicate Incident Detection
**[ACTION: Click '+ Report Incident' again to report a second similar ticket]**

> **DAKSH:**  
> "Now, let's test our duplicate incident intelligence. Imagine another employee across campus experiences payment issues at the same time and opens a new ticket.  
> 
> I'll enter:  
> Title: *'Payment card checkout unavailable'*  
> Description: *'Unable to process debit card checkout transactions in payment application.'*"

**[ACTION: Show the dynamic yellow warning banner appearing automatically on screen]**

> **CHAITANYA:**  
> "Look at the screen right now! Before the user even submits, or right upon creation, our **`DuplicateIncidentDetector`** activates.  
> 
> Behind the scenes, we compute a composite similarity score:  
> - **TF-IDF Semantic Vectorization** with Cosine Similarity;  
> - **Jaccard Token Overlap** across stemmed technical terms; and  
> - A **Contextual Service Boost** of +0.20 when incidents reference the same IT service.  
> 
> Because the calculated similarity score exceeds our **0.35 threshold** (scoring over 0.40), the UI renders this prominent alert banner linking directly to Parent Ticket `INC-8910`. This prevents technician fatigue and duplicate triage efforts."

---

### SCENE 4: Technician Triage, SLA Timer & AI SRE Runbooks (9:30 – 12:30)
**Primary Speakers:** Dhruv Vadadoriya & Devang Mittal  
**Screen Display:** Switch role dropdown to **Devon Vance (Technician)**

#### [9:30 – 10:45] Technician Workload & Acknowledgment
**[ACTION: Switch role dropdown to 'Devon Vance (Technician)']**

> **DHRUV:**  
> "Now, let's switch our persona to **Devon Vance**, our Database and Cloud Ops specialist.  
> 
> Look at the left sidebar: Devon has a real-time **Workload Capacity Meter** showing his active load (e.g., 2/5 tickets). Our system enforces a strict capacity ceiling of 5 active tickets per technician; if an assignment would exceed this limit, the system raises `TechnicianCapacityExceededException`.  
> 
> Because our active assignment strategy is **Skill-Based Composite**, the P1 payment database outage was automatically assigned to Devon based on his verified PostgreSQL skills.  
> 
> I will now open the ticket and click **'Acknowledge'**."

**[ACTION: Click 'Acknowledge'. Show status badge turning blue (ACKNOWLEDGED) and response timer locking]**

> **DHRUV:**  
> "The State Pattern advances the incident from `ASSIGNED` to `ACKNOWLEDGED`. Crucially, this action halts the response SLA timer, satisfying compliance before the 5-minute breach threshold."

#### [10:45 – 12:30] Requesting Info & AI SRE Runbook Resolution
**[ACTION: Click 'Request Info', enter 'Please upload postgres server logs', submit. Then show the SRE Runbook tab]**

> **DEVANG:**  
> "Notice two key enterprise features here:  
> 1. **Bi-Directional Communication:** Devon can click **'Request Info'** to ask Alice for diagnostic server logs. The State Pattern records this dialogue in the audit history.  
> 2. **AI-Assisted SRE Runbooks & Historical Resolution:** Look at the **'Suggested Fixes'** panel. Our resolution recommender vectorizes past closed incidents and curated ITIL runbooks. For database pool starvation, it suggests:  
>    *'Increase max_connections in postgresql.conf to 300 and recycle PgBouncer pool.'*  
> 
> Devon can click **'Use This Resolution'**! The system automatically advances the incident from `ACKNOWLEDGED` to `IN_PROGRESS`, pre-fills the resolution textarea, and smooth-scrolls right into the action view. Devon adds his final verification notes and clicks **'Submit Resolution'**!"

**[ACTION: Click 'Use This Resolution', show green toast, click 'Resolve Ticket']**

> **DEVANG:**  
> "The ticket is now marked `RESOLVED`. An event is published to all observers, triggering both notification channels."

---

### SCENE 5: Dual Notification Channels & Verification (12:30 – 14:30)
**Primary Speakers:** Devang Mittal & Daksh Tamoli  
**Screen Display:** Header Notification Bell $\to$ Terminal/Outbox $\to$ Switch to Alice Chen

#### [12:30 – 13:30] Dual Channels: Real SMTP Email + In-App Bell Center
**[ACTION: Click the notification bell icon in the top navigation bar]**

> **DEVANG:**  
> "One of our core rubric deliverables is supporting **two distinct notification channels**:  
> 1. **Channel 1 (In-App Notification Center):** Notice the animated bell icon in the top header. When I click it, a glassmorphic popover displays our unread alerts. We see our high-severity alert: *'Incident P1 Resolved by Devon Vance'*. Clicking the alert marks it read and immediately navigates to the ticket. Clicking outside smoothly dismisses the popover.  
> 2. **Channel 2 (Enterprise SMTP Email Delivery):** In `backend/app/infrastructure/email/service.py`, our system connects via TLS to a real SMTP server. If credentials are not configured, it gracefully falls back to our persistent outbox table (`outbox_emails`), guaranteeing zero lost messages. Each email is formatted with professional multi-part HTML, displaying incident IDs, priority badges, and direct links."

#### [13:30 – 14:30] Customer Verification & 5-Star Feedback Loop
**[ACTION: Switch role back to 'Alice Chen (Employee)', open resolved ticket]**

> **DAKSH:**  
> "Now we switch back to **Alice Chen**, the original reporter.  
> 
> Under ITIL guidelines, a technician cannot unilaterally close a ticket—the affected user must verify that the service is truly restored.  
> 
> Alice has two choices:  
> - If the issue persists, she clicks **'Reject / Reopen'**, which triggers `IncidentState.verify(confirmed=False)` and reverts the state back to `IN_PROGRESS`.  
> - If the fix succeeded, she selects her **5-Star Rating**, types *'Payment gateway confirmed operational, thank you!'*, and clicks **'Confirm Resolution'**."

**[ACTION: Select 5 stars, type note, click 'Confirm Resolution'. Show ticket transitioning to VERIFIED then CLOSED]**

> **DAKSH:**  
> "The incident transitions to `VERIFIED` and then `CLOSED`. An immutable audit record is committed, recording Alice's satisfaction score in our operations analytics."

---

### SCENE 6: Service Dependency Topology & Admin Dynamic Config (14:30 – 17:30)
**Primary Speakers:** Chaitanya Somani & Daksh Tamoli  
**Screen Display:** Switch role to **Sarah Connor (Admin)** $\to$ 'Service Topology' view $\to$ 'Admin Switchboard' modal

#### [14:30 – 16:00] Service Dependency Graph & Cascade Failure Analysis
**[ACTION: Switch role to 'Sarah Connor (Admin)', click 'Service Analysis & Topology' tab]**

> **CHAITANYA:**  
> "Now let's examine our advanced innovation features. I am logged in as **Sarah Connor**, our IT Systems Administrator.  
> 
> I'll open the **Service Analysis & Topology View**. Here we see our services modeled as a **Directed Acyclic Graph (DAG)**. Notice that:  
> - `Payment Processing Bridge` depends on `Core Database Cluster`; and  
> - `Internal Mail Relay` also depends on `Core Database Cluster`.  
> 
> What happens if our database experiences a catastrophic outage? Let's simulate a critical P1 outage on `Core Database Cluster`."

**[ACTION: Click on 'Core Database Cluster', toggle status to 'OUTAGE / P1 IMPACT']**

> **CHAITANYA:**  
> "Watch the graph update in real time! Our graph traversal algorithm performs a breadth-first search across downstream dependencies.  
> 
> Notice how the **Payment Processing Bridge** automatically transitions from `OPERATIONAL` to **`IMPACTED`**, marked with an amber warning border and tooltip: *'Cascade warning: Upstream dependency Core Database Cluster is under P1 outage'*. This gives leadership instant operational situational awareness."

#### [16:00 – 17:30] Dynamic Admin Configuration Switchboard
**[ACTION: Daksh clicks 'Admin Switchboard' button in top navbar]**

> **DAKSH:**  
> "Next is our **Admin Dynamic Configuration Switchboard**. The rubric mandates that administrators must be able to modify operational policies at runtime without touching source code or restarting servers.  
> 
> From this unified control panel, Sarah can:  
> 1. **Add a New IT Service:** Let's add *'Campus Wi-Fi Cluster'* as a Tier-2 service with dependencies. Click Save—the service is instantly available across the catalog!  
> 2. **Register Incident Categories:** Add *'Security Breach'* with diagnostic NLP keywords like *'phishing, malware, ddos'*.  
> 3. **Tune Dynamic SLA Policies:** Adjust P1 response thresholds from 5 minutes to 3 minutes on the fly.  
> 4. **Switch Assignment Strategy:** We can toggle the active technician assignment strategy between `Composite Smart`, `Least Loaded`, `Skill Based`, and `Round Robin` with a single click.  
> 
> Every change is committed to SQLite and instantly reflected across all active sessions."

---

### SCENE 7: Automated Test Suite Execution & Academic Defense (17:30 – 20:00)
**Primary Speakers:** Chaitanya Somani & All Team Members  
**Screen Display:** Terminal running pytest $\to$ Operations Analytics / Export PDF $\to$ Final Video Close

#### [17:30 – 18:45] Execution of Complete 25-Case Pytest Suite
**[ACTION: Switch to full-screen terminal window]**

> **CHAITANYA:**  
> "To prove that our architecture adheres to every single rubric requirement and edge case, we engineered a comprehensive **25-case automated Pytest suite** in `backend/tests/test_oops_requirements.py`.  
> 
> Let's run the full suite live in verbose mode."

**[ACTION: Run command in terminal: `PYTHONPATH=. backend/venv/bin/pytest backend/tests/test_oops_requirements.py -v`]**

> **CHAITANYA:**  
> "Watch the tests execute:  
> - **TC-01 and TC-02** verify the State Pattern and illegal transition prevention;  
> - **TC-03 to TC-05** validate our Priority and Assignment Strategy algorithms;  
> - **TC-06** verifies `TechnicianCapacityExceededException`;  
> - **TC-07 to TC-09** validate the SLA engine, risk detection, and hierarchical auto-escalation;  
> - **TC-10** verifies NLP duplicate detection with cosine similarity $\ge 0.35$;  
> - **TC-11 and TC-13** verify the Observer Pattern and immutable audit logging;  
> - **TC-12** validates RBAC security;  
> - **TC-16 to TC-21** verify authentication, password strength, and 2FA email OTPs;  
> - **TC-22 and TC-23** test our SRE runbook recommender and DAG topology cascade;  
> - **TC-24** verifies all **12 custom domain exceptions** inheriting from `DomainException`; and  
> - **TC-25** validates our dual notification channels.  
> 
> **Result: 25 passed in under 1 second! 100% pass rate!**"

#### [18:45 – 20:00] Executive Analytics, PDF Export & Final Defense Remarks
**[ACTION: Switch back to browser, open 'Operations Analytics' tab, click 'Export PDF Report']**

> **DAKSH:**  
> "As our final feature, Sarah can open the **Operations Analytics Dashboard** to review real-time MTTR (Mean Time to Resolution), SLA compliance rates, and technician load distribution. Clicking **'Export PDF Report'** formats a publication-ready summary for executive reporting.  
> 
> To summarize our academic defense:  
> - **Object-Oriented Integrity:** I-ITSM proves how the State, Strategy, Observer, Factory, and Repository patterns create a resilient, decoupled enterprise system.  
> - **Robustness:** Custom exception hierarchies, 2FA security, and immutable audit logs ensure complete traceability.  
> - **Innovation:** Machine intelligence, NLP duplicate detection, and graph cascade topology elevate I-ITSM into a platform ready for real campus IT adoption.  
> 
> On behalf of **Group 75**—Devang Mittal, Dhruv Vadadoriya, Chaitanya Somani, and myself, Daksh Tamoli—thank you for your time and evaluation!"

**[ACTION: Show final team slide or GitHub repository page, wave, and fade to black]**

---

## 📋 Quick Speaker Cue Sheet (Keep on Second Screen)

| Member | Primary Modules & Topics | Key File References | Target Time |
| :--- | :--- | :--- | :--- |
| **Daksh Tamoli** | • Intro & Group 75 Welcome<br>• Employee Reporting UI<br>• Verification & Rating Loop<br>• Dynamic Admin Switchboard<br>• Concluding Remarks | `frontend/src/App.tsx`<br>`PROJECT_REPORT.md` | 0:00 – 0:45<br>6:30 – 8:00<br>13:30 – 14:30<br>16:00 – 17:30<br>18:45 – 20:00 |
| **Devang Mittal** | • Clean Architecture Layers<br>• Security, PBKDF2 & 2FA Email OTP<br>• Bi-Directional Dialogue<br>• Dual Notification Channels (SMTP + In-App) | `backend/app/main.py`<br>`backend/app/infrastructure/email/service.py`<br>`backend/app/domain/exceptions.py` | 0:45 – 3:00<br>10:45 – 12:30<br>12:30 – 13:30 |
| **Dhruv Vadadoriya**| • State Pattern (8 States, guards, rejection)<br>• Strategy Pattern (4 Assignment, 2 Priority)<br>• Factory & Observer Patterns<br>• Technician Workload & Triage | `backend/app/domain/states/incident_state.py`<br>`backend/app/domain/strategies/`<br>`backend/app/domain/factories/`<br>`backend/app/domain/observers/` | 3:00 – 6:30<br>9:30 – 10:45 |
| **Chaitanya Somani**| • NLP Categorization & Priority Matrix<br>• NLP Duplicate Detection (TF-IDF + Cosine)<br>• Service Dependency Topology (DAG)<br>• 25-Case Pytest Automated Test Suite | `backend/app/domain/intelligence/duplicate_detector.py`<br>`backend/app/domain/models/service.py`<br>`backend/tests/test_oops_requirements.py` | 8:00 – 9:30<br>14:30 – 16:00<br>17:30 – 18:45 |
