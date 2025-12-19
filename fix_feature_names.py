#!/usr/bin/env python3
"""
Script to extract and update feature names from their content in the database.
"""

import sqlite3
import re


def extract_feature_name(content):
    """Extract feature name from content using multiple patterns."""
    # Try format 1: "FEATURE NAME:" followed by the name on next line
    match = re.search(r"FEATURE NAME:\s*\n\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        if name and name != "[Fill in here]":
            return name

    # Try format 2: "1. FEATURE NAME" with subtitle line
    match = re.search(
        r"(?:\d+\.\s*)?FEATURE NAME\s*\n.*?\n\s*(.+?)(?:\n|$)", content, re.IGNORECASE
    )
    if match:
        name = match.group(1).strip()
        if name and name != "[Fill in here]":
            return name

    return None


def main():
    conn = sqlite3.connect("templates.db")
    cursor = conn.cursor()

    # Get all features with generic "Feature X" names
    cursor.execute(
        "SELECT id, name, content FROM feature_templates WHERE name LIKE 'Feature %'"
    )
    features = cursor.fetchall()

    print(f"Found {len(features)} features with generic names\n")

    updated = 0
    for feature_id, old_name, content in features:
        new_name = extract_feature_name(content)
        if new_name:
            print(f"ID {feature_id}: '{old_name}' -> '{new_name}'")
            cursor.execute(
                "UPDATE feature_templates SET name = ? WHERE id = ?",
                (new_name, feature_id),
            )
            updated += 1
        else:
            print(f"ID {feature_id}: Could not extract name from content")

    conn.commit()
    conn.close()

    print(f"\n✅ Updated {updated} feature names")


if __name__ == "__main__":
    main()
