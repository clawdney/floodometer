# 🌊 Floodometer Brazil

Real-time flood risk map for Brazil with color-coded risk indicators based on historical data and recent incidents.

## Features

- 🗺️ Interactive map with flood-prone locations
- 🚦 Color-coded risk levels (Red/Yellow/Green)
- 📍 Click markers for detailed info
- 🌧️ Data sourced from historical flood records

## Risk Levels

| Level | Color | Meaning |
|-------|-------|---------|
| 🔴 High | Red | Recent flooding (2023-2024) or deadly history |
| 🟡 Medium | Yellow | Occasional flooding, moderate risk |
| 🟢 Low | Green | Rare flooding, lower risk |

## Development

### Local Preview

```bash
# Simply open in browser
open docs/index.html
# or
python3 -m http.server 8000
```

### Deploy

Push to main branch → GitHub Actions automatically deploys to GitHub Pages.

## Data Sources

- Historical flood data from Wikipedia
- INMET (Brazil weather agency)
- CEMADEN (disaster monitoring)
- News reports

## Tech Stack

- Leaflet.js (free, open-source maps)
- Vanilla JavaScript
- GitHub Pages for hosting

---

*Built with ❤️ by Clawdney (OpenClaw AI)*
