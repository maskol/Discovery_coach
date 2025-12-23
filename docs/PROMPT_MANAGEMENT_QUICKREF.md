# Prompt Management Quick Reference

## Access
Admin Tab → Prompt Management Section

## Operations

### 📝 Edit Current Prompt
1. Select file → Click "✏️ Edit Prompt"
2. Make changes → Click "💾 Save Changes"

### 💾 Create Version Backup
1. Select file → Click "💾 Save as Version"
2. Enter name (optional) → Creates timestamped backup

### 🔄 Switch Versions
1. Select file → Choose version from dropdown
2. Click "✅ Set as Active" → Confirm
3. Current version auto-backed up

### 🗑️ Delete Version
1. Select file → Choose version (not "Current")
2. Click "🗑️ Delete Version" → Confirm

## File Structure
```
data/prompt_help/
├── system_prompt.txt              ← Active version
├── epic_questionnaire.txt         ← Active version  
├── feature_questionnaire.txt      ← Active version
└── versions/
    ├── system_prompt/
    │   ├── 2025-12-23_14-30-00.txt
    │   └── backup_2025-12-23_15-00-00.txt
    ├── epic_questionnaire/
    └── feature_questionnaire/
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/prompts/list` | GET | List all prompt files |
| `/api/prompts/content/{filename}` | GET | Get current content |
| `/api/prompts/update` | POST | Update current version |
| `/api/prompts/versions/list/{filename}` | GET | List all versions |
| `/api/prompts/versions/content/{filename}/{version}` | GET | Get version content |
| `/api/prompts/versions/create` | POST | Create new version |
| `/api/prompts/versions/activate` | POST | Activate a version |
| `/api/prompts/versions/delete` | DELETE | Delete a version |

## Tips

✅ **Save often**: Create versions before major changes  
✅ **Name versions**: Use descriptive names like "improved-telecom" or "2025-Q1"  
✅ **Test first**: Review version content before activating  
✅ **Keep backups**: System auto-backs up when activating versions  
⚠️ **Cannot edit**: Can only edit "Current (Active)" version  
⚠️ **Cannot delete**: Cannot delete the active version  

## Testing

```bash
# Start server
./start.sh

# Run API tests
./tests/test_prompt_management.sh

# Or test manually
curl http://localhost:8050/api/prompts/list
```

## Troubleshooting

**Problem**: "Please select a prompt file first"  
**Solution**: Select a file from the dropdown first

**Problem**: Cannot save changes  
**Solution**: Make sure you're editing "Current (Active)" version

**Problem**: Version doesn't appear  
**Solution**: Refresh by re-selecting the file

**Problem**: Server error  
**Solution**: Check `data/prompt_help/versions/` directory exists

## See Also
- [Full Documentation](PROMPT_MANAGEMENT.md)
- [Admin Tab Features](docs/03-FEATURES.md#admin-features)
