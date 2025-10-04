# Automation Guide

This guide explains how the USIS CDN system automatically updates and backs up data on GitHub Pages.

## 🤖 Automated Updates

The system runs **automatically every 7 days** via GitHub Actions, without requiring any manual intervention.

### Schedule
- **Frequency**: Every 7 days
- **Time**: 6:00 AM UTC (12:00 PM Bangladesh Time)
- **Trigger**: Cron schedule `0 6 */7 * *`

### What Happens During Auto-Update

1. **Fetch Fresh Data**: Downloads latest course data from USIS API
2. **Process Data**: Calculates metadata and generates JSON files
3. **Check for Changes**: Compares new data with existing data
4. **Create Backups**: If exam dates changed, creates timestamped backups
5. **Commit Changes**: Commits updated files to repository
6. **Deploy**: GitHub Pages automatically publishes changes

## 📦 Automatic Backup System

### When Backups Are Created

Backups are **automatically created** when:
- The scheduled update detects a change in the **first mid exam start date**
- The workflow compares `metadata.midExamStartDate` between old and new data
- If different, it triggers backup creation

### Backup Naming Format

Backups use the format: `DDMMMYYYY_filename.json`

**Example:**
- Current mid exam start date: `2025-11-01`
- System updates and detects new date: `2025-12-15`
- Backup created: `01Nov2025_connect.json` and `01Nov2025_exams.json`
- The backup name reflects the **OLD date** being replaced

### What Gets Backed Up

Each backup snapshot includes:
1. **Complete Course Data** (`DDMMMYYYY_connect.json`)
   - All sections
   - Full metadata
   - Seat information
   - Class schedules

2. **Exam Schedules** (`DDMMMYYYY_exams.json`)
   - All exam dates
   - Exam times
   - Metadata

### Backup Storage

- **Location**: `backups/` directory in repository
- **Accessibility**: 
  - Web interface: `https://YOUR-USERNAME.github.io/usis-cdn/backups.html`
  - Direct download: `https://YOUR-USERNAME.github.io/usis-cdn/backups/01Nov2025_connect.json`
  - GitHub repository: Browse `backups/` folder
  
## 🎯 Manual Triggers

You can manually trigger an update at any time:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **Update USIS Data** workflow
4. Click **Run workflow** button
5. Select branch (usually `main`) and click **Run workflow**

This is useful for:
- Getting immediate updates outside the 7-day schedule
- Testing the workflow
- Force-creating a backup

## 🔍 Monitoring Updates

### Check Update Status

1. **GitHub Actions Tab**:
   - View all workflow runs
   - See success/failure status
   - Read detailed logs

2. **Commit History**:
   - Each update creates a commit
   - Commit message includes timestamp: `Auto-update data - 2025-10-05 06:00:00 UTC`
   - Review changes in commit diff

3. **Landing Page**:
   - Shows "Last Updated" timestamp
   - Reflects most recent data fetch

### Workflow Logs

To view detailed logs:
1. Go to **Actions** tab
2. Click on a workflow run
3. Expand step details to see:
   - Data fetch status
   - Backup creation messages
   - Commit/push results

Example log output:
```
Old mid exam start date: 2025-11-01
New mid exam start date: 2025-12-15
📅 Mid exam date changed from 2025-11-01 to 2025-12-15
Creating backups...
✓ Backups created: 01Nov2025_connect.json and 01Nov2025_exams.json
```

## 🛠️ Technical Details

### Workflow File Location
`.github/workflows/update-data.yml`

### Key Steps

1. **Checkout Repository**
   ```yaml
   - uses: actions/checkout@v4
     with:
       fetch-depth: 0  # Fetch all history for backup comparison
   ```

2. **Check for Exam Date Changes**
   - Reads old `connect.json`
   - Extracts `midExamStartDate`
   - Stores in environment variable

3. **Run Update Script**
   ```yaml
   - run: python update_cdn.py
   ```

4. **Create Backup If Needed**
   - Compares old vs new mid exam date
   - If changed, creates timestamped backups
   - Retrieves old data using `git show HEAD:filename.json`

5. **Commit and Push**
   - Adds new JSON files
   - Adds backup files (if created)
   - Commits with automated message
   - Pushes to repository

### Environment Variables

The workflow uses GitHub Actions environment:
- `OLD_MID_DATE`: Stores previous mid exam start date
- `NEW_MID_DATE`: Stores current mid exam start date
- `BACKUP_DATE`: Formatted date for backup filenames

## 🔧 Customization

### Change Update Frequency

Edit `.github/workflows/update-data.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 */7 * *'  # Every 7 days
```

**Common schedules:**
- Daily: `0 6 * * *`
- Every 3 days: `0 6 */3 * *`
- Weekly: `0 6 * * 0` (Sundays)
- Monthly: `0 6 1 * *` (1st of each month)

### Disable Backups

To disable automatic backups, comment out the backup step in the workflow:

```yaml
# - name: Create backup if exam dates changed
#   run: |
#     # ... backup logic
```

### Change Backup Trigger

To backup on different conditions, modify the comparison in the workflow:

```yaml
# Backup on final exam date change instead
if [ "$OLD_FINAL_DATE" != "$NEW_FINAL_DATE" ] && [ -n "$NEW_FINAL_DATE" ]; then
```

## 📊 Viewing Backups

### Web Interface
Visit `backups.html` to see a visual grid of all backups with:
- Formatted dates
- Download buttons
- Automatic detection of available backups

### API Access
Access backups programmatically:

```javascript
// Fetch backup
fetch('https://YOUR-USERNAME.github.io/usis-cdn/backups/01Nov2025_connect.json')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 🚨 Troubleshooting

### Updates Not Running

**Check:**
1. Repository is public (required for GitHub Actions on free tier)
2. Actions are enabled in repository settings
3. Workflow file syntax is valid (check Actions tab for errors)

**Fix:**
- Go to Settings > Actions > General
- Ensure "Allow all actions" is enabled
- Check "Read and write permissions" is enabled

### Backups Not Being Created

**Possible causes:**
1. Exam dates haven't changed
2. First run (no previous data to compare)
3. Workflow step failed

**Check workflow logs:**
```
No exam date change detected. Skipping backup.
```
or
```
First run - no backup needed
```

### Push Failures

**If workflow can't push:**
1. Check repository permissions
2. Ensure Actions has write access
3. Verify no branch protection rules block Actions

**Fix:**
- Settings > Actions > General > Workflow permissions
- Select "Read and write permissions"

## 📈 Best Practices

1. **Monitor First Few Runs**: Check Actions tab after initial deployment
2. **Review Backups**: Verify backups are created correctly when dates change
3. **Set Up Notifications**: Configure GitHub to email on workflow failures
4. **Clean Old Backups**: Periodically review and remove very old backups
5. **Test Manual Triggers**: Verify you can manually run updates

## 🎓 Understanding the Schedule

**Cron syntax**: `0 6 */7 * *`

Breaking it down:
- `0` - Minute (0)
- `6` - Hour (6 AM UTC)
- `*/7` - Day of month (every 7 days)
- `*` - Month (any)
- `*` - Day of week (any)

**Why 7 days?**
- Course data typically doesn't change daily
- Reduces API requests and GitHub Actions usage
- Captures most semester changes
- Balances freshness with resource usage

You can adjust to fit your needs!

---

**Questions?** Check the main `README.md` or open an issue on GitHub.
