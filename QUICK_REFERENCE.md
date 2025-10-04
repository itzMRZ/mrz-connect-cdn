# MRZ Connect CDN - Quick Reference

## 🌐 Live URLs
```
https://connect-cdn.itzmrz.xyz
https://connect-cdn.itzmrz.xyz/connect.json
https://connect-cdn.itzmrz.xyz/exams.json
https://connect-cdn.itzmrz.xyz/backups.html
```

## 📊 File Sizes
```
connect.json:     3.4 MB → 137 KB (96% compressed)
exams.json:       516 KB → 20 KB (96% compressed)
```

## 🔄 Backup Format
```
Format: YYYYMMDD_HHMM_Semester_filename.json
Example: 20251104_1200_Fall2025_connect.json

Semesters:
  Jan-Apr = Spring
  May-Aug = Summer
  Sep-Dec = Fall
```

## 🚀 Deploy Commands
```bash
cd /path/to/usis-cdn
git init
git add .
git commit -m "MRZ Connect CDN"
git branch -M main
git remote add origin https://github.com/USERNAME/mrz-cdn.git
git push -u origin main
```

## 🌍 DNS Configuration
```
Type: CNAME
Name: connect-cdn
Value: USERNAME.github.io
TTL: 3600
```

## 💻 API Usage

### JavaScript
```javascript
const res = await fetch('https://connect-cdn.itzmrz.xyz/connect.json');
const data = await res.json();
console.log(data.metadata.totalSections);
```

### Python
```python
import requests
data = requests.get('https://connect-cdn.itzmrz.xyz/connect.json').json()
print(data['metadata']['totalSections'])
```

### curl
```bash
curl https://connect-cdn.itzmrz.xyz/connect.json
```

## 🎨 UI Colors
```
Background: #0a0a0a
Text: #e0e0e0
Accent 1: #00ff00 (green)
Accent 2: #00aaff (cyan)
Border: #333
```

## 📅 Schedule
```
Updates: Every 7 days at 6 AM UTC
Backups: When mid exam date changes
Current: Fall 2025
```

## 📁 Key Files
```
index.html          - Main landing page
backups.html        - Backup viewer
update_cdn.py       - Data update script
CNAME               - Custom domain config
.github/workflows/  - Automation
```

## 🔧 Common Commands
```bash
# Update data locally
python update_cdn.py

# Check file sizes
Get-ChildItem *.json* | Select Name, Length

# Open in browser
Start-Process index.html

# View backups folder
explorer backups\
```

## 📈 Performance
```
Bandwidth: 25x more requests (gzip)
Speed: 24x faster on mobile
Cost: $0/month forever
```
