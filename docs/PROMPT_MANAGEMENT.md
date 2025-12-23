# Prompt Management Feature

## Overview

Added comprehensive prompt management functionality to the Discovery Coach application, allowing users to edit prompts and manage different versions through the Admin tab.

## Features Implemented

### 1. User Interface (Admin Tab)

Added a new "Prompt Management" section in the Admin tab with:
- **Prompt File Selector**: Dropdown to select from available prompt files in `data/prompt_help/`
- **Version Selector**: Dropdown to select between current active version and saved versions
- **Edit Prompt**: Opens the selected prompt in a full-featured editor
- **Save as Version**: Creates a timestamped backup of the current prompt
- **Set as Active**: Activates a selected version (automatically backs up current version)
- **Delete Version**: Removes a selected version (cannot delete active version)

### 2. Prompt Editor Modal

Features:
- Full-screen modal editor with syntax highlighting preparation
- Displays current file name and version
- Large textarea with monospace font for comfortable editing
- Unsaved changes detection with confirmation dialog
- Can only edit the "Current (Active)" version
- Can view (read-only) any saved version

### 3. Backend API Endpoints

All endpoints are prefixed with `/api/prompts/`:

#### File Operations
- `GET /api/prompts/list` - List all prompt files
- `GET /api/prompts/content/{filename}` - Get current content of a prompt file
- `POST /api/prompts/update` - Update the current prompt file content

#### Version Management
- `GET /api/prompts/versions/list/{filename}` - List all versions of a file
- `GET /api/prompts/versions/content/{filename}/{version_name}` - Get specific version content
- `POST /api/prompts/versions/create` - Create a new version from current content
- `POST /api/prompts/versions/activate` - Activate a version (with automatic backup)
- `DELETE /api/prompts/versions/delete` - Delete a specific version

### 4. Version Control System

Structure:
```
data/
├── prompt_help/
│   ├── system_prompt.txt           (Current active version)
│   ├── epic_questionnaire.txt      (Current active version)
│   ├── feature_questionnaire.txt   (Current active version)
│   └── versions/
│       ├── system_prompt/
│       │   ├── 2025-12-23_14-30-00.txt
│       │   ├── 2025-12-23_15-45-00.txt
│       │   └── backup_2025-12-23_16-20-00.txt
│       ├── epic_questionnaire/
│       └── feature_questionnaire/
```

Features:
- Automatic timestamp-based version naming
- Optional custom version names
- Automatic backup creation when activating a version
- Sorted by modification time (newest first)
- Version metadata includes timestamp and file size

## Usage Workflow

### Editing a Prompt

1. Navigate to the **Admin** tab
2. Select a prompt file from the dropdown (e.g., "system_prompt.txt")
3. Versions list will load automatically
4. Click **"✏️ Edit Prompt"** to open the editor
5. Make your changes in the textarea
6. Click **"💾 Save Changes"** to update the active version

### Creating a Version Backup

1. Select the prompt file you want to backup
2. Click **"💾 Save as Version"**
3. Enter a custom name or leave blank for automatic timestamp
4. Version is created and appears in the versions dropdown

### Switching to a Previous Version

1. Select the prompt file
2. Select the desired version from the versions dropdown
3. Click **"✏️ Edit Prompt"** to view the version content (read-only)
4. To make it active, click **"✅ Set as Active"**
5. Confirm the action (current version will be automatically backed up)
6. The selected version becomes the new active version

### Viewing Version History

1. Select a prompt file
2. The versions dropdown shows all available versions with timestamps
3. Select any version and click **"✏️ Edit Prompt"** to view its content

### Deleting Old Versions

1. Select a prompt file
2. Select the version to delete from the dropdown
3. Click **"🗑️ Delete Version"**
4. Confirm the deletion (cannot be undone)

## Technical Details

### Frontend Components

**Files Modified:**
- `frontend/index.html` - Added Prompt Management section and modal
- `frontend/script.js` - Added prompt management functions (~280 lines)
- `frontend/styles.css` - Added prompt editor styles

**Key JavaScript Functions:**
- `loadPromptFilesList()` - Loads available prompt files
- `loadPromptFile()` - Loads a specific file and its versions
- `loadPromptVersion()` - Switches between versions
- `openPromptEditor()` - Opens the editor modal
- `savePromptChanges()` - Saves changes to current version
- `createPromptVersion()` - Creates a new version
- `activatePromptVersion()` - Activates a selected version
- `deletePromptVersion()` - Deletes a version

### Backend Implementation

**File Modified:**
- `backend/app.py` - Added 8 new endpoints (~260 lines)

**Key Endpoints:**
- List files and versions
- Read/write prompt content
- Version CRUD operations
- Automatic backup on version activation

**Request Models:**
- `PromptUpdateRequest` - For updating prompt content
- `PromptVersionRequest` - For version operations

### Error Handling

- File not found errors (404 responses)
- Invalid version operations (400 responses)
- Cannot edit non-current versions (warning message)
- Cannot delete current version (warning message)
- Unsaved changes confirmation dialog
- Network error handling with user feedback

### Security Considerations

- File path validation (restricted to `data/prompt_help/` directory)
- No arbitrary file system access
- Version names sanitized
- Read/write operations use UTF-8 encoding

## Future Enhancements

Possible improvements:
1. **Diff View**: Show differences between versions
2. **Syntax Highlighting**: Add real-time syntax highlighting for prompts
3. **Search**: Search within prompt content
4. **Export/Import**: Export versions to files or import from external sources
5. **Rollback History**: Track who made changes and when
6. **Preview Mode**: Test prompts before activating
7. **Bulk Operations**: Manage multiple versions at once
8. **Version Comparison**: Side-by-side comparison of versions

## Testing

To test the feature:

1. Start the server: `./start.sh`
2. Open the frontend: `http://localhost:8050`
3. Click on the **"⚙️ Admin"** tab
4. Scroll to the **"📝 Prompt Management"** section
5. Select a prompt file and test the various operations

## Dependencies

No new dependencies were added. The feature uses existing:
- FastAPI for backend
- Vanilla JavaScript for frontend
- Standard Python libraries (os, datetime)

## Files Changed

1. `frontend/index.html` - Added UI components
2. `frontend/script.js` - Added JavaScript functions
3. `frontend/styles.css` - Added styles
4. `backend/app.py` - Added API endpoints
5. Created `data/prompt_help/versions/` directory structure

## Documentation Updated

- This file: `docs/PROMPT_MANAGEMENT.md`
- Main README should be updated to mention this feature
