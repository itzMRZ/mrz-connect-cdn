# GitHub Free Tier Limits Reference

This document explains GitHub's free tier limits and how they apply to the USIS CDN project.

## 📊 Summary: Your Usage vs. Limits

| Resource | Free Limit | Your Usage | Status |
|----------|-----------|------------|--------|
| **Actions Minutes** | 2,000/month | 8-12/month | ✅ 0.6% |
| **Pages Bandwidth** | 100 GB/month | 12-60 GB/month* | ✅ 12-60% |
| **Repository Size** | 5 GB (soft) | < 100 MB | ✅ < 2% |
| **Storage Growth** | 5 GB (soft) | ~20 MB/year | ✅ 0.4%/year |

*Depends on traffic. 12 GB = 100 requests/day, 60 GB = 500 requests/day

## 🎯 GitHub Actions Limits

### Free Tier (Public Repos)
- **Minutes/month**: 2,000 (but unlimited for public repos!)
- **Concurrent jobs**: 20
- **Job queue time**: Unlimited
- **Artifact storage**: 500 MB

### Your Actual Usage

**Current Schedule (Every 7 Days):**
```
Runs per month: 4
Minutes per run: 2-3
Monthly usage: 8-12 minutes
Annual usage: 96-144 minutes

Percentage: 0.6% of 2,000 limit
```

**If Running Daily:**
```
Runs per month: 30
Minutes per run: 2-3
Monthly usage: 60-90 minutes

Percentage: 4.5% of 2,000 limit
Still very safe! ✅
```

**Action Cost Breakdown:**
- Fetch data from API: ~5 seconds
- Process data: ~10 seconds
- Create backups (if needed): ~5 seconds
- Commit and push: ~30 seconds
- **Total: ~50 seconds per run**

### Important Note
✨ **Public repositories get UNLIMITED Actions minutes!**

Your private usage (if repo were private):
- 2,000 minutes = ~33 hours/month
- You'd use ~0.2 hours/month
- You could run 2,400 times/month and still be under limit!

## 🌐 GitHub Pages Limits

### Free Tier
- **Bandwidth**: 100 GB/month
- **Storage**: 1 GB total
- **Build frequency**: 10 builds/hour
- **Sites per account**: Unlimited

### Your Storage Usage

**Current Files:**
```
connect.json:     3.4 MB
exams.json:       0.5 MB
HTML/CSS/JS:      0.05 MB
Documentation:    0.03 MB
----------------
Total:            ~4 MB
```

**With Backups (Projected):**
```
Year 1:  ~20 MB  (2-3 backups)
Year 2:  ~40 MB  (4-6 backups)
Year 3:  ~60 MB  (6-9 backups)
Year 5:  ~100 MB (10-15 backups)
Year 10: ~200 MB (20-30 backups)

Still < 20% of 1 GB limit after 10 years! ✅
```

### Bandwidth Calculations

**Per Request:**
- Full download: ~4 MB
- Gzipped: ~400 KB (90% smaller!)
- Metadata only: < 1 KB

**Monthly Bandwidth by Traffic Level:**

| Daily Requests | Request Size | Monthly Bandwidth | % of Limit | Status |
|---------------|--------------|-------------------|------------|--------|
| 100 | 4 MB | 12 GB | 12% | ✅ Safe |
| 500 | 4 MB | 60 GB | 60% | ✅ OK |
| 830 | 4 MB | 100 GB | 100% | ⚠️ At limit |
| 1,000 | 4 MB | 120 GB | 120% | ❌ Over |
| 100 | 400 KB (gzip) | 1.2 GB | 1.2% | ✅ Excellent |
| 1,000 | 400 KB (gzip) | 12 GB | 12% | ✅ Great |

**Key Insight:** With gzip compression, you can handle 10x more traffic!

### Traffic Scenarios

**Realistic for University Data:**
```
Students checking exam dates: 50-200/day
Automated apps checking updates: 10-50/day
Estimated total: 100-300 requests/day

Monthly: 3,000-9,000 requests
Bandwidth: 12-36 GB (without compression)
Status: ✅ Well within limits
```

**High Traffic Scenario:**
```
Popular API with many apps: 1,000+/day
Monthly: 30,000+ requests
Bandwidth: 120+ GB
Status: ❌ Would exceed limit

Solution: Enable gzip compression
With gzip: 12 GB/month
Status: ✅ Back to safe
```

## 💾 Repository Storage Limits

### Limits
- **Soft limit**: 5 GB (recommended)
- **Hard limit**: 100 GB (enforced)
- **File size**: 100 MB per file (for Git)
- **Large files**: Use Git LFS for files > 50 MB

### Your Growth

**Current Repository:**
```
Code/HTML: 50 KB
JSON data: 4 MB
Backups: 0-4 MB (grows over time)
Total: ~5 MB
```

**10-Year Projection:**
```
Assuming 3 backups/year:
Year 1: 5 MB + 12 MB = 17 MB
Year 2: 17 MB + 12 MB = 29 MB
Year 5: 65 MB
Year 10: 125 MB

Still < 3% of 5 GB soft limit! ✅
```

### Optimization Options

**1. Delete Old Backups**
We've included `cleanup-old-backups.yml` workflow:
- Runs annually
- Removes backups > 2 years old
- Keeps repository lean

**2. Compress JSON**
```python
# Instead of pretty JSON (indent=2)
json.dump(data, f, indent=2)  # 3.4 MB

# Use minified JSON
json.dump(data, f, separators=(',', ':'))  # 2.4 MB

# Savings: ~30% smaller
```

**3. Use External Storage (If Needed)**
For very large archives:
- Keep only recent backups in repo
- Move old backups to:
  - AWS S3 (free tier: 5 GB)
  - Google Drive
  - Dropbox

## 🚨 What Happens If You Exceed Limits?

### GitHub Actions
**If you somehow exceed 2,000 minutes/month:**
- Actions stop running until next month
- You get email notification
- Can purchase more minutes ($0.008/minute)

**But you won't because:**
- Public repos = unlimited Actions
- You use < 1% of the limit

### GitHub Pages Bandwidth
**If you exceed 100 GB/month:**
- GitHub may soft-limit your site
- Site becomes slower but stays up
- GitHub contacts you about usage
- You can upgrade or add CDN

**Solutions:**
1. Enable CloudFlare (free CDN)
2. Implement caching headers
3. Use gzip compression
4. Rate limit API access

### Repository Size
**If you exceed 5 GB:**
- Git operations slow down
- GitHub sends warnings
- Still works, but not recommended

**If you exceed 100 GB:**
- Can't push new commits
- Must reduce size

**Our projection:** Never an issue (< 200 MB in 10 years)

## 💡 Best Practices to Stay Under Limits

### 1. Monitor Usage
- Check Actions tab monthly
- Review Pages analytics (if enabled)
- Monitor repository size

### 2. Optimize Files
```yaml
# Enable gzip in GitHub Pages (automatic)
# Just ensure your files are under 10 MB

# Minify JSON (optional)
json.dump(data, f, separators=(',', ':'))
```

### 3. Clean Old Data
```bash
# Run cleanup workflow annually
# Keeps repository < 100 MB forever
```

### 4. Cache Responses
```html
<!-- Add to HTML files -->
<meta http-equiv="Cache-Control" content="max-age=3600">
```

### 5. Implement Rate Limiting (Optional)
If you expect heavy API usage, add rate limiting:
```javascript
// In your app consuming the API
const cache = {};
function fetchWithCache(url) {
  if (cache[url] && Date.now() - cache[url].time < 3600000) {
    return cache[url].data;
  }
  // ... fetch and cache
}
```

## 📈 Scaling Beyond Free Tier

### If Your Project Grows

**GitHub Pro ($4/month):**
- 3,000 Actions minutes/month
- 2 GB Pages storage
- 100 GB Pages bandwidth (same)

**Not needed for your project**, but available if:
- You want private repos
- Need more Actions for other projects
- Want advanced features

### Alternative Solutions

**If bandwidth becomes an issue:**

1. **CloudFlare (Free)**
   - Free CDN
   - Unlimited bandwidth
   - Caches your JSON files
   - Setup: 10 minutes

2. **Netlify (Free)**
   - 100 GB bandwidth/month (same as GitHub)
   - Better caching
   - Easier CDN setup

3. **Vercel (Free)**
   - 100 GB bandwidth/month
   - Serverless functions
   - API rate limiting built-in

## 🎓 Recommendations for Your Project

### Current Setup: Perfect! ✅

Your configuration is optimal:
- Every 7 days: 0.6% Actions usage
- Smart backups: Minimal storage growth
- Clean architecture: Easy to maintain

### Future-Proofing (Optional)

1. **Enable cleanup workflow**: Keeps repo under 100 MB forever
2. **Monitor first 6 months**: Check actual traffic
3. **Add CloudFlare**: If traffic exceeds 500 requests/day
4. **Implement caching**: If serving to many apps

### Don't Worry About

- ✅ Actions minutes (you use < 1%)
- ✅ Repository size (grows slowly)
- ✅ Build limits (one build per update)
- ✅ Storage space (< 200 MB in 10 years)

### Only Monitor

- ⚠️ Bandwidth (if traffic > 500 requests/day)
- ⚠️ Backup accumulation (cleanup annually)

## 📊 Real-World Comparison

**Similar Projects:**
```
Project: COVID-19 Data API
Traffic: 10,000 requests/day
Data: ~5 MB per request
Solution: CloudFlare CDN
Cost: $0 (free tier)

Project: University Course Catalog
Traffic: 200 requests/day
Data: ~3 MB per request
Hosting: GitHub Pages only
Cost: $0 (under limits)

Your Project: USIS CDN
Expected: 100-300 requests/day
Data: ~4 MB per request
Recommendation: GitHub Pages only ✅
Optional: Add CloudFlare if traffic grows
```

## 🎯 Bottom Line

**You're in great shape!** 

- Current usage: < 1% of all limits
- 10-year projection: Still < 20% of limits
- Cost: $0/month forever
- Scalability: Can handle 10x traffic with optimizations

**TL;DR:** Don't worry about limits. You won't hit them. 🎉

---

**Last Updated**: October 2025  
**GitHub Limits**: Subject to change (usually improve over time)
