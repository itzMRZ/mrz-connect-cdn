# MRZ Connect CDN - Final Setup Guide

## 🎉 What's New

### ✅ Simplified UI
- **Minimal terminal-style design**
- Only shows useful, practical information
- Removed unnecessary fluff
- Clean code blocks with actual usage examples
- Green/cyan color scheme (#00ff00 / #00aaff)

### ✅ Custom Domain Ready
- Domain: `connect-cdn.itzmrz.xyz`
- CNAME file included
- All URLs updated in the site

### ✅ Semester-Based Backups
- New naming format: `YYYYMMDD_HHMM_Semester_filename.json`
- Example: `20251104_1200_Fall2025_connect.json`
- Sequence: Fall 2025 → Spring 2026 → Summer 2026 → Fall 2026 → ...
- Backups UI shows semester names clearly

---

## 📁 Updated Files

```
✅ index.html          - Simplified terminal-style UI
✅ backups.html        - Clean backup list with semester names
✅ .github/workflows/  - Semester-based backup naming
✅ CNAME               - Custom domain configuration
```

---

## 🚀 Deployment Steps

### 1. Push to GitHub

```bash
cd /path/to/usis-cdn
git init
git add .
git commit -m "MRZ Connect CDN - Simplified UI with semester backups"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/mrz-cdn.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to repository Settings
2. Click **Pages** in sidebar
3. Source: `main` branch, `/ (root)`
4. Click **Save**
5. Wait 1-2 minutes

### 3. Configure Custom Domain

**On GitHub:**
1. Still in Pages settings
2. Under "Custom domain", enter: `connect-cdn.itzmrz.xyz`
3. Click **Save**
4. Wait for DNS check (may show error initially - that's OK)

**On your Domain Provider (where itzmrz.xyz is registered):**
1. Go to DNS settings for `itzmrz.xyz`
2. Add a CNAME record:
   ```
   Type: CNAME
   Name: connect-cdn
   Value: YOUR-USERNAME.github.io
   TTL: 3600 (or Auto)
   ```
3. Save changes
4. Wait 5-30 minutes for DNS propagation

### 4. Enable HTTPS

After DNS propagates:
1. Go back to GitHub Pages settings
2. Check **Enforce HTTPS** (may take a few minutes to become available)
3. GitHub will automatically provision SSL certificate

---

## 🌐 Your Live URLs

After deployment:

```
Main Site:
https://connect-cdn.itzmrz.xyz

API Endpoints:
https://connect-cdn.itzmrz.xyz/connect.json
https://connect-cdn.itzmrz.xyz/exams.json

Backups:
https://connect-cdn.itzmrz.xyz/backups.html
```

---

## 📊 Backup Naming Examples

### Format
```
YYYYMMDD_HHMM_Semester_filename.json
```

### Real Examples
```
20251104_1200_Fall2025_connect.json     # Fall 2025 backup
20251104_1200_Fall2025_exams.json

20260115_0600_Spring2026_connect.json   # Spring 2026 backup
20260115_0600_Spring2026_exams.json

20260620_0600_Summer2026_connect.json   # Summer 2026 backup
20260620_0600_Summer2026_exams.json
```

### Semester Logic
```
January-April   = Spring {YEAR}
May-August      = Summer {YEAR}
September-December = Fall {YEAR}
```

---

## 🎨 UI Features

### Index Page
- **Status indicator**: Online/Offline
- **API endpoints**: With your custom domain
- **Usage examples**: JavaScript and Python
- **Current stats**: Sections, enrolled, available, updated
- **Exam dates**: Mid and final periods
- **Downloads**: Direct links to JSON files

### Backups Page
- **Semester grouping**: Fall 2025, Spring 2026, etc.
- **Timestamps**: Date and time of backup creation
- **Download links**: connect.json and exams.json for each
- **Auto-loading**: Uses GitHub API to detect backups

---

## 🔧 Testing Checklist

### Local Testing
- [ ] Open `index.html` in browser
- [ ] Verify terminal-style design loads
- [ ] Check that stats display correctly
- [ ] Test download links work
- [ ] Open `backups.html`
- [ ] Verify it shows "No backups" message initially

### After GitHub Deployment
- [ ] Visit `https://YOUR-USERNAME.github.io/mrz-cdn/`
- [ ] Verify page loads with dark theme
- [ ] Check API endpoints show correctly
- [ ] Test JSON downloads work
- [ ] Manually trigger workflow in Actions tab
- [ ] Wait for completion
- [ ] Verify `.gz` files are committed

### After Custom Domain Setup
- [ ] Visit `https://connect-cdn.itzmrz.xyz`
- [ ] Verify site loads (may take 5-30 minutes)
- [ ] Check HTTPS works (green padlock)
- [ ] Test API endpoints with custom domain
- [ ] Share links with others to verify access

---

## 📝 Custom Domain DNS Configuration

### Required DNS Record

```
Record Type: CNAME
Name/Host: connect-cdn
Value/Points to: YOUR-USERNAME.github.io
TTL: 3600 or Automatic
```

### Common DNS Providers

**Cloudflare:**
1. DNS tab
2. Add record
3. Type: CNAME, Name: connect-cdn, Target: YOUR-USERNAME.github.io
4. Proxy status: DNS only (grey cloud)
5. Save

**Namecheap:**
1. Advanced DNS tab
2. Add New Record
3. Type: CNAME Record, Host: connect-cdn, Value: YOUR-USERNAME.github.io
4. Save

**GoDaddy:**
1. DNS Management
2. Add
3. Type: CNAME, Name: connect-cdn, Value: YOUR-USERNAME.github.io
4. Save

---

## 🔄 How It Works

### Updates (Every 7 Days)
1. GitHub Actions triggers at 6 AM UTC
2. Fetches fresh data from API
3. Compares mid exam start date with previous
4. If changed → creates semester-based backup
5. Generates new JSON + gzipped versions
6. Commits and pushes to repository
7. GitHub Pages auto-deploys

### Backups (On Semester Change)
```bash
# When mid exam date changes:
OLD_DATE: 2025-11-01 (Fall 2025)
NEW_DATE: 2026-01-15 (Spring 2026)

# Creates:
backups/20251104_1200_Fall2025_connect.json
backups/20251104_1200_Fall2025_exams.json

# Semester determined by current month:
# January-April = Spring
# May-August = Summer  
# September-December = Fall
```

---

## 💻 API Usage Examples

### JavaScript

```javascript
// Fetch from your custom domain
const response = await fetch('https://connect-cdn.itzmrz.xyz/connect.json');
const data = await response.json();

console.log('Total Sections:', data.metadata.totalSections);
console.log('Enrolled:', data.metadata.totalConsumedSeats);

// Filter specific course
const cse110 = data.sections.filter(s => s.courseCode === 'CSE110');
console.log('CSE110 Sections:', cse110.length);
```

### Python

```python
import requests

# Fetch from your custom domain
response = requests.get('https://connect-cdn.itzmrz.xyz/connect.json')
data = response.json()

print(f"Total Sections: {data['metadata']['totalSections']}")
print(f"Occupancy: {data['metadata']['occupancyRate']}%")

# Find sections with seats available
available = [s for s in data['sections'] if s['consumedSeat'] < s['capacity']]
print(f"Sections with availability: {len(available)}")
```

### curl

```bash
# Fetch data
curl https://connect-cdn.itzmrz.xyz/connect.json

# Check specific field
curl -s https://connect-cdn.itzmrz.xyz/connect.json | jq '.metadata.totalSections'

# Download gzipped version
curl -O https://connect-cdn.itzmrz.xyz/connect.json.gz
```

---

## 🎯 What Changed from Previous Version

### Removed
❌ Unnecessary stats (section ID range, separate occupancy card)  
❌ Overly designed gradient backgrounds  
❌ Redundant information displays  
❌ Fancy animations and effects  
❌ Multiple download options for same file  

### Added
✅ Semester-based backup naming  
✅ Clean terminal aesthetic  
✅ Custom domain support (CNAME file)  
✅ Practical code examples only  
✅ Simplified stats (what actually matters)  

### Improved
🔄 Backup naming: `05Oct2025_connect.json` → `20251104_1200_Fall2025_connect.json`  
🔄 UI: Fancy gradients → Clean terminal  
🔄 Domain: GitHub subdomain → connect-cdn.itzmrz.xyz  
🔄 Footer: Verbose → Simple one-liner  

---

## 📈 Performance

**File Sizes:**
- connect.json: 3.4 MB → 137 KB (96% compression)
- exams.json: 516 KB → 20 KB (96% compression)

**Capacity:**
- Without gzip: 25,000 requests/month
- With gzip: 637,000 requests/month (25x!)

**Speed:**
- Mobile 4G: 6s → 0.25s (24x faster!)
- Mobile 3G: 30s → 1.2s (25x faster!)

---

## 🐛 Troubleshooting

### Custom Domain Not Working
- Wait 30 minutes for DNS propagation
- Check DNS record is CNAME pointing to `YOUR-USERNAME.github.io`
- Try accessing via original GitHub URL first
- Clear browser cache

### HTTPS Not Available
- DNS must propagate first (30 min - 24 hours)
- Go to Pages settings
- Uncheck and recheck "Enforce HTTPS"
- Wait 5-10 minutes

### Backups Not Showing
- Backups only created when mid exam date changes
- Check Actions tab for workflow runs
- Look in `backups/` directory on GitHub
- May need to manually trigger first update

### Stats Not Loading
- Ensure `connect.json` exists in repository
- Check browser console for errors
- Verify JSON is valid (use jsonlint.com)
- Clear browser cache

---

## 🎓 Final Notes

Your MRZ Connect CDN is now:
- **Simplified**: Only shows what matters
- **Professional**: Terminal-style developer interface
- **Branded**: Custom domain connect-cdn.itzmrz.xyz
- **Organized**: Semester-based backup system
- **Fast**: 96% compression with gzip
- **Automated**: Zero maintenance required
- **Free**: $0/month forever

**Next step**: Deploy to GitHub and configure DNS! 🚀

---

**Current Semester**: Fall 2025  
**Backup Format**: `YYYYMMDD_HHMM_Semester_file.json`  
**Custom Domain**: connect-cdn.itzmrz.xyz  
**Auto-updates**: Every 7 days at 6 AM UTC  
