"""
One-off migration: adds the new SecurityFinding columns (confidence, impact,
recommendation, evidence, owasp, cwe) to an EXISTING Postgres database.

Not needed for a fresh DB — Base.metadata.create_all() in main.py already
creates these columns for a table that doesn't exist yet. This script is
only for a database that already has a security_findings table from before
this change.

Usage:
    python backend/migrations/add_finding_fields.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import text
from backend.database.db import engine

NEW_COLUMNS = {
    "confidence": "VARCHAR DEFAULT 'high'",
    "impact": "TEXT",
    "recommendation": "TEXT",
    "evidence": "TEXT",
    "owasp": "VARCHAR",
    "cwe": "VARCHAR",
}

with engine.begin() as conn:
    for col, coltype in NEW_COLUMNS.items():
        conn.execute(text(
            f"ALTER TABLE security_findings ADD COLUMN IF NOT EXISTS {col} {coltype}"
        ))
        print(f"ok: {col}")

print("Migration complete.")
