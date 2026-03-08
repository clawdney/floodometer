#!/usr/bin/env python3
"""
Floodometer Forecast Monitor
Checks weather forecast and prioritizes news scraping based on risk
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Open-Meteo API (free, no key needed)
FORECAST_API = "https://api.open-meteo.com/v1/forecast"

# Risk thresholds (mm of precipitation in next 24h)
THRESHOLDS = {
    'green': 10,   # < 10mm = safe
    'yellow': 30,  # 10-30mm = warning
    'orange': 50,  # 30-50mm = high
    'red': 100     # > 50mm = critical
}

# All cities from alerts.json
CITIES = [
    {"name": "Porto Alegre", "state": "RS", "lat": -30.0346, "lng": -51.2177},
    {"name": "Canoas", "state": "RS", "lat": -29.9177, "lng": -51.1836},
    {"name": "Lajeado", "state": "RS", "lat": -29.1167, "lng": -51.9667},
    {"name": "Rio de Janeiro", "state": "RJ", "lat": -22.9068, "lng": -43.1729},
    {"name": "Niterói", "state": "RJ", "lat": -22.8833, "lng": -43.1036},
    {"name": "São Paulo", "state": "SP", "lat": -23.5505, "lng": -46.6333},
    {"name": "Campinas", "state": "SP", "lat": -22.9099, "lng": -47.0626},
    {"name": "Belo Horizonte", "state": "MG", "lat": -19.9167, "lng": -43.9345},
    {"name": "Curitiba", "state": "PR", "lat": -25.4284, "lng": -49.2733},
    {"name": "Recife", "state": "PE", "lat": -8.0476, "lng": -34.8770},
    {"name": "Salvador", "state": "BA", "lat": -12.9714, "lng": -38.5014},
    {"name": "Fortaleza", "state": "CE", "lat": -3.7172, "lng": -38.5433},
    {"name": "Manaus", "state": "AM", "lat": -3.1190, "lng": -60.0217},
    {"name": "Brasília", "state": "DF", "lat": -15.8267, "lng": -47.9218},
    {"name": "Vitória", "state": "ES", "lat": -20.3155, "lng": -40.3128},
    {"name": "Goiânia", "state": "GO", "lat": -16.6799, "lng": -49.2550},
    {"name": "Natal", "state": "RN", "lat": -5.7945, "lng": -35.2110},
    {"name": "Belém", "state": "PA", "lat": -1.4558, "lng": -48.5039},
    {"name": "Florianópolis", "state": "SC", "lat": -27.5954, "lng": -48.5480},
    {"name": "Blumenau", "state": "SC", "lat": -26.9194, "lng": -49.0661},
    {"name": "Juiz de Fora", "state": "MG", "lat": -21.7617, "lng": -43.3217},
    {"name": "Ubá", "state": "MG", "lat": -21.1144, "lng": -42.9407},
    {"name": "Rio das Ostras", "state": "RJ", "lat": -22.7483, "lng": -41.9456},
    {"name": "Mariana", "state": "MG", "lat": -20.3775, "lng": -43.4168},
    {"name": "Carangola", "state": "MG", "lat": -20.7331, "lng": -42.4831},
    {"name": "Barra do Piraí", "state": "RJ", "lat": -22.4719, "lng": -43.8278},
    {"name": "Volta Redonda", "state": "RJ", "lat": -22.4932, "lng": -44.1017},
    {"name": "Petrópolis", "state": "RJ", "lat": -22.5050, "lng": -43.1789},
    {"name": "Teresópolis", "state": "RJ", "lat": -22.4123, "lng": -42.9632},
    {"name": "Nova Friburgo", "state": "RJ", "lat": -22.2818, "lng": -42.5346},
    {"name": "Silva Jardim", "state": "RJ", "lat": -22.6509, "lng": -42.7119},
    {"name": "Cachoeiro de Itapemirim", "state": "RJ", "lat": -20.8500, "lng": -41.1000},
]

def get_risk_level(precip_24h):
    """Determine risk level from precipitation forecast"""
    if precip_24h < THRESHOLDS['green']:
        return 'green'
    elif precip_24h < THRESHOLDS['yellow']:
        return 'yellow'
    elif precip_24h < THRESHOLDS['orange']:
        return 'orange'
    else:
        return 'red'

def fetch_forecast(lat, lng):
    """Fetch 7-day forecast from Open-Meteo"""
    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": ["precipitation_sum", "precipitation_probability_max", "weathercode"],
        "timezone": "America/Sao_Paulo",
        "forecast_days": 7
    }
    
    try:
        r = requests.get(FORECAST_API, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  ⚠️ API error: {e}")
    return None

def analyze_forecast(data):
    """Analyze forecast data for flood risk"""
    if not data or 'daily' not in data:
        return None
    
    daily = data['daily']
    precipitation = daily.get('precipitation_sum', [])
    
    # Calculate 24h precipitation (today)
    precip_24h = precipitation[0] if precipitation else 0
    
    # Calculate max in next 7 days
    max_precip = max(precipitation) if precipitation else 0
    
    # Total for week
    total_precip = sum(precipitation) if precipitation else 0
    
    # Risk assessment
    risk_today = get_risk_level(precip_24h)
    risk_week = get_risk_level(max_precip)
    
    # Determine overall risk (worst of today or week)
    risk_order = {'green': 0, 'yellow': 1, 'orange': 2, 'red': 3}
    overall_risk = max(risk_today, risk_week, key=lambda x: risk_order.get(x, 0))
    
    return {
        'precip_24h': precip_24h,
        'precip_max_7d': max_precip,
        'precip_total_7d': total_precip,
        'risk_today': risk_today,
        'risk_week': risk_week,
        'overall_risk': overall_risk,
        'dates': daily.get('time', [])[:7]
    }

def check_all_cities():
    """Check forecast for all cities"""
    results = []
    high_priority = []
    
    print("🌧️ Checking forecasts...")
    
    for city in CITIES:
        data = fetch_forecast(city['lat'], city['lng'])
        if data:
            analysis = analyze_forecast(data)
            if analysis:
                result = {
                    'name': city['name'],
                    'state': city['state'],
                    'lat': city['lat'],
                    'lng': city['lng'],
                    **analysis
                }
                results.append(result)
                
                # Flag high priority for news scraping
                if analysis['overall_risk'] in ['orange', 'red']:
                    high_priority.append(result)
                    
                print(f"  {city['name']} ({city['state']}): {analysis['precip_24h']:.1f}mm → {analysis['overall_risk']}")
        else:
            print(f"  {city['name']}: API failed")
    
    return results, high_priority

def get_scraper_schedule(high_priority):
    """Determine scraping schedule based on priority regions"""
    schedule = {
        'hourly': [],   # Critical - scrape every hour
        '6hourly': [],  # High - scrape every 6 hours
        'daily': [],    # Medium - scrape daily
        'weekly': []    # Low - scrape weekly
    }
    
    for city in high_priority:
        risk = city['overall_risk']
        if risk == 'red':
            schedule['hourly'].append(city)
        elif risk == 'orange':
            schedule['6hourly'].append(city)
        elif risk == 'yellow':
            schedule['daily'].append(city)
        else:
            schedule['weekly'].append(city)
    
    return schedule

def save_forecast_results(results, high_priority):
    """Save forecast results"""
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_cities': len(results),
        'high_priority_count': len(high_priority),
        'cities': results,
        'high_priority': high_priority
    }
    
    output_file = Path(__file__).parent / "docs" / "forecast.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Saved to {output_file}")
    return output_file

def run():
    print("=" * 50)
    print("🌧️ Floodometer Forecast Monitor")
    print("=" * 50)
    
    results, high_priority = check_all_cities()
    
    if high_priority:
        print(f"\n🚨 {len(high_priority)} HIGH PRIORITY regions:")
        for city in high_priority:
            print(f"   {city['name']} ({city['state']}): {city['precip_24h']:.1f}mm/24h")
    
    # Get schedule
    schedule = get_scraper_schedule(high_priority)
    print(f"\n📅 Scraping Schedule:")
    print(f"   Hourly: {len(schedule['hourly'])} cities")
    print(f"   Every 6h: {len(schedule['6hourly'])} cities")
    print(f"   Daily: {len(schedule['daily'])} cities")
    print(f"   Weekly: {len(schedule['weekly'])} cities")
    
    # Save results
    save_forecast_results(results, high_priority)
    
    return high_priority

if __name__ == "__main__":
    run()
