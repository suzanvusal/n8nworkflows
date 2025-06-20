# N8N Workflow Naming Convention

## Overview
This document establishes a consistent naming convention for n8n workflow files to improve organization, searchability, and maintainability.

## Current State Analysis
- **Total workflows**: 2,053 files
- **Problematic files**: 858 generic "workflow_XXX" patterns (41.7%)
- **Broken filenames**: 9 incomplete names (fixed)
- **Well-named files**: ~1,200 files (58.3%)

## Standardized Naming Format

### Primary Format
```
[ID]_[Service1]_[Service2]_[Purpose]_[Trigger].json
```

### Components

#### 1. ID (Optional but Recommended)
- **Format**: `001-9999`
- **Purpose**: Maintains existing numbering for tracking
- **Examples**: `100_`, `1001_`, `2500_`

#### 2. Services (1-3 primary integrations)
- **Format**: CamelCase service names
- **Examples**: `Gmail`, `Slack`, `GoogleSheets`, `Stripe`, `Hubspot`
- **Limit**: Maximum 3 services to keep names readable
- **Order**: Most important service first

#### 3. Purpose (Required)
- **Common purposes**:
  - `Create` - Creating new records/content
  - `Update` - Updating existing data
  - `Sync` - Synchronizing between systems
  - `Send` - Sending notifications/messages
  - `Backup` - Data backup operations
  - `Monitor` - Monitoring and alerting
  - `Process` - Data processing/transformation
  - `Import` - Importing/fetching data
  - `Export` - Exporting data
  - `Automation` - General automation tasks

#### 4. Trigger Type (Optional)
- **When to include**: For non-manual workflows
- **Types**: `Webhook`, `Scheduled`, `Triggered`
- **Omit**: For manual workflows (most common)

### Examples of Good Names

#### Current Good Examples (Keep As-Is)
```
100_Create_a_new_task_in_Todoist.json
103_verify_email.json
110_Get_SSL_Certificate.json
112_Get_Company_by_Name.json
```

#### Improved Names (After Renaming)
```
# Before: 1001_workflow_1001.json
# After:  1001_Bitwarden_Automation.json

# Before: 1005_workflow_1005.json  
# After:  1005_Openweathermap_SMS_Scheduled.json

# Before: 100_workflow_100.json
# After:  100_Data_Process.json
```

#### Hash-Based Names (Preserve Description)
```
# Good: Keep the descriptive part
02GdRzvsuHmSSgBw_Nostr_AI_Powered_Reporting_Gmail_Telegram.json

# Better: Clean up if too long
17j2efAe10uXRc4p_Auto_WordPress_Blog_Generator.json
```

## Naming Rules

### Character Guidelines
- **Use**: Letters, numbers, underscores, hyphens
- **Avoid**: Spaces, special characters (`<>:"|?*`)
- **Replace**: Spaces with underscores
- **Length**: Maximum 80 characters (recommended), 100 absolute max

### Service Name Mappings
```
n8n-nodes-base.gmail → Gmail
n8n-nodes-base.googleSheets → GoogleSheets  
n8n-nodes-base.slack → Slack
n8n-nodes-base.stripe → Stripe
n8n-nodes-base.hubspot → Hubspot
n8n-nodes-base.webhook → Webhook
n8n-nodes-base.cron → Cron
n8n-nodes-base.httpRequest → HTTP
```

### Purpose Keywords Detection
Based on workflow content analysis:
- **Create**: Contains "create", "add", "new", "insert", "generate"
- **Update**: Contains "update", "edit", "modify", "change", "sync"  
- **Send**: Contains "send", "notify", "alert", "email", "message"
- **Monitor**: Contains "monitor", "check", "watch", "track"
- **Backup**: Contains "backup", "export", "archive", "save"

## Implementation Strategy

### Phase 1: Critical Issues (Completed)
- ✅ Fixed 9 broken filenames with incomplete names
- ✅ Created automated renaming tools

### Phase 2: High Impact (In Progress)
- 🔄 Rename 858 generic "workflow_XXX" files
- ⏳ Process in batches of 50 files
- ⏳ Preserve existing ID numbers

### Phase 3: Optimization (Planned)
- ⏳ Standardize 55 hash-only names
- ⏳ Shorten 36 overly long names (>100 chars)
- ⏳ Clean up special characters

### Phase 4: Maintenance
- ⏳ Document new workflow naming guidelines
- ⏳ Create naming validation tools
- ⏳ Update workflow documentation system

## Tools

### Automated Renaming
- **workflow_renamer.py**: Intelligent content-based renaming
- **batch_rename.py**: Controlled batch processing
- **Patterns supported**: generic_workflow, incomplete_names, hash_only, too_long

### Usage Examples
```bash
# Dry run to see what would be renamed
python3 workflow_renamer.py --pattern generic_workflow --report-only

# Execute renames for broken files
python3 workflow_renamer.py --pattern incomplete_names --execute

# Batch process large sets
python3 batch_rename.py generic_workflow 50
```

## Quality Assurance

### Before Renaming
- ✅ Backup original files
- ✅ Test renaming script on small sample
- ✅ Check for naming conflicts
- ✅ Validate generated names

### After Renaming
- ✅ Verify all files still load correctly
- ✅ Update database indexes
- ✅ Test search functionality
- ✅ Generate updated documentation

## Migration Notes

### What Gets Preserved
- ✅ Original file content (unchanged)
- ✅ Existing ID numbers when present
- ✅ Workflow functionality
- ✅ N8n compatibility

### What Gets Improved
- ✅ Filename readability
- ✅ Search discoverability  
- ✅ Organization consistency
- ✅ Documentation quality

## Future Considerations

### New Workflow Guidelines
For creating new workflows:
1. **Use descriptive names** from the start
2. **Follow the established format**: `ID_Service_Purpose.json`
3. **Avoid generic terms** like "workflow", "automation" unless specific
4. **Keep names concise** but meaningful
5. **Use consistent service names** from the mapping table

### Maintenance
- **Monthly review** of new workflows
- **Automated validation** in CI/CD pipeline
- **Documentation updates** as patterns evolve
- **User training** on naming conventions

---

*This naming convention was established during the documentation system optimization project in June 2025.*