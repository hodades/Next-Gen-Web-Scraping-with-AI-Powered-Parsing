import requests
import json
import pandas as pd
import time
import os
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

class CookieManager:
    def __init__(self):
        self.context = None
        self.page = None
        self.playwright = None
        self.chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        self.user_data_dir = r"C:\\Users\\AmirB\\AppData\\Local\\Temp\\Chrome_Playwright_Profile"

    def start(self):
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        if self.context:
            self.context.close()

        print("🟢 Lancement navigateur Playwright...")
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            executable_path=self.chrome_path,
            headless=False,
            args=["--profile-directory=Default"]
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        
        # Try different wait strategies with fallbacks
        try:
            print("🌐 Tentative de navigation vers everywatch.com...")
            self.page.goto("https://everywatch.com", wait_until="domcontentloaded", timeout=60000)
            print("✅ Navigation réussie (domcontentloaded)")
        except Exception as e:
            print(f"⚠️ Échec domcontentloaded, tentative sans wait: {e}")
            try:
                self.page.goto("https://everywatch.com", timeout=60000)
                print("✅ Navigation réussie (sans wait)")
            except Exception as e2:
                print(f"❌ Échec de navigation: {e2}")
                print("🔄 Continuons quand même...")
        
        time.sleep(2)

    def get_cookie_header(self):
        cookies = self.context.cookies("https://everywatch.com")
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    def stop(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

class WatchScraper:
    def __init__(self):
        self.build_id = "fPbAMl-fY2ZzUCpo_X038"
        self.output_file = 'all_watches_data.json'
        self.cookie_manager = CookieManager()
        self.cookie_header = ""

    def refresh_cookies(self):
        self.cookie_manager.start()
        self.cookie_header = self.cookie_manager.get_cookie_header()

    def get_headers(self, ref_url=None):
        referer = 'https://everywatch.com/breguet?pageSize=120&pageNumber=1'
        if ref_url and ref_url.startswith('https://everywatch.com/') and 'watch-' in ref_url:
            parts = ref_url.split('/')
            if len(parts) >= 5:
                referer = f"https://everywatch.com/{parts[3]}"
                if len(parts) >= 6:
                    referer += f"/{parts[4]}"

        headers = {
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': referer,
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-nextjs-data': '1',
            'Cookie': self.cookie_header
        }

        print(f"🔄 Referer calculé: {referer}")
        return headers

    def parse_watch_url(self, url):
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) == 2:
            return parts[0], "watch", parts[1].replace("watch-", "")
        elif len(parts) == 3:
            return parts[0], parts[1], parts[2].replace("watch-", "")
        elif len(parts) == 4:
            return parts[0], parts[1], parts[3].replace("watch-", "")
        else:
            print(f"⚠️ Format URL non supporté : {url}")
            return None, None, None

    def build_api_url(self, url):
        brand, model, ref = self.parse_watch_url(url)
        if not all([brand, model, ref]):
            return None
        if model == "watch":
            return f"https://everywatch.com/_next/data/{self.build_id}/{brand}/watch-{ref}.json?brand={brand}&refSlug=watch-{ref}"
        else:
            return f"https://everywatch.com/_next/data/{self.build_id}/{brand}/{model}/watch-{ref}.json?brand={brand}&modelSlug={model}&refSlug=watch-{ref}"

    def scrape_watch(self, url):
        try:
            api_url = self.build_api_url(url)
            if not api_url:
                return {'url': url, 'error': 'API URL invalid'}
            headers = self.get_headers(url)
            print(f"🌐 URL page: {url}")
            print(f"🔗 URL API: {api_url}")

            response = requests.get(api_url, headers=headers)
            if response.status_code == 403:
                print("🚫 BLOQUÉ ! Status 403")
                return {'blocked': True}
            json_data = response.json()
            pageProps = json_data.get('pageProps', {})
            if 'error' in pageProps and isinstance(pageProps['error'], dict):
                print(f"🚫 BLOQUÉ ! Code: {pageProps['error'].get('blockCode')}")
                return {'blocked': True, 'block_info': pageProps['error']}

            return {
                'url': url,
                'api_url': api_url,
                'data': {
                    'masterId': pageProps.get('masterId'),
                    'metadata': pageProps.get('metadata', {}),
                    'watchDetail': pageProps.get('watchDetail', {})
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'url': url, 'error': str(e)}

    def load_existing_results(self):
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def get_processed_urls(self, results):
        return {result['url'] for result in results if 'url' in result}

    def save_results(self, results):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Résultats sauvegardés dans {self.output_file}")

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            print(f"⏳ Attente: {i}s...", end='\r')
            time.sleep(1)
        print(" " * 20, end='\r')

    def scrape_all_from_csv(self, csv_file="Watchfeed.csv", delay_seconds=3, batch_size=400):
        print("🚀 Démarrage du scraping (cookies dynamiques)...")
        if not os.path.exists(csv_file):
            print("❌ Fichier introuvable.")
            return

        df = pd.read_csv(csv_file)
        results = self.load_existing_results()
        done_urls = self.get_processed_urls(results)
        all_urls = [url for url in df['Links'] if url not in done_urls]
        total = len(all_urls)

        print(f"📊 URLs déjà traitées: {len(done_urls)}")
        print(f"📊 URLs restantes: {total}")

        for i, url in enumerate(all_urls, 1):
            if (i - 1) % batch_size == 0:
                print("🔁 Rafraîchissement des cookies...")
                self.refresh_cookies()

            print(f"\n📍 Scraping {i}/{total}: {url}")
            result = self.scrape_watch(url)

            if result and result.get('blocked'):
                print("🚫 Bloqué ! Attente de 2 minutes...")
                time.sleep(120)
                continue

            if result:
                results.append(result)
                self.save_results(results)
                if 'error' not in result:
                    print(f"✅ Succès pour {url}")
                else:
                    print(f"⚠️ Erreur: {result.get('error')}")

            if i < total:
                self.countdown(delay_seconds)

        self.cookie_manager.stop()
        print(f"\n🎉 Scraping terminé ! {len(results)} résultats dans {self.output_file}")
        return results

if __name__ == "__main__":
    scraper = WatchScraper()
    scraper.scrape_all_from_csv("Watchfeed.csv", delay_seconds=3)
