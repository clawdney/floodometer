#!/usr/bin/env python3
"""
News-based flood city discovery + AccuWeather alert fetcher.
Automatically finds cities with recent flood incidents.
"""

import requests
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

# Known city codes for AccuWeather
CITY_CODES = {
    'porto alegre': {'lat': -30.0346, 'lng': -51.2177, 'code': '4564'},
    'canoas': {'lat': -29.9177, 'lng': -51.1836, 'code': '4571'},
    'lajeado': {'lat': -29.1167, 'lng': -51.9667, 'code': '126769'},
    'rio de janeiro': {'lat': -22.9068, 'lng': -43.1729, 'code': '4544'},
    'niterói': {'lat': -22.8833, 'lng': -43.1036, 'code': '10733'},
    'niteroi': {'lat': -22.8833, 'lng': -43.1036, 'code': '10733'},
    'são paulo': {'lat': -23.5505, 'lng': -46.6333, 'code': '45881'},
    'sao paulo': {'lat': -23.5505, 'lng': -46.6333, 'code': '45881'},
    'campinas': {'lat': -22.9099, 'lng': -47.0626, 'code': '45883'},
    'belo horizonte': {'lat': -19.9167, 'lng': -43.9345, 'code': '4607'},
    'curitiba': {'lat': -25.4284, 'lng': -49.2733, 'code': '4611'},
    'recife': {'lat': -8.0476, 'lng': -34.877, 'code': '4245'},
    'salvador': {'lat': -12.9714, 'lng': -38.5014, 'code': '4242'},
    'fortaleza': {'lat': -3.7172, 'lng': -38.5433, 'code': '4243'},
    'manaus': {'lat': -3.119, 'lng': -60.0217, 'code': '3944'},
    'brasília': {'lat': -15.8267, 'lng': -47.9218, 'code': '15482'},
    'brasilia': {'lat': -15.8267, 'lng': -47.9218, 'code': '15482'},
    'vitória': {'lat': -20.3155, 'lng': -40.3128, 'code': '4605'},
    'vitoria': {'lat': -20.3155, 'lng': -40.3128, 'code': '4605'},
    'goiânia': {'lat': -16.6799, 'lng': -49.255, 'code': '8108'},
    'goiania': {'lat': -16.6799, 'lng': -49.255, 'code': '8108'},
    'natal': {'lat': -5.7945, 'lng': -35.211, 'code': '4256'},
    'belém': {'lat': -1.4558, 'lng': -48.5039, 'code': '4238'},
    'belem': {'lat': -1.4558, 'lng': -48.5039, 'code': '4238'},
    'florianópolis': {'lat': -27.5954, 'lng': -48.548, 'code': '4622'},
    'florianopolis': {'lat': -27.5954, 'lng': -48.548, 'code': '4622'},
    'blumenau': {'lat': -26.9194, 'lng': -49.0661, 'code': '10236'},
    'juiz de fora': {'lat': -21.7617, 'lng': -43.3217, 'code': '45887'},
    'ubá': {'lat': -21.1144, 'lng': -42.9407, 'code': '45624'},
    'uba': {'lat': -21.1144, 'lng': -42.9407, 'code': '45624'},
    'rio das ostras': {'lat': -22.7483, 'lng': -41.9456, 'code': '104348'},
    'mariana': {'lat': -20.3775, 'lng': -43.4168, 'code': '10268'},
    'carangola': {'lat': -20.7331, 'lng': -42.4831, 'code': '22869'},
    'barra do piraí': {'lat': -22.4719, 'lng': -43.8278, 'code': '10667'},
    'volta redonda': {'lat': -22.4932, 'lng': -44.1017, 'code': '45878'},
    'petrópolis': {'lat': -22.505, 'lng': -43.1789, 'code': '45876'},
    'petropolis': {'lat': -22.505, 'lng': -43.1789, 'code': '45876'},
    'teresópolis': {'lat': -22.4123, 'lng': -42.9632, 'code': '45879'},
    'teresopolis': {'lat': -22.4123, 'lng': -42.9632, 'code': '45879'},
    'nova friburgo': {'lat': -22.2818, 'lng': -42.5346, 'code': '45875'},
    'silva jardim': {'lat': -22.6509, 'lng': -42.7119, 'code': '45880'},
}


def search_flood_news():
    """Search Brazilian news for recent flood incidents."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Search queries for recent floods
    queries = [
        'enchente Brasil março 2026',
        'alagamento Brasil fevereiro 2026',
        'chuva forte Brasil janeiro 2026',
        'deslizamento Brasil 2026',
        'inundação Brasil 2026'
    ]
    
    cities_found = defaultdict(list)
    
    # Try G1 (Globo) news search
    try:
        url = "https://g1.globo.com/busca/"
        for query in queries:
            try:
                resp = requests.get(url, params={'q': query}, headers=headers, timeout=10)
                text = resp.text.lower()
                
                # Find city names in results
                for city_lower, data in CITY_CODES.items():
                    if city_lower in text:
                        cities_found[city_lower].append({
                            'source': 'G1',
                            'query': query,
                            'type': 'news'
                        })
            except Exception as e:
                print(f"Error searching G1 for '{query}': {e}")
    except Exception as e:
        print(f"G1 search error: {e}")
    
    return cities_found


def fetch_accuweather_alerts():
    """Fetch alerts for all known cities."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    results = []
    
    # Deduplicate by normalized name
    seen = set()
    
    for city_lower, data in CITY_CODES.items():
        if city_lower in seen:
            continue
        seen.add(city_lower)
        
        city_name = city_lower.title()
        if ' De ' in city_name:
            city_name = city_name.replace(' De ', ' de ')
        if ' Das ' in city_name:
            city_name = city_name.replace(' Das ', ' das ')
        if ' Do ' in city_name:
            city_name = city_name.replace(' Do ', ' do ')
            
        try:
            url = f"https://www.accuweather.com/en/br/{city_lower.replace(' ', '-')}/{data['code']}/weather-forecast/{data['code']}"
            r = requests.get(url, headers=headers, timeout=10)
            text = r.text
            
            has_alerts = '"hasAlerts":true' in text
            is_flood = 'alertscategory":"FLOOD' in text
            
            result = {
                'name': city_name,
                'lat': data['lat'],
                'lng': data['lng'],
                'code': data['code'],
                'accuweatherAlert': None
            }
            
            if has_alerts:
                alert_type = 'FLOOD' if is_flood else 'OTHER'
                result['accuweatherAlert'] = {
                    'hasAlerts': True,
                    'type': alert_type,
                    'source': 'AccuWeather'
                }
                print(f"⚠️ {city_name}: {alert_type}")
            
            results.append(result)
            
        except Exception as e:
            print(f"Error fetching {city_name}: {e}")
            results.append({
                'name': city_name,
                'lat': data['lat'],
                'lng': data['lng'],
                'code': data['code'],
                'accuweatherAlert': None
            })
    
    return results


def main():
    print("=" * 50)
    print("FLOODOMETER - Auto City Discovery")
    print("=" * 50)
    
    print("\n[1/2] Searching news for flood cities...")
    news_cities = search_flood_news()
    if news_cities:
        print(f"Found {len(news_cities)} cities in news:")
        for city in news_cities:
            print(f"  - {city}")
    else:
        print("No new cities from news (will use known cities)")
    
    print("\n[2/2] Fetching AccuWeather alerts...")
    cities_data = fetch_accuweather_alerts()
    
    # Add discovered cities from news that aren't in our list
    for city_lower in news_cities:
        if city_lower not in CITY_CODES:
            print(f"New city from news: {city_lower} - need coordinates!")
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'news_cities': list(news_cities.keys()),
        'cities': cities_data
    }
    
    with open('docs/alerts.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n" + "=" * 50)
    print(f"Saved {len(cities_data)} cities to docs/alerts.json")
    print(f"Alerts: {sum(1 for c in cities_data if c['accuweatherAlert'])}")
    print(f"Flood: {sum(1 for c in cities_data if c['accuweatherAlert'] and c['accuweatherAlert']['type'] == 'FLOOD')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
