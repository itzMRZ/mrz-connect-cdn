# Backups Directory

This directory contains historical snapshots of USIS course data, automatically created when exam dates change.

## 📅 Backup Naming Convention

Backups are named using the format: `DDMMMYYYY_filename.json`

**Examples:**
- `05Oct2025_connect.json` - Full course data backed up on October 5, 2025
- `05Oct2025_exams.json` - Exam schedules backed up on October 5, 2025
- `15Nov2025_connect.json` - Full course data backed up on November 15, 2025

The date represents the **old mid exam start date** before it was changed.

## 🔄 How Backups Are Created

Backups are automatically created by GitHub Actions when:
1. The scheduled update runs (every 7 days)
2. The first mid exam start date changes from the previous value
3. The workflow detects the change and creates a backup of the **old data**

## 📂 What's Backed Up

Each backup snapshot includes:
- **`DDMMMYYYY_connect.json`**: Complete section data with all course information
- **`DDMMMYYYY_exams.json`**: Exam schedules for all courses

## 🌐 Accessing Backups

### Via Web Interface
Visit `backups.html` on the main site to browse and download backups.

### Direct URL Access
```
https://YOUR-USERNAME.github.io/usis-cdn/backups/05Oct2025_connect.json
https://YOUR-USERNAME.github.io/usis-cdn/backups/05Oct2025_exams.json
```

### Via GitHub
Browse this directory on GitHub to view all available backups.

## 📊 Use Cases

Backups are useful for:
- **Historical analysis**: Compare exam dates across semesters
- **Data recovery**: Restore previous data if needed
- **Change tracking**: See how course offerings evolved over time
- **Research**: Analyze patterns in scheduling and enrollment

## 🗑️ Retention Policy

Currently, backups are retained indefinitely. You may want to:
- Manually delete old backups to save space
- Keep only the most recent N backups
- Archive backups older than X months

## 🔧 Technical Details

- Backups are created by `.github/workflows/update-data.yml`
- The workflow compares `metadata.midExamStartDate` between runs
- Old data is retrieved from the previous Git commit using `git show HEAD:filename.json`
- Backups are committed to the repository along with new data

## 📝 Notes

- Empty directory initially - backups appear after first exam date change
- All times are in UTC
- Backup creation is logged in GitHub Actions workflow runs
- Manual backups can be created by running the workflow manually from the Actions tab

---

**Last Updated**: January 2025
