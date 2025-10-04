# MRZ Connect CDN

Course and exam data API with automatic updates and backups.

## Links

- **Website**: https://connect-cdn.itzmrz.xyz/
- **Backups**: https://connect-cdn.itzmrz.xyz/backups.html
- **GitHub**: https://github.com/itzmrz/mrz-connect-cdn
- **Source Data**: https://usis-cdn.eniamza.com/connect.json

## API Endpoints

```
https://connect-cdn.itzmrz.xyz/connect.json      (~3.4 MB, gzipped to 137 KB)
https://connect-cdn.itzmrz.xyz/exams.json        (~516 KB, gzipped to 20 KB)
```

## Usage

### Regular Files

**JavaScript:**
```js
fetch('https://connect-cdn.itzmrz.xyz/connect.json')
  .then(r => r.json())
  .then(data => console.log(data.metadata));
```

**Python:**
```python
import requests
data = requests.get('https://connect-cdn.itzmrz.xyz/connect.json').json()
print(data['metadata']['totalSections'])
```

### Gzipped Files (96% smaller, faster)

**JavaScript:**
```js
fetch('https://connect-cdn.itzmrz.xyz/connect.json.gz')
  .then(r => r.blob())
  .then(blob => blob.stream().pipeThrough(new DecompressionStream('gzip')))
  .then(stream => new Response(stream).json())
  .then(data => console.log(data.metadata));
```

**Python:**
```python
import requests, gzip, json
r = requests.get('https://connect-cdn.itzmrz.xyz/connect.json.gz')
data = json.loads(gzip.decompress(r.content))
print(data['metadata']['totalSections'])
```

## Features

- Auto-updates every 7 days via GitHub Actions
- Automatic semester-based backups when exam dates change
- Gzip compression (96% size reduction)
- Free hosting on GitHub Pages

## Run Locally

```bash
pip install requests
python update_cdn.py
```

## Credits

Data source provided by [@eniamza](https://github.com/eniamza) via [usis-cdn.eniamza.com](https://usis-cdn.eniamza.com/connect.json)

## License

MIT
