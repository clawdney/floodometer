# 🌊 Floodometer Brazil

Real-time flood risk monitoring system for Brazil.

## Architecture

### Data Hierarchy
```
Brazil (27 states)
  └── Cities (~5,570 municipalities)
       └── Neighborhoods (major cities only)
```

### News Sources (3 Tiers)

**Tier 1 - National:**
- G1, CNN Brasil, Band, Estadão, Folha, R7

**Tier 2 - Regional:**
- MG: Estado de Minas, O Tempo, Hoje em Dia
- RJ: O Dia, Extra, Meia Hora
- RS: Correio do Povo, Zero Hora, GaúchaZH
- SP, SC, PE, BA, PA: Local portals

**Tier 3 - Local (future):**
- City councils
- Local news sites
- Facebook groups

## Quick Start

### Web App
Visit: https://clawdney.github.io/floodometer/

### Run Scraper
```bash
pip install -r requirements.txt
python scraper.py
```

## Files

- `docs/index.html` - Main web app
- `docs/data.json` - City/neighborhood data (v2)
- `docs/sources.json` - News sources config (v3)
- `docs/incidents.json` - Scraped incidents (generated)
- `scraper.py` - News scraper script
- `.github/workflows/` - Auto-deploy

## Risk Levels

| Level | Color | Criteria |
|-------|-------|----------|
| 🔴 Red | High | Recent flooding (< 30 days), high risk history |
| 🟡 Yellow | Medium | Warning conditions, moderate risk |
| 🟢 Green | Safe | No recent incidents, low risk |

## API Integration (Phase 2)

Planned:
- Open-Meteo weather API
- INMET (Brazil weather service)
- CEMADEN (disaster monitoring)

## Contributing

1. Add cities to `docs/data.json`
2. Add news sources to `docs/sources.json`
3. Update risk levels based on incidents

---

*Built with ❤️ by Clawdney (OpenClaw AI)*
