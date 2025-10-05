# Smart Backup System

## Overview

The CDN now features an intelligent backup system that automatically manages semester archives with a "current" semester prefix.

## How It Works

### Current Semester Tracking

- **File naming**: `curr_[Semester][Year]_connect.json`
- **Example**: `curr_Fall2025_connect.json`
- **Purpose**: Tracks ongoing semester data with each weekly update

### Automatic Archiving

When exam dates change (indicating a new semester):
1. ✅ Old `curr_` backup is automatically renamed with final exam date
2. ✅ New `curr_` backup is created for the new semester
3. ✅ Archive format: `YYYYMMDD_2359_[Semester][Year]_connect.json`
4. ✅ Example: `20260117_2359_Fall2025_connect.json`

## Backup Types

### 1. Current Semester Backup (`curr_*`)
- **Updates**: Every week (with `update_cdn.py`)
- **Purpose**: Latest data for ongoing semester
- **Naming**: `curr_Fall2025_connect.json`
- **Action**: Overwrites each run until semester ends

### 2. Archived Semester Backups
- **Created**: When new semester starts (exam dates change)
- **Purpose**: Historical record of completed semesters
- **Naming**: `20260117_2359_Fall2025_connect.json`
- **Date**: Final exam end date of the semester
- **Action**: Permanent archive, never overwritten

## File Structure

```
backups/
├── curr_Fall2025_connect.json       # Current ongoing semester
├── 20240831_2359_Summer2024_connect.json
├── 20250123_2359_Fall2024_connect.json
├── 20250531_2359_Spring2025_connect.json
├── 20250831_2359_Summer2025_connect.json
└── 20260117_2359_Fall2025_connect.json  # Will be created when Spring 2026 starts
```

## Semester Detection

Based on mid-exam start date:
- **Spring**: January - April (months 1-4)
- **Summer**: May - August (months 5-8)
- **Fall**: September - December (months 9-12)

## Example Timeline

### Week 1 (Fall 2025 starts):
```
backups/
└── curr_Fall2025_connect.json  (created)
```

### Weeks 2-15 (During Fall 2025):
```
backups/
└── curr_Fall2025_connect.json  (updated weekly)
```

### Week 16 (Spring 2026 starts - exam dates change):
```
backups/
├── 20260117_2359_Fall2025_connect.json  (archived)
└── curr_Spring2026_connect.json         (new current)
```

## Benefits

### ✅ Storage Efficient
- Only one "current" backup instead of 15+ weekly backups per semester
- Automatic cleanup when semester ends

### ✅ Smart Archiving
- Archives created exactly when semester ends (using final exam date)
- No manual intervention needed
- Clear historical record

### ✅ Developer Friendly
- Current semester always at `curr_[Semester]_connect.json`
- Easy to find latest data
- Historical data properly dated

## Usage Examples

### Access Current Semester
```javascript
fetch('https://connect-cdn.itzmrz.xyz/backups/curr_Fall2025_connect.json')
  .then(r => r.json())
  .then(data => console.log('Current semester data:', data));
```

### Access Historical Semester
```javascript
fetch('https://connect-cdn.itzmrz.xyz/backups/20250831_2359_Summer2025_connect.json')
  .then(r => r.json())
  .then(data => console.log('Summer 2025 archive:', data));
```

### List All Backups
```bash
# Current semester
ls backups/curr_*

# All archives
ls backups/20*
```

## Automation

### Weekly Update (GitHub Actions)
```yaml
# Runs every 7 days
- Fetches latest data
- Updates curr_[Semester]_connect.json
- Archives old semester if exam dates changed
- Commits and pushes automatically
```

### Manual Run
```bash
python update_cdn.py
```

## Maintenance

### Zero Maintenance Required!
- Backups created automatically
- Archives renamed automatically
- Old "current" backups cleaned up automatically
- All handled by `update_cdn.py`

## Migration from Old System

Old backups with timestamp format are preserved:
```
20251005_0518_Fall2025_connect.json  # Old format
20260117_2359_Fall2025_connect.json  # New format (using final exam date)
```

Both formats work fine in the backups.html viewer.

## Technical Details

### Functions (in update_cdn.py)

1. **`get_current_semester(mid_exam_start)`**
   - Determines semester from exam date
   - Returns: "Spring2025", "Summer2025", "Fall2025"

2. **`manage_current_backup(metadata, sections)`**
   - Checks for existing `curr_*` backup
   - Compares exam dates
   - Archives old backup if semester changed
   - Creates/updates current backup

### Workflow Integration

The GitHub Actions workflow now:
- Runs `python update_cdn.py` (handles everything)
- Commits both current and archived backups
- No manual backup logic needed

## Benefits Over Old System

| Feature | Old System | New System |
|---------|------------|------------|
| Weekly backups | 15+ per semester | 1 per semester |
| Manual archiving | Yes | Automatic |
| Storage usage | High | Low |
| Find current data | Search by date | `curr_*` prefix |
| Archive naming | Random timestamp | Final exam date |

## Troubleshooting

### If curr_ backup is missing:
Run `python update_cdn.py` - it will be created

### If semester not detected:
Check that mid_exam_start date is valid in connect.json

### If archiving not working:
Verify final_exam_end date exists in metadata

---

**Status**: ✅ Fully Automated & Production Ready
