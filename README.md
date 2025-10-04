# MRZ Connect CDN

Static CDN serving course and exam data with automatic updates and intelligent backups.

## 🚀 Quick Start

```bash
# Install dependencies
pip install requests

# Generate data files
python update_cdn.py

# Open index.html in browser
open index.html
```

## 📊 File Sizes

| File | Regular | Gzipped | Compression |
|------|---------|---------|-------------|
| connect.json | 3.4 MB | 137 KB | **96%** |
| exams.json | 516 KB | 20 KB | **96.2%** |

GitHub Pages automatically serves `.gz` versions when browsers support it (all modern browsers do).

## 🌐 API Endpoints

Once deployed:
```
https://YOUR-USERNAME.github.io/mrz-cdn/connect.json
https://YOUR-USERNAME.github.io/mrz-cdn/connect.json.gz      (auto-served)
https://YOUR-USERNAME.github.io/mrz-cdn/exams.json
https://YOUR-USERNAME.github.io/mrz-cdn/exams.json.gz        (auto-served)
```

## 📦 Data Structure

### connect.json

```json
{
  "metadata": {
    "lastUpdated": "2025-10-04T22:00:00+00:00",
    "totalSections": 2100,
    "totalConsumedSeats": 63061,
    "totalEmptySeats": 4791,
    "occupancyRate": 92.9,
    "midExamStartDate": "2025-11-01",
    "midExamEndDate": "2025-11-23",
    "finalExamStartDate": "2025-12-05",
    "finalExamEndDate": "2026-01-17"
  },
  "sections": [...]
}
```

### exams.json

```json
{
  "metadata": {
    "lastUpdated": "2025-10-04T22:00:00+00:00",
    "totalExams": 1907,
    "midExamStartDate": "2025-11-01",
    "finalExamStartDate": "2025-12-05"
  },
  "exams": [
    {
      "courseCode": "CSE110",
      "sectionName": "01",
      "sectionId": 178770,
      "midExamDate": "2025-11-05",
      "midExamTime": "10:00 AM",
      "finalExamDate": "2025-12-10",
      "finalExamTime": "02:00 PM"
    }
  ]
}
```

## 💻 Usage Examples

### JavaScript

```javascript
// Fetch data (browser automatically requests .gz if available)
const response = await fetch('https://username.github.io/mrz-cdn/connect.json');
const data = await response.json();

console.log(`Total sections: ${data.metadata.totalSections}`);
console.log(`Occupancy: ${data.metadata.occupancyRate}%`);
```

### Python

```python
import requests

response = requests.get('https://username.github.io/mrz-cdn/connect.json')
data = response.json()

print(f"Total sections: {data['metadata']['totalSections']}")
```

### curl

```bash
# Get regular JSON
curl https://username.github.io/mrz-cdn/connect.json

# Get gzipped version (auto-decompressed by curl)
curl https://username.github.io/mrz-cdn/connect.json.gz | gunzip
```

## 🔄 Automation

### Schedule
- Runs every **7 days** at 6 AM UTC
- Manual trigger available via GitHub Actions

### Backups
- Automatically created when first mid exam date changes
- Named format: `DDMMMYYYY_filename.json` (e.g., `01Nov2025_connect.json`)
- Stored in `backups/` directory
- Accessible via `backups.html`

### Workflow

```yaml
# .github/workflows/update-data.yml
- Fetch fresh data from API
- Compare mid exam dates
- Create backups if dates changed
- Generate JSON + gzipped versions
- Commit and push to GitHub
- GitHub Pages auto-deploys
```

## 📈 Benefits of Gzip

### Bandwidth Savings

**Without gzip:**
- File size: 3.9 MB per request
- 100 GB limit = ~25,000 requests/month

**With gzip:**
- File size: 157 KB per request
- 100 GB limit = ~637,000 requests/month

**25x more requests within free tier!**

### Speed Improvements

| Connection | Regular | Gzipped |
|------------|---------|---------|
| Fiber (100 Mbps) | 0.3s | 0.01s |
| Broadband (10 Mbps) | 3s | 0.12s |
| Mobile 4G (5 Mbps) | 6s | 0.25s |
| Mobile 3G (1 Mbps) | 30s | 1.2s |

## 🚀 Deployment

### 1. Create GitHub Repo

```bash
cd /path/to/usis-cdn
git init
git add .
git commit -m "Initial commit: MRZ Connect CDN"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/mrz-cdn.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Repository → Settings → Pages
2. Source: `main` branch, `/ (root)` folder
3. Save

### 3. Access Your CDN

```
https://YOUR-USERNAME.github.io/mrz-cdn/
```

## 🛠️ Customization

### Change Update Frequency

Edit `.github/workflows/update-data.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'      # Daily
  - cron: '0 6 */3 * *'    # Every 3 days
  - cron: '0 6 */7 * *'    # Every 7 days (current)
```

### Disable Gzip

Edit `update_cdn.py` and remove the gzip generation section.

## 📊 GitHub Free Tier

| Resource | Limit | Usage | Status |
|----------|-------|-------|--------|
| Actions Minutes | 2,000/month | 8-12/month | ✅ 0.6% |
| Pages Bandwidth | 100 GB/month | 1-5 GB/month | ✅ 1-5% |
| Repository Size | 5 GB | < 200 MB | ✅ < 4% |

**With gzip, you can handle 8,000+ requests/day within free limits.**

## 📝 Files

```
├── .github/
│   └── workflows/
│       ├── update-data.yml          # Auto-update + backups
│       └── cleanup-old-backups.yml  # Annual cleanup
├── backups/                         # Historical snapshots
│   └── README.md
├── connect.json                     # Full data (3.4 MB)
├── connect.json.gz                  # Compressed (137 KB)
├── exams.json                       # Exam schedules (516 KB)
├── exams.json.gz                    # Compressed (20 KB)
├── index.html                       # Dark theme landing page
├── backups.html                     # Backup viewer
├── update_cdn.py                    # Data update script
└── README.md                        # This file
```

## 🔧 Troubleshooting

### Script fails
- Check Python version (3.6+)
- Install requests: `pip install requests`

### Gzipped files not serving
- Ensure `.gz` files are committed
- Clear browser cache
- Check GitHub Actions logs

### Bandwidth exceeded
- Check GitHub Pages analytics
- Consider adding CloudFlare CDN (free)
- Implement rate limiting

## 📚 Documentation

- [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Detailed automation docs
- [DEPLOYMENT.md](DEPLOYMENT.md) - Step-by-step deployment
- [GITHUB_LIMITS.md](GITHUB_LIMITS.md) - Free tier limits explained
- [backups/README.md](backups/README.md) - Backup system docs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

Open source for educational purposes.

---

**Built with ❤️ for developers** • Auto-updates every 7 days • 96% smaller with gzip
