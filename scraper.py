#!/usr/bin/env python3
"""
Floodometer News Scraper
Fetches flood-related news from multiple sources
"""

import requests
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup
import time

# Configuration
SOURCES_FILE = Path(__file__).parent / "sources.json"
OUTPUT_FILE = Path(__file__).parent / "incidents.json"
STATE_CODES = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SE', 'SP', 'TO']

# Keywords for flood detection
KEYWORDS = {
    'flood': ['enchente', 'alagamento', 'inundação', 'cheia', 'transbordamento', 'aluvião'],
    'weather': ['chuva', 'temporal', 'granizo', 'tempestade', 'ventania', 'chuva forte'],
    'disaster': ['desastre', 'tragédia', 'emergência', 'alerta', 'deslizamento', 'desmoronamento']
}

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.incidents = []
        
    def load_sources(self):
        with open(SOURCES_FILE) as f:
            return json.load(f)
    
    def is_flood_related(self, text):
        """Check if text is flood-related"""
        text = text.lower()
        for category, words in KEYWORDS.items():
            for word in words:
                if word in text:
                    return True, category
        return False, None
    
    def extract_city(self, text):
        """Try to extract city/location from text"""
        # Look for city patterns like "em Belo Horizonte", "na capital"
        patterns = [
            r'em\s+([A-Z][a-zà-ÿ\s]+?)(?:\s|,|\.|!|\?)',
            r'na\s+([A-Z][a-zà-ÿ\s]+?)(?:\s|,|\.|!|\?)',
            r'em\s+([A-Z][a-z]+)\s+-\s+([A-Z]{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match.group(1).:
                return matchstrip()
        
        # Check for state abbreviations
        for state in STATE_CODES:
            if state in text:
                return state
        
        return None
    
    def fetch_rss(self, source):
        """Fetch from RSS feed"""
        articles = []
        rss_url = source.get('rss')
        
        if not rss_url:
            return articles
        
        try:
            resp = self.session.get(rss_url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'xml')
                for item in soup.find_all('item')[:20]:
                    title = item.find('title')
                    desc = item.find('description')
                    link = item.find('link')
                    
                    if title:
                        title_text = title.get_text()
                        desc_text = desc.get_text() if desc else ""
                        
                        is_related, category = self.is_flood_related(title_text + " " + desc_text)
                        
                        if is_related:
                            articles.append({
                                'title': title_text.strip(),
                                'description': desc_text.strip()[:300],
                                'link': link.get_text() if link else "",
                                'source': source['name'],
                                'category': category,
                                'published': item.find('pubDate').get_text() if item.find('pubDate') else "",
                                'fetched_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"  ⚠️ RSS error: {e}")
        
        return articles
    
    def fetch_html(self, source):
        """Fetch from HTML page (simplified)"""
        articles = []
        
        try:
            resp = self.session.get(source['url'], timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Find article links (simplified - would need source-specific selectors)
                keywords = KEYWORDS['flood'] + KEYWORDS['disaster']
                
                for link in soup.find_all('a', href=True)[:30]:
                    href = link.get('href', '')
                    text = link.get_text().lower()
                    
                    for kw in keywords:
                        if kw in text or kw in href:
                            articles.append({
                                'title': link.get_text().strip()[:100],
                                'link': href if href.startswith('http') else source['url'] + href,
                                'source': source['name'],
                                'category': 'flood',
                                'fetched_at': datetime.now().isoformat()
                            })
                            break
        except Exception as e:
            print(f"  ⚠️ HTML error: {e}")
        
        return articles
    
    def search_google_news(self, state_code, city_name=None):
        """Search Google News for flood in specific location"""
        # Note: This would need Google News API or scraping
        # For now, return empty
        return []
    
    def scrape_source(self, source):
        """Scrape a single source"""
        print(f"  📰 {source['name']}...")
        
        articles = []
        
        # Try RSS first
        if source.get('rss'):
            articles.extend(self.fetch_rss(source))
        
        # Fallback to HTML
        if not articles:
            articles.extend(self.fetch_html(source))
        
        return articles
    
    def scrape_all(self):
        """Scrape all configured sources"""
        data = self.load_sources()
        
        # National sources
        print("\n🌍 National sources...")
        for source in data.get('newsSources', {}).get('national', []):
            self.incidents.extend(self.scrape_source(source))
            time.sleep(1)  # Rate limiting
        
        # Regional sources by state
        print("\n📍 Regional sources...")
        regional = data.get('newsSources', {}).get('regional', {})
        
        for state_code, sources in regional.items():
            print(f"\n  State: {state_code}")
            for source in sources:
                self.incidents.extend(self.scrape_source(source))
                time.sleep(1)
        
        # Save results
        self.save_results()
        
        return self.incidents
    
    def save_results(self):
        """Save scraped incidents"""
        output = {
            'last_updated': datetime.now().isoformat(),
            'total_incidents': len(self.incidents),
            'incidents': self.incidents[:100]  # Keep last 100
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Saved {len(self.incidents)} incidents to {OUTPUT_FILE}")

class IncidentAggregator:
    """Aggregate and deduplicate incidents"""
    
    def __init__(self):
        self.incidents_file = OUTPUT_FILE
    
    def load(self):
        if self.incidents_file.exists():
            with open(self.incidents_file) as f:
                return json.load(f)
        return {'incidents': []}
    
    def deduplicate(self):
        """Remove duplicates based on title similarity"""
        data = self.load()
        seen = set()
        unique = []
        
        for inc in data.get('incidents', []):
            # Simple dedupe - check title
            title_key = inc.get('title', '').lower()[:50]
            if title_key not in seen:
                seen.add(title_key)
                unique.append(inc)
        
        data['incidents'] = unique
        data['total_incidents'] = len(unique)
        
        with open(self.incidents_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Deduplicated: {len(unique)} unique incidents")
        return unique

def run():
    print("=" * 50)
    print("🌊 Floodometer News Scraper")
    print("=" * 50)
    
    scraper = NewsScraper()
    scraper.scrape_all()
    
    # Deduplicate
    agg = IncidentAggregator()
    agg.deduplicate()
    
    print("\n✅ Done!")

if __name__ == "__main__":
    run()
