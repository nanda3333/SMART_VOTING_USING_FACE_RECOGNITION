import sqlite3
import hashlib
import numpy as np
from datetime import datetime

DB_PATH = "voting_system.db"
PEPPER_SALT = "smart_voting_sha512_secure_salt_v2026"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id TEXT UNIQUE NOT NULL,
                voter_hash TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                mobile TEXT NOT NULL,
                face_encoding BLOB NOT NULL,
                has_voted INTEGER DEFAULT 0,
                registered_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_hash TEXT UNIQUE NOT NULL,
                party TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (voter_hash) REFERENCES voters (voter_hash) ON DELETE CASCADE
            )
        """)
        conn.commit()

def hash_identifier(identifier: str) -> str:
    clean_id = identifier.strip()
    salted_payload = (clean_id + PEPPER_SALT).encode("utf-8")
    return hashlib.sha512(salted_payload).hexdigest()

def register_voter(voter_id: str, name: str, mobile: str, embedding: np.ndarray) -> bool:
    clean_id = voter_id.strip()
    v_hash = hash_identifier(clean_id)
    blob_data = embedding.astype(np.float32).tobytes()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.cursor().execute(
                """
                INSERT INTO voters (voter_id, voter_hash, name, mobile, face_encoding, registered_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (clean_id, v_hash, name.strip(), mobile.strip(), blob_data, now)
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def load_all_embeddings() -> list[tuple[str, np.ndarray]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT voter_hash, face_encoding FROM voters")
        rows = cursor.fetchall()

    registry = []
    for voter_hash, blob in rows:
        embedding = np.frombuffer(blob, dtype=np.float32)
        registry.append((voter_hash, embedding))
    return registry

def cast_vote(voter_hash: str, party: str) -> tuple[bool, str]:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT has_voted FROM voters WHERE voter_hash = ?", (voter_hash,))
        record = cursor.fetchone()

        if not record:
            return False, "Voter registration record not found."
        if record[0] == 1:
            return False, "Ballot rejected: Identity has already cast a vote."

        cursor.execute(
            "INSERT INTO votes (voter_hash, party, timestamp) VALUES (?, ?, ?)",
            (voter_hash, party, now)
        )
        cursor.execute(
            "UPDATE voters SET has_voted = 1 WHERE voter_hash = ?",
            (voter_hash,)
        )
        conn.commit()
    return True, "Ballot successfully recorded in the audit ledger."

def delete_voter_by_hash(voter_hash: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("DELETE FROM votes WHERE voter_hash = ?", (voter_hash,))
        cursor.execute("DELETE FROM voters WHERE voter_hash = ?", (voter_hash,))
        conn.commit()
        return cursor.rowcount > 0

def delete_voter_by_id(identifier: str) -> bool:
    v_hash = hash_identifier(identifier)
    return delete_voter_by_hash(v_hash)

def get_all_voters() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, voter_id, name, mobile, voter_hash, has_voted, registered_at
            FROM voters ORDER BY id DESC
        """)
        rows = cursor.fetchall()

    voters = []
    for r in rows:
        voters.append({
            "Database ID": r[0],
            "Unique Voter ID": r[1],
            "Full Name": r[2],
            "Mobile Number": r[3],
            "Voter Hash": r[4][:16] + "...",
            "Full Hash": r[4],
            "Voted Status": "Yes" if r[5] == 1 else "No",
            "Registered At": r[6]
        })
    return voters

def get_analytics():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT party, COUNT(*) FROM votes GROUP BY party")
        vote_counts = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM voters")
        total_voters = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM votes")
        total_votes = cursor.fetchone()[0]

    return vote_counts, total_voters, total_votes