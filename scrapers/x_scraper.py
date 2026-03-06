"""
Scraper para perfil de X (Twitter) sin usar API
Utiliza Playwright para extraer tweets de un usuario
"""

import json
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pathlib import Path


class XScraper:
    def __init__(self, username, headless=True):
        """
        Inicializa el scraper de X

        Args:
            username: Usuario de X a scrapear (sin @)
            headless: Si se ejecuta el navegador en modo headless
        """
        self.username = username
        self.headless = headless
        self.base_url = f"https://x.com/{username}"
        self.tweets = []

    def scroll_page(self, page, scrolls=10, delay=2):
        """
        Hace scroll en la página para cargar más tweets

        Args:
            page: Página de Playwright
            scrolls: Número de veces que hacer scroll
            delay: Delay entre scrolls en segundos
        """
        for i in range(scrolls):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(delay)
            print(f"Scroll {i+1}/{scrolls} completado")

    def extract_tweets(self, page):
        """
        Extrae tweets de la página actual

        Args:
            page: Página de Playwright

        Returns:
            Lista de tweets extraídos
        """
        tweets_data = []

        # Esperar a que los tweets carguen
        try:
            page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
        except PlaywrightTimeout:
            print("No se encontraron tweets o timeout")
            return tweets_data

        # Obtener todos los artículos de tweets
        tweet_elements = page.query_selector_all('article[data-testid="tweet"]')
        print(f"Encontrados {len(tweet_elements)} tweets en la página")

        for tweet_el in tweet_elements:
            try:
                # Extraer texto del tweet
                text_element = tweet_el.query_selector('[data-testid="tweetText"]')
                text = text_element.inner_text() if text_element else ""

                # Extraer timestamp
                time_element = tweet_el.query_selector('time')
                timestamp = time_element.get_attribute('datetime') if time_element else None

                # Extraer métricas (likes, retweets, etc.)
                reply_count = self._get_metric(tweet_el, 'reply')
                retweet_count = self._get_metric(tweet_el, 'retweet')
                like_count = self._get_metric(tweet_el, 'like')

                # Verificar si es un retweet
                is_retweet = tweet_el.query_selector('span:has-text("Retweeted")') is not None

                tweet_data = {
                    'text': text,
                    'timestamp': timestamp,
                    'reply_count': reply_count,
                    'retweet_count': retweet_count,
                    'like_count': like_count,
                    'is_retweet': is_retweet,
                    'extracted_at': datetime.now().isoformat()
                }

                # Solo agregar si tiene texto y no es duplicado
                if text and not any(t['text'] == text for t in tweets_data):
                    tweets_data.append(tweet_data)

            except Exception as e:
                print(f"Error extrayendo tweet: {e}")
                continue

        return tweets_data

    def _get_metric(self, tweet_element, metric_type):
        """
        Extrae una métrica específica del tweet (likes, retweets, etc.)

        Args:
            tweet_element: Elemento del tweet
            metric_type: Tipo de métrica ('reply', 'retweet', 'like')

        Returns:
            Valor de la métrica o 0
        """
        try:
            metric_element = tweet_element.query_selector(f'[data-testid="{metric_type}"]')
            if metric_element:
                metric_text = metric_element.inner_text()
                # Limpiar y convertir a número
                metric_text = metric_text.strip().replace(',', '').replace('K', '000').replace('M', '000000')
                return int(metric_text) if metric_text.isdigit() else 0
        except:
            pass
        return 0

    def scrape(self, max_tweets=100, scroll_count=10):
        """
        Ejecuta el scraping del perfil

        Args:
            max_tweets: Número máximo de tweets a extraer
            scroll_count: Número de scrolls a realizar

        Returns:
            Lista de tweets extraídos
        """
        print(f"Iniciando scraping de @{self.username}")

        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            try:
                # Navegar al perfil
                print(f"Navegando a {self.base_url}")
                page.goto(self.base_url, wait_until='networkidle', timeout=30000)

                # Esperar un poco para que cargue
                time.sleep(3)

                # Hacer scroll y extraer tweets
                self.scroll_page(page, scrolls=scroll_count)

                # Extraer todos los tweets
                self.tweets = self.extract_tweets(page)

                print(f"\nTotal de tweets únicos extraídos: {len(self.tweets)}")

                # Limitar al máximo solicitado
                if len(self.tweets) > max_tweets:
                    self.tweets = self.tweets[:max_tweets]
                    print(f"Limitado a {max_tweets} tweets")

            except Exception as e:
                print(f"Error durante el scraping: {e}")
            finally:
                browser.close()

        return self.tweets

    def save_to_json(self, output_path=None):
        """
        Guarda los tweets en formato JSON

        Args:
            output_path: Ruta donde guardar el archivo (opcional)
        """
        if output_path is None:
            # Crear nombre de archivo con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data/x_tweets/{self.username}_{timestamp}.json"

        # Crear directorio si no existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Guardar datos
        data = {
            'username': self.username,
            'scraped_at': datetime.now().isoformat(),
            'tweet_count': len(self.tweets),
            'tweets': self.tweets
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\nDatos guardados en: {output_path}")
        return output_path


def main():
    """Función principal para ejecutar el scraper"""
    # Configuración
    USERNAME = "zuler"  # Sin @
    MAX_TWEETS = 200
    SCROLL_COUNT = 20
    HEADLESS = True  # Cambiar a False para ver el navegador

    # Crear scraper
    scraper = XScraper(username=USERNAME, headless=HEADLESS)

    # Ejecutar scraping
    tweets = scraper.scrape(max_tweets=MAX_TWEETS, scroll_count=SCROLL_COUNT)

    # Guardar resultados
    if tweets:
        scraper.save_to_json()

        # Mostrar algunos ejemplos
        print("\n" + "="*50)
        print("EJEMPLOS DE TWEETS EXTRAÍDOS:")
        print("="*50)
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"\n--- Tweet {i} ---")
            print(f"Texto: {tweet['text'][:100]}...")
            print(f"Likes: {tweet['like_count']}")
            print(f"Retweets: {tweet['retweet_count']}")
            print(f"Fecha: {tweet['timestamp']}")
    else:
        print("\nNo se extrajeron tweets")


if __name__ == "__main__":
    main()
