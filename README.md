# SMART_VOTING_USING_FACE_RECOGNITION

An end-to-end biometric electronic voting system built with **Streamlit**, **DeepFace (FaceNet512)**, and **SQLite**. The platform provides contactless voter registration, real-time facial verification at the polling booth, duplicate voting prevention via atomic SQL transactions, and an administrative portal for live telemetrics and directory management.

---

## Technical Highlights & Architecture

- **Deep Metric Learning:** Leverages **FaceNet512** deep embeddings (`D = 512`) with cosine distance matching (`threshold ≤ 0.40`) for facial verification, replacing heuristic detectors with pose- and illumination-invariant representations.
- **Cryptographic Identity Protection:** Enrolled voter identification numbers are salted and digested using **SHA-512**:

  `VoterHash = SHA512(CleanID + Salt)`

  ensuring non-reversible masking across database tables.
- **ACID Transaction Integrity:** Prevents double-voting using database-level uniqueness constraints and atomic verification flags (`has_voted = 1`) within SQLite transactions.
- **Reactive Single-Page Architecture:** Built entirely on Streamlit, eliminating blocking multi-process orchestration, desktop windowing dependencies, and UI-freezing thread locks.

### System Architecture

```
[Camera Capture]
        │
        ▼
[Facial Detection & Alignment]
        │
        ▼
[512D Embedding Extraction - FaceNet512]
        │
        ▼
[1:N Cosine Distance Verification (≤ 0.40)]
        │
        ▼
[Salted SHA-512 Verification]
        │
        ▼
[Atomic SQL Transaction Ledger]
```
### Project Structure
```
SMART_VOTING_USING_FACE_RECOGNITION/
├── app.py                   # Streamlit web interface & session router
├── core/
│   ├── __init__.py          # Package declaration
│   ├── db.py                # SQLite schema, voter operations & SHA-512 hashing
│   └── face_engine.py       # FaceNet512 embedding inference & cosine verification
├── requirements.txt         # Project dependencies
└── README.md                # Technical documentation

```

| Category                            | Technologies                                                |
| ----------------------------------- | ----------------------------------------------------------- |
| **Frontend & Dashboard**            | Streamlit, Pandas                                           |
| **Computer Vision & Deep Learning** | DeepFace, FaceNet512, OpenCV Headless, TensorFlow / Keras   |
| **Database & Security**             | SQLite3, Python Standard Library `hashlib` (Salted SHA-512) |
| **Numerical Computing**             | NumPy                                                       |


Installation & Setup
1. Clone the Repository
git clone https://github.com/<your-username>/SMART_VOTING_USING_FACE_RECOGNITION.git
cd SMART_VOTING_USING_FACE_RECOGNITION

2. Set Up a Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Linux / macOS
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Launch the Application
streamlit run app.py


###Application Modules
1. Telemetrics Overview
Displays real-time turnout metrics:
Registered Voters
Total Ballots Cast
Turnout %
Visualizes system architecture and verification pipeline specifications.

2. Voter Enrollment
Captures voter details:
Unique Identification Number
Full Name
Mobile Number
Extracts a 512-dimensional facial embedding vector using FaceNet512.
Commits the record to SQLite with an auto-generated salted SHA-512 voter hash.

3. Electronic Balloting Booth
Step 1 — Biometric Verification
Computes a 512D probe vector from the camera feed.
Evaluates the minimum cosine distance against all registered citizen profiles.
Upon successful verification (distance ≤ 0.40), unlocks candidate balloting options.
Step 2 — Ballot Submission
Upon successful biometric verification, the candidate ballot options are unlocked.
The vote is written and has_voted = 1 is updated within a single transaction.
Subsequent voting attempts for the same voter are rejected.

4. Administrative Operations & Governance
Authenticated via administrative passcode.
Live Election Tallies:
Bar chart distribution
Vote tables
One-click summary CSV export
Voter Registry Management
Export Directory: Download the full voter roll containing:
Unique ID
Full Name
Mobile Number
Voted Status
Registration Timestamp
De-register / Delete Records: Administrative purge functionality to delete voter records by entering their ID or selecting from the enrolled registry list.
Security & Privacy Considerations
Deterministic Masking: Citizen identification numbers are never matched in plain text during polling operations; comparisons rely solely on salted SHA-512 digests.
Template Protection: Biometric templates are stored as floating-point coordinate arrays rather than raw image files, preventing facial reconstruction from stored assets.
Relational Integrity: Foreign key constraints (ON DELETE CASCADE) maintain consistency across voter registries and cast ballot audit tables.
Duplicate Voting Prevention: Atomic database transactions ensure that ballot submission and the corresponding has_voted = 1 update are handled together.
###Verification Workflow
```
                    ┌─────────────────────┐
                    │   Voter Enrollment  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ FaceNet512 Embedding│
                    │       (512D)        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Salted SHA-512 ID  │
                    │       Hashing       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    SQLite Voter     │
                    │      Registry       │
                    └──────────┬──────────┘
                               │
                         Polling Booth
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Camera Capture   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Face Verification   │
                    │ Cosine Distance ≤.40│
                    └──────────┬──────────┘
                               │
                         Match Successful
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Candidate       │
                    │       Ballot        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Atomic SQL Vote   │
                    │   has_voted = 1     │
                    └─────────────────────┘

```









