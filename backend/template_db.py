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

    def __init__(self, db_path: str = "backend/db/templates.db"):
        """Initialize database connection"""
        self.db_path = db_path
        # Ensure db directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Strategic Initiative templates table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS strategic_initiative_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                strategic_context TEXT,
                customer_segment TEXT,
                desired_outcomes TEXT,
                leading_indicators TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT
            )
        """
        )

        # Epic templates table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS epic_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                strategic_initiative_id INTEGER,
                content TEXT NOT NULL,
                epic_hypothesis_statement TEXT,
                business_outcome TEXT,
                leading_indicators TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                FOREIGN KEY (strategic_initiative_id) REFERENCES strategic_initiative_templates(id)
            )
        """
        )

        # Add new columns to existing epic_templates table if they don't exist
        try:
            cursor.execute(
                "ALTER TABLE epic_templates ADD COLUMN epic_hypothesis_statement TEXT"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute(
                "ALTER TABLE epic_templates ADD COLUMN business_outcome TEXT"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute(
                "ALTER TABLE epic_templates ADD COLUMN leading_indicators TEXT"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Feature templates table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feature_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                epic_id INTEGER,
                content TEXT NOT NULL,
                benefit_hypothesis TEXT,
                acceptance_criteria TEXT,
                wsjf TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                FOREIGN KEY (epic_id) REFERENCES epic_templates(id)
            )
        """
        )

        # Add new columns to existing feature_templates table if they don't exist
        try:
            cursor.execute(
                "ALTER TABLE feature_templates ADD COLUMN benefit_hypothesis TEXT"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute(
                "ALTER TABLE feature_templates ADD COLUMN acceptance_criteria TEXT"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE feature_templates ADD COLUMN wsjf TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Strategic Initiatives table (actual initiatives, not templates)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS strategic_initiatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                objective TEXT,
                key_results TEXT,
                milestones TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT
            )
        """
        )

        # Story templates table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS story_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                feature_id INTEGER,
                content TEXT NOT NULL,
                description TEXT,
                acceptance_criteria TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                tags TEXT,
                FOREIGN KEY (feature_id) REFERENCES feature_templates(id)
            )
        """
        )

        conn.commit()
        conn.close()

    def save_strategic_initiative_template(
        self,
        name: str,
        content: str,
        strategic_context: Optional[str] = None,
        customer_segment: Optional[str] = None,
        desired_outcomes: Optional[str] = None,
        leading_indicators: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save a strategic initiative template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO strategic_initiative_templates (name, content, strategic_context, customer_segment, desired_outcomes, leading_indicators, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                content,
                strategic_context,
                customer_segment,
                desired_outcomes,
                leading_indicators,
                now,
                now,
                metadata_json,
                tags_json,
            ),
        )

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return template_id

    def save_epic_template(
        self,
        name: str,
        content: str,
        epic_hypothesis_statement: Optional[str] = None,
        business_outcome: Optional[str] = None,
        leading_indicators: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save an epic template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO epic_templates (name, content, epic_hypothesis_statement, business_outcome, leading_indicators, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                content,
                epic_hypothesis_statement,
                business_outcome,
                leading_indicators,
                now,
                now,
                metadata_json,
                tags_json,
            ),
        )

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return template_id

    def save_feature_template(
        self,
        name: str,
        content: str,
        epic_id: Optional[int] = None,
        benefit_hypothesis: Optional[str] = None,
        acceptance_criteria: Optional[str] = None,
        wsjf: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save a feature template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO feature_templates (name, epic_id, content, benefit_hypothesis, acceptance_criteria, wsjf, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                epic_id,
                content,
                benefit_hypothesis,
                acceptance_criteria,
                wsjf,
                now,
                now,
                metadata_json,
                tags_json,
            ),
        )

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return template_id

    def update_epic_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        content: Optional[str] = None,
        epic_hypothesis_statement: Optional[str] = None,
        business_outcome: Optional[str] = None,
        leading_indicators: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
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
        if epic_hypothesis_statement is not None:
            updates.append("epic_hypothesis_statement = ?")
            params.append(epic_hypothesis_statement)
        if business_outcome is not None:
            updates.append("business_outcome = ?")
            params.append(business_outcome)
        if leading_indicators is not None:
            updates.append("leading_indicators = ?")
            params.append(leading_indicators)
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))

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

    def get_strategic_initiative_template(self, template_id: int) -> Optional[Dict]:
        """Get a strategic initiative template by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM strategic_initiative_templates WHERE id = ?", (template_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "content": row["content"],
                "strategic_context": row["strategic_context"],
                "customer_segment": row["customer_segment"],
                "desired_outcomes": row["desired_outcomes"],
                "leading_indicators": row["leading_indicators"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
        return None

    def get_epic_template(self, template_id: int) -> Optional[Dict]:
        """Get an epic template by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM epic_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "content": row["content"],
                "epic_hypothesis_statement": row["epic_hypothesis_statement"],
                "business_outcome": row["business_outcome"],
                "leading_indicators": row["leading_indicators"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
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
            return {
                "id": row["id"],
                "name": row["name"],
                "epic_id": row["epic_id"],
                "content": row["content"],
                "benefit_hypothesis": row["benefit_hypothesis"],
                "acceptance_criteria": row["acceptance_criteria"],
                "wsjf": row["wsjf"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
        return None

    def list_strategic_initiative_templates(
        self, limit: int = 100, offset: int = 0, search: Optional[str] = None
    ) -> List[Dict]:
        """List all strategic initiative templates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if search:
            cursor.execute(
                """
                SELECT id, name, created_at, updated_at, tags
                FROM strategic_initiative_templates
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
                FROM strategic_initiative_templates
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
                SELECT id, name, epic_id, created_at, updated_at, tags, metadata
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
                SELECT id, name, epic_id, created_at, updated_at, tags, metadata
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
                SELECT id, name, epic_id, created_at, updated_at, tags, metadata
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
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            }
            for row in rows
        ]

    def delete_strategic_initiative_template(self, template_id: int) -> bool:
        """Delete a strategic initiative template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM strategic_initiative_templates WHERE id = ?", (template_id,)
        )
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return success

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

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "content": row["content"],
                "epic_hypothesis_statement": row["epic_hypothesis_statement"],
                "business_outcome": row["business_outcome"],
                "leading_indicators": row["leading_indicators"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
            for row in rows
        ]

    def export_all_features_as_json(self) -> List[Dict]:
        """Export all feature templates as JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM feature_templates ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "epic_id": row["epic_id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
            for row in rows
        ]

    # ============================================
    # Story Template Functions
    # ============================================

    def save_story_template(
        self,
        name: str,
        content: str,
        feature_id: Optional[int] = None,
        description: Optional[str] = None,
        acceptance_criteria: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save a story template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO story_templates (name, feature_id, content, description, acceptance_criteria, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                feature_id,
                content,
                description,
                acceptance_criteria,
                now,
                now,
                metadata_json,
                tags_json,
            ),
        )

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"✅ Saved story template '{name}' with ID: {template_id}")
        return template_id

    def get_story_template(self, template_id: int) -> Optional[Dict]:
        """Get a story template by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM story_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "feature_id": row["feature_id"],
                "content": row["content"],
                "description": row["description"],
                "acceptance_criteria": row["acceptance_criteria"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
        return None

    def list_story_templates(
        self,
        limit: int = 100,
        offset: int = 0,
        feature_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Dict]:
        """List all story templates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if feature_id:
            cursor.execute(
                """
                SELECT id, name, feature_id, created_at, updated_at, tags, metadata
                FROM story_templates
                WHERE feature_id = ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (feature_id, limit, offset),
            )
        elif search:
            cursor.execute(
                """
                SELECT id, name, feature_id, created_at, updated_at, tags, metadata
                FROM story_templates
                WHERE name LIKE ? OR content LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (f"%{search}%", f"%{search}%", limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT id, name, feature_id, created_at, updated_at, tags, metadata
                FROM story_templates
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
                "feature_id": row["feature_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "tags": json.loads(row["tags"]),
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            }
            for row in rows
        ]

    def delete_story_template(self, template_id: int) -> bool:
        """Delete a story template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM story_templates WHERE id = ?", (template_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    # ============================================
    # Strategic Initiatives (Work Items)
    # ============================================

    def save_strategic_initiative(
        self,
        name: str,
        objective: Optional[str] = None,
        key_results: Optional[str] = None,
        milestones: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """Save a strategic initiative to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        tags_json = json.dumps(tags) if tags else "[]"

        cursor.execute(
            """
            INSERT INTO strategic_initiatives (name, objective, key_results, milestones, created_at, updated_at, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                objective,
                key_results,
                milestones,
                now,
                now,
                metadata_json,
                tags_json,
            ),
        )

        initiative_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return initiative_id

    def get_strategic_initiative(self, initiative_id: int) -> Optional[Dict]:
        """Get a strategic initiative by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM strategic_initiatives WHERE id = ?", (initiative_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "name": row["name"],
                "objective": row["objective"],
                "key_results": row["key_results"],
                "milestones": row["milestones"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]),
                "tags": json.loads(row["tags"]),
            }
        return None

    def update_strategic_initiative(
        self,
        initiative_id: int,
        name: Optional[str] = None,
        objective: Optional[str] = None,
        key_results: Optional[str] = None,
        milestones: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Update a strategic initiative"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get existing data
        existing = self.get_strategic_initiative(initiative_id)
        if not existing:
            conn.close()
            return False

        # Use existing values if new ones not provided
        name = name if name is not None else existing["name"]
        objective = objective if objective is not None else existing["objective"]
        key_results = (
            key_results if key_results is not None else existing["key_results"]
        )
        milestones = milestones if milestones is not None else existing["milestones"]
        metadata = metadata if metadata is not None else existing["metadata"]
        tags = tags if tags is not None else existing["tags"]

        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata)
        tags_json = json.dumps(tags)

        cursor.execute(
            """
            UPDATE strategic_initiatives
            SET name = ?, objective = ?, key_results = ?, milestones = ?, updated_at = ?, metadata = ?, tags = ?
            WHERE id = ?
        """,
            (
                name,
                objective,
                key_results,
                milestones,
                now,
                metadata_json,
                tags_json,
                initiative_id,
            ),
        )

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def list_strategic_initiatives(
        self, limit: int = 100, offset: int = 0, search: Optional[str] = None
    ) -> List[Dict]:
        """List all strategic initiatives"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if search:
            cursor.execute(
                """
                SELECT id, name, objective, created_at, updated_at, tags
                FROM strategic_initiatives
                WHERE name LIKE ? OR objective LIKE ?
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """,
                (f"%{search}%", f"%{search}%", limit, offset),
            )
        else:
            cursor.execute(
                """
                SELECT id, name, objective, created_at, updated_at, tags
                FROM strategic_initiatives
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
                "objective": row["objective"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "tags": json.loads(row["tags"]),
            }
            for row in rows
        ]

    def delete_strategic_initiative(self, initiative_id: int) -> bool:
        """Delete a strategic initiative"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM strategic_initiatives WHERE id = ?", (initiative_id,)
        )
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return success
