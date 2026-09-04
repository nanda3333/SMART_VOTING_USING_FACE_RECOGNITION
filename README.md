# SMART_VOTING_USING_FACE_RECOGNITION

An end-to-end biometric electronic voting system built with **Streamlit**, **DeepFace (FaceNet512)**, and **SQLite**. The platform provides contactless voter registration, real-time facial verification at the polling booth, duplicate voting prevention via atomic SQL transactions, and an administrative portal for live telemetry and directory management.

---

## Technical Highlights & Architecture

- **Deep Metric Learning:** Leverages **FaceNet512** deep embeddings (`D = 512`) with cosine distance matching (`threshold ≤ 0.40`) for facial verification, replacing heuristic matching with pose- and illumination-tolerant representations.
- **Cryptographic Identity Protection:** Enrolled voter identification numbers are salted and digested using **SHA-512**:

  ```text
  VoterHash = SHA512(CleanID + Salt)
  ```

  This provides a non-reversible masked representation of voter IDs in the database.
- **ACID Transaction Integrity:** Prevents double-voting using database-level uniqueness constraints and atomic verification flags (`has_voted = 1`) within SQLite transactions.
- **Reactive Single-Page Architecture:** Built entirely on Streamlit, eliminating blocking multi-process orchestration, desktop windowing dependencies, and UI-freezing thread locks.

### Verification Pipeline

```text
[Camera Capture]
       │
       ▼
[Facial Detection & Alignment]
       │
       ▼
[512D Embedding Extraction - FaceNet512]
       │
       ▼
[1:N Cosine Distance Verification - ≤ 0.40]
       │
       ▼
[Salted SHA-512 Identity Verification]
       │
       ▼
[Atomic SQL Transaction Ledger]
```

---

## Project Structure

```text
SMART_VOTING_USING_FACE_RECOGNITION/
├── app.py                   # Streamlit web interface & session router
├── core/
│   ├── __init__.py          # Package declaration
│   ├── db.py                # SQLite schema, voter operations & SHA-512 hashing
│   └── face_engine.py       # FaceNet512 embedding inference & cosine verification
├── requirements.txt         # Project dependencies
└── README.md                # Technical documentation
```

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Frontend & Dashboard** | Streamlit, Pandas |
| **Computer Vision & Deep Learning** | DeepFace, FaceNet512, OpenCV Headless, TensorFlow / Keras |
| **Database & Security** | SQLite3, Python Standard Library `hashlib` (Salted SHA-512) |
| **Numerical Computing** | NumPy |

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/SMART_VOTING_USING_FACE_RECOGNITION.git
cd SMART_VOTING_USING_FACE_RECOGNITION
```

### 2. Set Up a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the Application

```bash
streamlit run app.py
```

---

## Application Modules

### 1. Telemetrics Overview

- Displays real-time turnout metrics:
  - Registered Voters
  - Total Ballots Cast
  - Turnout Percentage
- Visualizes the system architecture and facial verification pipeline specifications.

### 2. Voter Enrollment

- Captures voter details:
  - **Unique Identification Number**
  - **Full Name**
  - **Mobile Number**
- Extracts a **512-dimensional facial embedding vector** using `FaceNet512`.
- Commits the voter record to SQLite with an automatically generated salted SHA-512 voter hash.

### 3. Electronic Balloting Booth

#### Step 1 — Biometric Verification

- Captures a probe image from the camera feed.
- Generates a 512-dimensional facial embedding using `FaceNet512`.
- Evaluates the minimum cosine distance against registered voter profiles.
- Accepts the biometric match when the distance is within the configured threshold (`≤ 0.40`).

#### Step 2 — Ballot Submission

- Successful biometric verification unlocks the candidate ballot options.
- The vote is recorded and `has_voted = 1` is updated within a single database transaction.
- Subsequent voting attempts for the same voter are rejected.

### 4. Administrative Operations & Governance

- Administrative access is protected by an administrative passcode.
- Provides live election tallies, including:
  - Vote distribution bar charts
  - Vote tables
  - Summary CSV export

#### Voter Registry Management

- **Export Directory:** Download the voter directory containing:
  - Unique ID
  - Full Name
  - Mobile Number
  - Voted Status
  - Registration Timestamp
- **De-register / Delete Records:** Administrators can remove voter records by entering their ID or selecting a voter from the enrolled registry list.

---

## Security & Privacy Considerations

- **Deterministic Masking:** Citizen identification numbers are not used as plain-text identifiers during polling operations; comparisons rely on salted SHA-512 digests.
- **Template Protection:** Biometric templates are stored as floating-point embedding vectors rather than raw facial image files, reducing exposure of original facial images.
- **Relational Integrity:** Foreign-key constraints with `ON DELETE CASCADE` maintain consistency between voter registry records and associated ballot/audit records.
- **Duplicate Voting Prevention:** Database transactions ensure that recording a ballot and marking the voter as having voted are handled atomically.

> **Important:** This project is intended as a software/academic demonstration of biometric electronic voting concepts. A production electoral system would require substantially stronger security controls, independent biometric validation, secure hardware, cryptographic election protocols, accessibility provisions, auditing, legal/regulatory compliance, and extensive security testing.

---

## System Workflow

```text
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
                    │   Camera Capture    │
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
                    │    Candidate        │
                    │      Ballot         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Atomic SQL Vote     │
                    │ + has_voted = 1     │
                    └─────────────────────┘
```

---

## Configuration

The primary application configuration can be adjusted in the source code, including:

- Face recognition model: `FaceNet512`
- Embedding dimension: `512`
- Cosine distance threshold: `0.40`
- Database engine: `SQLite3`
- Identity hashing: `SHA-512` with a salt
- Application framework: `Streamlit`

For production or deployment environments, administrative credentials should be stored securely rather than hard-coded in application source code.

---

## Future Enhancements

Potential improvements include:

- Multi-factor voter authentication
- Stronger credential and secret management
- Hardware-backed key storage
- Encrypted biometric template storage
- Liveness / anti-spoofing detection
- Role-based administrative access
- Comprehensive audit logging
- Secure remote database deployment
- Improved accessibility support
- Independent security and biometric accuracy testing
- Privacy-preserving biometric matching

---
---

## Disclaimer

> This project is developed for educational, academic, and demonstration purposes. It demonstrates the implementation of biometric voter authentication, facial recognition, database integrity, and electronic ballot management using Python, Streamlit, DeepFace, and SQLite.
>
> This software is **not intended for use in real-world elections or official electoral processes**. Production deployment would require extensive security auditing, biometric validation, privacy protections, accessibility measures, cryptographic election protocols, legal approval, regulatory compliance, and independent testing.
