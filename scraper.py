#!/usr/bin/env python3
"""Fetch AccuWeather alerts for Brazilian cities."""

import requests
import json
import re
from datetime import datetime

# City codes mapping
CITIES = {
    "Porto Alegre": {"lat": -30.0346, "lng": -51.2177, "code": "4564"},
    "Canoas": {"lat": -29.9177, "lng": -51.1836, "code": "4571"},
    "Lajeado": {"lat": -29.1167, "lng": -51.9667, "code": "126769"},
    "Rio de Janeiro": {"lat": -22.9068, "lng": -43.1729, "code": "4544"},
    "Niterói": {"lat": -22.8833, "lng": -43.1036, "code": "10733"},
    "São Paulo": {"lat": -23.5505, "lng": -46.6333, "code": "45881"},
    "Campinas": {"lat": -22.9099, "lng": -47.0626, "code": "45883"},
    "Belo Horizonte": {"lat": -19.9167, "lng": -43.9345, "code": "4607"},
    "Curitiba": {"lat": -25.4284, "lng": -49.2733, "code": "4611"},
    "Recife": {"lat": -8.0476, "lng": -34.877, "code": "4245"},
    "Salvador": {"lat": -12.9714, "lng": -38.5014, "code": "4242"},
    "Fortaleza": {"lat": -3.7172, "lng": -38.5433, "code": "4243"},
    "Manaus": {"lat": -3.119, "lng": -60.0217, "code": "3944"},
    "Brasília": {"lat": -15.8267, "lng": -47.9218, "code": "15482"},
    "Vitória": {"lat": -20.3155, "lng": -40.3128, "code": "4605"},
    "Goiânia": {"lat": -16.6799, "lng": -49.255, "code": "8108"},
    "Natal": {"lat": -5.7945, "lng": -35.211, "code": "4256"},
    "Belém": {"lat": -1.4558, "lng": -48.5039, "code": "4238"},
    "Florianópolis": {"lat": -27.5954, "lng": -48.548, "code": "4622"},
    "Blumenau": {"lat": -26.9194, "lng": -49.0661, "code": "10236"},
}

def fetch_alerts(city_name, code):
    """Fetch AccuWeather page and check for flood alerts."""
    url = f"https://www.accuweather.com/en/br/{city_name.lower().replace(' ', '-')}/{code}/weather-forecast/{code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        text = resp.text
        
        # Check for hasAlerts
        has_alerts = '"hasAlerts":true' in text
        
        if has_alerts:
            # Check for flood alerts
            if 'alertscategory":"FLOOD' in text or 'alertscategory": "FLOOD' in text:
                return {"hasAlerts": True, "type": "FLOOD", "source": "AccuWeather"}
            return {"hasAlerts": True, "type": "OTHER", "source": "AccuWeather"}
        
    except Exception as e:
        print(f"Error fetching {city_name}: {e}")
    
    return {"hasAlerts": False}


def main():
    print("Fetching AccuWeather alerts...")
    
    results = []
    
    for city_name, data in CITIES.items():
        print(f"Checking {city_name}...")
        alerts = fetch_alerts(city_name, data["code"])
        
        results.append({
            "name": city_name,
            "lat": data["lat"],
            "lng": data["lng"],
            "code": data["code"],
            "accuweatherAlert": alerts
        })
        
        if alerts["hasAlerts"]:
            print(f"  ⚠️ {city_name}: {alerts}")
    
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "cities": results
    }
    
    # Save to JSON
    with open("docs/alerts.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved to docs/alerts.json")
    print(f"Total cities: {len(results)}")
    print(f"Alerts found: {sum(1 for r in results if r['accuweatherAlert']['hasAlerts'])}")


if __name__ == "__main__":
    main()
