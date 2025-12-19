"""
SQLite database management for Epic and Feature templates
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TemplateDatabase:
    """Manages template storage in SQLite database"""

    def __init__(self, db_path: str = "templates.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Epic templates table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS epic_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT
            )
        """
        )

        # Feature templates table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feature_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                epic_id INTEGER,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                FOREIGN KEY (epic_id) REFERENCES epic_templates(id)
            )
        """
        )

        conn.commit()
        # Minimal migration: add structured fields if missing
        def ensure_columns(table: str, columns: Dict[str, str]):
            cursor.execute(f"PRAGMA table_info({table})")
            existing = {row[1] for row in cursor.fetchall()}
            for col, col_type in columns.items():
                if col not in existing:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")

        # Epic structured fields
        ensure_columns(
            "epic_templates",
            {
                "description": "TEXT",
                "benefit_hypothesis": "TEXT",
                "nfrs": "TEXT",
                "wsjf_value": "INTEGER",
                "wsjf_time_criticality": "INTEGER",
                "wsjf_risk_reduction": "INTEGER",
                "wsjf_job_size": "INTEGER",
                "wsjf_score": "REAL",
            },
        )

        # Feature structured fields
        ensure_columns(
            "feature_templates",
            {
                "feature_type": "TEXT",
                "description": "TEXT",
                "benefit_hypothesis": "TEXT",
                "acceptance_criteria": "TEXT",
                "nfrs": "TEXT",
                "wsjf_value": "INTEGER",
                "wsjf_time_criticality": "INTEGER",
                "wsjf_risk_reduction": "INTEGER",
                "wsjf_job_size": "INTEGER",
                "wsjf_score": "REAL",
            },
        )

        conn.commit()
        conn.close()

    def save_epic_template(
        self,
        name: str,
        content: str,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        benefit_hypothesis: Optional[str] = None,
        nfrs: Optional[str] = None,
        wsjf_value: Optional[int] = None,
        wsjf_time_criticality: Optional[int] = None,
        wsjf_risk_reduction: Optional[int] = None,
        wsjf_job_size: Optional[int] = None,
    ) -> int:
        """Save an epic template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO epic_templates (name, content, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (name, content, now, now, metadata_json, tags_json),
        )

        template_id = cursor.lastrowid

        # If structured fields provided, update them
        updates = []
        params = []
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if benefit_hypothesis is not None:
            updates.append("benefit_hypothesis = ?")
            params.append(benefit_hypothesis)
        if nfrs is not None:
            updates.append("nfrs = ?")
            params.append(nfrs)
        if wsjf_value is not None:
            updates.append("wsjf_value = ?")
            params.append(wsjf_value)
        if wsjf_time_criticality is not None:
            updates.append("wsjf_time_criticality = ?")
            params.append(wsjf_time_criticality)
        if wsjf_risk_reduction is not None:
            updates.append("wsjf_risk_reduction = ?")
            params.append(wsjf_risk_reduction)
        if wsjf_job_size is not None:
            updates.append("wsjf_job_size = ?")
            params.append(wsjf_job_size)
        # Compute wsjf_score if components present
        wsjf_score = None
        try:
            if (
                wsjf_value is not None
                and wsjf_time_criticality is not None
                and wsjf_risk_reduction is not None
                and wsjf_job_size not in (None, 0)
            ):
                wsjf_score = (
                    (wsjf_value + wsjf_time_criticality + wsjf_risk_reduction)
                    / float(wsjf_job_size)
                )
        except Exception:
            wsjf_score = None
        if wsjf_score is not None:
            updates.append("wsjf_score = ?")
            params.append(wsjf_score)

        if updates:
            params.append(template_id)
            cursor.execute(
                f"UPDATE epic_templates SET {', '.join(updates)} WHERE id = ?",
                params,
            )

        conn.commit()
        conn.close()

        return template_id

    def save_feature_template(
        self,
        name: str,
        content: str,
        epic_id: Optional[int] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        feature_type: Optional[str] = None,
        description: Optional[str] = None,
        benefit_hypothesis: Optional[str] = None,
        acceptance_criteria: Optional[List[str]] = None,
        nfrs: Optional[str] = None,
        wsjf_value: Optional[int] = None,
        wsjf_time_criticality: Optional[int] = None,
        wsjf_risk_reduction: Optional[int] = None,
        wsjf_job_size: Optional[int] = None,
    ) -> int:
        """Save a feature template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO feature_templates (name, epic_id, content, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (name, epic_id, content, now, now, metadata_json, tags_json),
        )

        template_id = cursor.lastrowid

        # If structured fields provided, update them
        updates = []
        params = []
        if feature_type is not None:
            updates.append("feature_type = ?")
            params.append(feature_type)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if benefit_hypothesis is not None:
            updates.append("benefit_hypothesis = ?")
            params.append(benefit_hypothesis)
        if acceptance_criteria is not None:
            updates.append("acceptance_criteria = ?")
            params.append(json.dumps(acceptance_criteria))
        if nfrs is not None:
            updates.append("nfrs = ?")
            params.append(nfrs)
        if wsjf_value is not None:
            updates.append("wsjf_value = ?")
            params.append(wsjf_value)
        if wsjf_time_criticality is not None:
            updates.append("wsjf_time_criticality = ?")
            params.append(wsjf_time_criticality)
        if wsjf_risk_reduction is not None:
            updates.append("wsjf_risk_reduction = ?")
            params.append(wsjf_risk_reduction)
        if wsjf_job_size is not None:
            updates.append("wsjf_job_size = ?")
            params.append(wsjf_job_size)
        # Compute wsjf_score if components present
        wsjf_score = None
        try:
            if (
                wsjf_value is not None
                and wsjf_time_criticality is not None
                and wsjf_risk_reduction is not None
                and wsjf_job_size not in (None, 0)
            ):
                wsjf_score = (
                    (wsjf_value + wsjf_time_criticality + wsjf_risk_reduction)
                    / float(wsjf_job_size)
                )
        except Exception:
            wsjf_score = None
        if wsjf_score is not None:
            updates.append("wsjf_score = ?")
            params.append(wsjf_score)

        if updates:
            params.append(template_id)
            cursor.execute(
                f"UPDATE feature_templates SET {', '.join(updates)} WHERE id = ?",
                params,
            )

        conn.commit()
        conn.close()

        return template_id

    def update_epic_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        benefit_hypothesis: Optional[str] = None,
        nfrs: Optional[str] = None,
        wsjf_value: Optional[int] = None,
        wsjf_time_criticality: Optional[int] = None,
        wsjf_risk_reduction: Optional[int] = None,
        wsjf_job_size: Optional[int] = None,
    ) -> bool:
        """Update an existing epic template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build update query dynamically
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if benefit_hypothesis is not None:
            updates.append("benefit_hypothesis = ?")
            params.append(benefit_hypothesis)
        if nfrs is not None:
            updates.append("nfrs = ?")
            params.append(nfrs)
        if wsjf_value is not None:
            updates.append("wsjf_value = ?")
            params.append(wsjf_value)
        if wsjf_time_criticality is not None:
            updates.append("wsjf_time_criticality = ?")
            params.append(wsjf_time_criticality)
        if wsjf_risk_reduction is not None:
            updates.append("wsjf_risk_reduction = ?")
            params.append(wsjf_risk_reduction)
        if wsjf_job_size is not None:
            updates.append("wsjf_job_size = ?")
            params.append(wsjf_job_size)

        # Compute wsjf_score if components provided
        wsjf_score = None
        try:
            if (
                wsjf_value is not None
                and wsjf_time_criticality is not None
                and wsjf_risk_reduction is not None
                and wsjf_job_size not in (None, 0)
            ):
                wsjf_score = (
                    (wsjf_value + wsjf_time_criticality + wsjf_risk_reduction)
                    / float(wsjf_job_size)
                )
        except Exception:
            wsjf_score = None
        if wsjf_score is not None:
            updates.append("wsjf_score = ?")
            params.append(wsjf_score)

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(template_id)

        query = f"UPDATE epic_templates SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def update_feature_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        content: Optional[str] = None,
        epic_id: Optional[int] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        feature_type: Optional[str] = None,
        description: Optional[str] = None,
        benefit_hypothesis: Optional[str] = None,
        acceptance_criteria: Optional[List[str]] = None,
        nfrs: Optional[str] = None,
        wsjf_value: Optional[int] = None,
        wsjf_time_criticality: Optional[int] = None,
        wsjf_risk_reduction: Optional[int] = None,
        wsjf_job_size: Optional[int] = None,
    ) -> bool:
        """Update an existing feature template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if epic_id is not None:
            updates.append("epic_id = ?")
            params.append(epic_id)
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))
        if feature_type is not None:
            updates.append("feature_type = ?")
            params.append(feature_type)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if benefit_hypothesis is not None:
            updates.append("benefit_hypothesis = ?")
            params.append(benefit_hypothesis)
        if acceptance_criteria is not None:
            updates.append("acceptance_criteria = ?")
            params.append(json.dumps(acceptance_criteria))
        if nfrs is not None:
            updates.append("nfrs = ?")
            params.append(nfrs)
        if wsjf_value is not None:
            updates.append("wsjf_value = ?")
            params.append(wsjf_value)
        if wsjf_time_criticality is not None:
            updates.append("wsjf_time_criticality = ?")
            params.append(wsjf_time_criticality)
        if wsjf_risk_reduction is not None:
            updates.append("wsjf_risk_reduction = ?")
            params.append(wsjf_risk_reduction)
        if wsjf_job_size is not None:
            updates.append("wsjf_job_size = ?")
            params.append(wsjf_job_size)

        # Compute wsjf_score if components provided
        wsjf_score = None
        try:
            if (
                wsjf_value is not None
                and wsjf_time_criticality is not None
                and wsjf_risk_reduction is not None
                and wsjf_job_size not in (None, 0)
            ):
                wsjf_score = (
                    (wsjf_value + wsjf_time_criticality + wsjf_risk_reduction)
                    / float(wsjf_job_size)
                )
        except Exception:
            wsjf_score = None
        if wsjf_score is not None:
            updates.append("wsjf_score = ?")
            params.append(wsjf_score)

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(template_id)

        query = f"UPDATE feature_templates SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def get_epic_template(self, template_id: int) -> Optional[Dict]:
        """Get an epic template by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM epic_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            result = {
                "id": row["id"],
                "name": row["name"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
            # Optional structured fields
            for key in [
                "description",
                "benefit_hypothesis",
                "nfrs",
                "wsjf_value",
                "wsjf_time_criticality",
                "wsjf_risk_reduction",
                "wsjf_job_size",
                "wsjf_score",
            ]:
                try:
                    result[key] = row[key]
                except Exception:
                    result[key] = None
            return result
        return None

    def get_feature_template(self, template_id: int) -> Optional[Dict]:
        """Get a feature template by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM feature_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            result = {
                "id": row["id"],
                "name": row["name"],
                "epic_id": row["epic_id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
            for key in [
                "feature_type",
                "description",
                "benefit_hypothesis",
                "acceptance_criteria",
                "nfrs",
                "wsjf_value",
                "wsjf_time_criticality",
                "wsjf_risk_reduction",
                "wsjf_job_size",
                "wsjf_score",
            ]:
                try:
                    val = row[key]
                    if key == "acceptance_criteria" and val:
                        result[key] = json.loads(val)
                    else:
                        result[key] = val
                except Exception:
                    result[key] = None
            return result
        return None

    def list_epic_templates(
        self, limit: int = 100, offset: int = 0, search: Optional[str] = None
    ) -> List[Dict]:
        """List all epic templates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if search:
            cursor.execute(
                """
                SELECT id, name, created_at, updated_at, tags
                FROM epic_templates
                WHERE name LIKE ? OR content LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (f"%{search}%", f"%{search}%", limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT id, name, created_at, updated_at, tags
                FROM epic_templates
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "tags": json.loads(row["tags"]),
            }
            for row in rows
        ]

    def list_feature_templates(
        self,
        limit: int = 100,
        offset: int = 0,
        epic_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Dict]:
        """List all feature templates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if epic_id:
            cursor.execute(
                """
                SELECT id, name, epic_id, created_at, updated_at, tags
                FROM feature_templates
                WHERE epic_id = ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (epic_id, limit, offset),
            )
        elif search:
            cursor.execute(
                """
                SELECT id, name, epic_id, created_at, updated_at, tags
                FROM feature_templates
                WHERE name LIKE ? OR content LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (f"%{search}%", f"%{search}%", limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT id, name, epic_id, created_at, updated_at, tags
                FROM feature_templates
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "epic_id": row["epic_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "tags": json.loads(row["tags"]),
            }
            for row in rows
        ]

    def delete_epic_template(self, template_id: int) -> bool:
        """Delete an epic template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM epic_templates WHERE id = ?", (template_id,))
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return success

    def delete_feature_template(self, template_id: int) -> bool:
        """Delete a feature template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM feature_templates WHERE id = ?", (template_id,))
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return success

    def export_epic_as_json(self, template_id: int) -> Optional[Dict]:
        """Export an epic template as JSON"""
        return self.get_epic_template(template_id)

    def export_feature_as_json(self, template_id: int) -> Optional[Dict]:
        """Export a feature template as JSON"""
        return self.get_feature_template(template_id)

    def export_all_epics_as_json(self) -> List[Dict]:
        """Export all epic templates as JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM epic_templates ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        result: List[Dict] = []
        for row in rows:
            item = {
                "id": row["id"],
                "name": row["name"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
            for key in [
                "description",
                "benefit_hypothesis",
                "nfrs",
                "wsjf_value",
                "wsjf_time_criticality",
                "wsjf_risk_reduction",
                "wsjf_job_size",
                "wsjf_score",
            ]:
                try:
                    item[key] = row[key]
                except Exception:
                    item[key] = None
            result.append(item)
        return result

    def export_all_features_as_json(self) -> List[Dict]:
        """Export all feature templates as JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM feature_templates ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        result: List[Dict] = []
        for row in rows:
            item = {
                "id": row["id"],
                "name": row["name"],
                "epic_id": row["epic_id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
            for key in [
                "feature_type",
                "description",
                "benefit_hypothesis",
                "acceptance_criteria",
                "nfrs",
                "wsjf_value",
                "wsjf_time_criticality",
                "wsjf_risk_reduction",
                "wsjf_job_size",
                "wsjf_score",
            ]:
                try:
                    val = row[key]
                    if key == "acceptance_criteria" and val:
                        item[key] = json.loads(val)
                    else:
                        item[key] = val
                except Exception:
                    item[key] = None
            result.append(item)
        return result
