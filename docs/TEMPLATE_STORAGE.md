# Template Storage and Management System

## Overview
The Discovery Coach now includes a complete template storage and management system using SQLite database. You can save filled templates, load them for editing, and export them as JSON.

## Features

### 💾 Save Template to Database
- Store filled Epic or Feature templates in a local SQLite database
- Add custom names and tags for organization
- Automatically tracks creation and update timestamps
- Stores metadata (model used, provider, creation source)

### 📂 Load Template from Database
- Retrieve previously saved templates by ID
- Continue working on templates across sessions
- View template metadata (name, dates, tags)
- Edit and update existing templates

### 📋 View Saved Templates
- List all saved Epic or Feature templates
- See template names, IDs, creation dates, and tags
- Quick overview of all stored templates
- Search functionality (coming soon)

### 📤 Export as JSON
- Export individual templates as JSON files
- Export all templates of a type (Epic or Feature) at once
- Downloadable JSON files for backup or integration
- Includes all metadata and content

## How to Use

### 1. Fill and Save a Template

```
1. Have a discovery conversation with the coach
2. Click "📝 Fill Epic Template" or "📝 Fill Feature Template"
3. Review the filled template in the chat
4. Click "💾 Save Template to DB"
5. Enter a name for the template
6. Optionally add tags (comma-separated)
7. Template is saved with a unique ID
```

### 2. Load an Existing Template

```
1. Click "📂 Load Template from DB"
2. Enter template type: "epic" or "feature"
3. Enter the template ID
4. Template content appears in the chat
5. You can now continue editing or export it
```

### 3. View All Saved Templates

```
1. Click "📋 View Saved Templates"
2. Enter template type: "epic" or "feature"
3. See a list of all saved templates with:
   - Template ID
   - Template Name
   - Tags
   - Creation and Update dates
```

### 4. Export Templates as JSON

```
For a single template:
1. Click "📤 Export as JSON"
2. Choose "Cancel" (for single template)
3. Enter template type: "epic" or "feature"
4. Enter the template ID
5. JSON file downloads automatically

For all templates:
1. Click "📤 Export as JSON"
2. Choose "OK" (for all templates)
3. Enter template type: "epic" or "feature"
4. JSON file with all templates downloads
```

## Database Schema

### Epic Templates Table
```sql
CREATE TABLE epic_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT,  -- JSON: {model, provider, created_from}
    tags TEXT       -- JSON: ["tag1", "tag2"]
);
```

### Feature Templates Table
```sql
CREATE TABLE feature_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    epic_id INTEGER,  -- Optional link to parent Epic
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT,    -- JSON: {model, provider, created_from}
    tags TEXT,        -- JSON: ["tag1", "tag2"]
    FOREIGN KEY (epic_id) REFERENCES epic_templates(id)
);
```

## API Endpoints

### POST /api/template/save
Save a new template to the database.

**Request:**
```json
{
  "template_type": "epic",
  "name": "Customer Onboarding Epic",
  "content": "EPIC NAME\n...",
  "epic_id": null,
  "metadata": {
    "model": "gpt-4o-mini",
    "provider": "openai",
    "created_from": "discovery_conversation"
  },
  "tags": ["onboarding", "customer", "priority-high"]
}
```

**Response:**
```json
{
  "success": true,
  "template_id": 1,
  "message": "Epic template saved successfully"
}
```

### POST /api/template/load
Load a template from the database.

**Request:**
```json
{
  "template_id": 1,
  "template_type": "epic"
}
```

**Response:**
```json
{
  "success": true,
  "template": {
    "id": 1,
    "name": "Customer Onboarding Epic",
    "content": "EPIC NAME\n...",
    "created_at": "2025-12-19T10:30:00",
    "updated_at": "2025-12-19T10:30:00",
    "metadata": {...},
    "tags": ["onboarding", "customer"]
  }
}
```

### GET /api/template/list/{template_type}
List all templates of a given type.

**Request:**
```
GET /api/template/list/epic?limit=100&offset=0&search=onboarding
```

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": 1,
      "name": "Customer Onboarding Epic",
      "created_at": "2025-12-19T10:30:00",
      "updated_at": "2025-12-19T10:30:00",
      "tags": ["onboarding", "customer"]
    }
  ],
  "count": 1
}
```

### POST /api/template/update
Update an existing template.

**Request:**
```json
{
  "template_id": 1,
  "template_type": "epic",
  "name": "Updated Epic Name",
  "content": "Updated content...",
  "tags": ["updated", "reviewed"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Epic template updated successfully"
}
```

### POST /api/template/delete
Delete a template from the database.

**Request:**
```json
{
  "template_id": 1,
  "template_type": "epic"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Epic template deleted successfully"
}
```

### POST /api/template/export
Export template(s) as JSON.

**Request (single template):**
```json
{
  "template_type": "epic",
  "template_id": 1,
  "export_all": false
}
```

**Request (all templates):**
```json
{
  "template_type": "epic",
  "export_all": true
}
```

**Response:**
```json
{
  "success": true,
  "export_type": "single",
  "template_type": "epic",
  "data": {
    "id": 1,
    "name": "Customer Onboarding Epic",
    "content": "...",
    "created_at": "2025-12-19T10:30:00",
    "updated_at": "2025-12-19T10:30:00",
    "metadata": {...},
    "tags": [...]
  }
}
```

## File Locations

- **Database**: `templates.db` (created automatically in project root)
- **Backend Module**: `backend/template_db.py` (SQLite management)
- **API Endpoints**: `backend/app.py` (FastAPI routes)
- **Frontend UI**: `frontend/index.html` (Template Storage section)
- **Frontend Logic**: `frontend/script.js` (Template management functions)

## Tips and Best Practices

### Naming Convention
- Use descriptive names: "Customer Onboarding - MVP Epic"
- Include version if iterating: "Payment Integration v2"
- Add project/team identifiers: "[B2B] Sales Portal Feature"

### Tagging Strategy
- Use consistent tags across templates
- Examples: `priority-high`, `q1-2026`, `customer-facing`, `technical-debt`
- Tags make it easy to filter and organize templates

### Workflow Example
```
Day 1:
1. Discovery conversation about new feature
2. Fill Feature Template
3. Save to DB with tags: "draft", "needs-review"

Day 2:
4. Load template from DB
5. Continue refinement conversation
6. Update template in DB, change tag to "reviewed"

Day 3:
7. Export as JSON for documentation system
8. Share with team via JSON file
```

### Backup Strategy
- Periodically export all templates as JSON
- Store JSON exports in version control
- Database file (`templates.db`) should be backed up regularly

### Integration with Other Systems
The JSON export format is designed for easy integration:
- Import into Jira, Confluence, or other tools
- Parse with scripts for reporting
- Convert to other formats (PDF, Word, etc.)

## Troubleshooting

### Template not saving
- Check that you've filled a template first
- Ensure the backend server is running
- Check browser console for errors

### Can't find template ID
- Use "📋 View Saved Templates" to see all IDs
- IDs are auto-incremented starting from 1

### Database file missing
- Database is created automatically on first save
- Located at: `templates.db` in project root
- If deleted, a new empty database will be created

### Export not downloading
- Check browser's download settings
- Allow pop-ups from localhost
- Check browser console for errors

## Future Enhancements

Planned features for future releases:
- ✨ Search templates by content and tags
- ✨ Bulk operations (delete, export, tag)
- ✨ Template versioning and history
- ✨ Compare template versions
- ✨ Share templates via link
- ✨ Import templates from JSON
- ✨ Template templates (pre-filled examples)
- ✨ Rich text editing in browser
- ✨ Collaborative editing features

## Technical Details

### Database Technology
- **SQLite3**: Lightweight, serverless, zero-configuration
- **Location**: Local file (`templates.db`)
- **Performance**: Suitable for thousands of templates
- **Portability**: Single file, easy to backup and move

### Security Considerations
- Database stored locally (not transmitted)
- Sensitive data remains on your machine
- Use Ollama provider for extra privacy
- No external database connections required

### Performance
- Fast retrieval (indexed by ID)
- Efficient search (SQLite FTS available)
- Minimal overhead (< 1MB database for typical use)
- No external API calls for storage operations

## Support

If you encounter issues:
1. Check the browser console for errors
2. Verify the backend server is running
3. Check `templates.db` file permissions
4. Review API response in Network tab
5. Restart the backend server

For questions or feature requests, create an issue in the repository.
