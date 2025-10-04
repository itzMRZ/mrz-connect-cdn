# MRZ Connect CDN

Static CDN for course and exam data with auto-updates and backups.

## 🚀 Features

- **96% compression** with gzip (3.4 MB → 137 KB)
- **Auto-updates** every 7 days
- **Semester backups** when exam dates change
- **Free hosting** on GitHub Pages

## 🌐 Live API

```
https://connect-cdn.itzmrz.xyz/connect.json
https://connect-cdn.itzmrz.xyz/exams.json
```

## 💻 Usage

### JavaScript
```javascript
fetch('https://connect-cdn.itzmrz.xyz/connect.json')
  .then(r => r.json())
  .then(data => console.log(data.metadata));
```

### Python
```python
import requests
data = requests.get('https://connect-cdn.itzmrz.xyz/connect.json').json()
print(data['metadata']['totalSections'])
```

## 📊 Data

- **2,100** sections
- **63,061** enrolled students
- **1,907** exam schedules
- Updates automatically every 7 days

## 🔧 Local Setup

```bash
pip install requests
python update_cdn.py
```

## 📄 License

MIT
