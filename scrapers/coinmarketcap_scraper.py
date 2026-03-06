"""
Scraper para noticias de CoinMarketCap
Extrae artículos, títulos, contenido e imágenes
"""

import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class CoinMarketCapScraper:
    def __init__(self, headless=True, coins=None):
        """
        Inicializa el scraper de CoinMarketCap

        Args:
            headless: Si se ejecuta en modo headless
            coins: Lista de monedas a scrapear (e.g., ['bitcoin', 'ethereum'])
        """
        self.base_url = "https://coinmarketcap.com"
        self.news_url = f"{self.base_url}/headlines/news/"
        self.articles = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        # Monedas principales por defecto
        self.coins = coins or [
            'bitcoin',
            'ethereum',
            'tether',
            'bnb',
            'solana',
            'xrp',
            'cardano',
            'dogecoin'
        ]

    def scrape_coin_news(self, coin_slug, max_news=5):
        """
        Scrape noticias de la página de una moneda específica

        Args:
            coin_slug: Slug de la moneda (e.g., 'bitcoin', 'ethereum')
            max_news: Número máximo de noticias a extraer por moneda

        Returns:
            Lista de datos de noticias
        """
        coin_url = f"{self.base_url}/currencies/{coin_slug}/"
        print(f"\nScraping noticias de {coin_slug}...")

        try:
            response = requests.get(coin_url, headers=self.headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Error al obtener página de {coin_slug}: {e}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = []

        # Buscar sección de noticias
        # CoinMarketCap puede tener la sección de noticias con diferentes selectores
        news_selectors = [
            'div[class*="news"]',
            'section[class*="news"]',
            'div[id*="news"]',
            'a[href*="/headlines/news/"]',
            'a[href*="/alexandria/article/"]'
        ]

        all_news_links = set()
        for selector in news_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Buscar enlaces dentro del elemento
                links = element.find_all('a', href=True) if hasattr(element, 'find_all') else [element]
                for link in links:
                    href = link.get('href', '')
                    if '/headlines/news/' in href or '/alexandria/article/' in href:
                        full_url = urljoin(self.base_url, href)
                        all_news_links.add(full_url)

        # También buscar directamente todos los enlaces de noticias
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if '/headlines/news/' in href or '/alexandria/article/' in href:
                full_url = urljoin(self.base_url, href)
                # Verificar si el enlace menciona la moneda
                link_text = link.get_text(strip=True).lower()
                if coin_slug.lower() in link_text or coin_slug.lower() in href.lower():
                    all_news_links.add(full_url)

        print(f"  Encontrados {len(all_news_links)} enlaces de noticias")

        # Extraer información básica de cada noticia
        for i, news_url in enumerate(list(all_news_links)[:max_news]):
            try:
                # Obtener título desde el enlace si es posible
                news_link = soup.find('a', href=lambda h: h and news_url in h)
                title = news_link.get_text(strip=True) if news_link else None

                news_data = {
                    'url': news_url,
                    'coin': coin_slug,
                    'title_preview': title,
                    'found_at': coin_url
                }
                news_items.append(news_data)

            except Exception as e:
                print(f"  Error procesando noticia {i+1}: {e}")
                continue

        return news_items

    def scrape_news_list(self, max_articles=20):
        """
        Scrape la lista de noticias de todas las monedas configuradas

        Args:
            max_articles: Número máximo de artículos a extraer en total

        Returns:
            Lista de URLs de artículos únicos
        """
        print(f"Scraping noticias de {len(self.coins)} monedas...")

        all_news = []
        max_per_coin = max(3, max_articles // len(self.coins))

        for coin in self.coins:
            coin_news = self.scrape_coin_news(coin, max_news=max_per_coin)
            all_news.extend(coin_news)
            time.sleep(1)  # Delay entre monedas

        # Extraer URLs únicas
        unique_urls = []
        seen_urls = set()

        for news in all_news:
            url = news['url']
            if url not in seen_urls:
                unique_urls.append(url)
                seen_urls.add(url)

        print(f"\nTotal de artículos únicos encontrados: {len(unique_urls)}")
        return unique_urls[:max_articles]

    def scrape_article(self, url):
        """
        Scrape un artículo individual

        Args:
            url: URL del artículo

        Returns:
            Diccionario con datos del artículo
        """
        print(f"Scraping artículo: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error al obtener artículo: {e}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraer título
        title = None
        title_selectors = ['h1', 'h1.title', '.article-title', 'title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break

        # Extraer contenido
        content = ""
        content_selectors = [
            'article', '.article-content', '.content', '.post-content',
            'div[class*="article"]', 'div[class*="content"]'
        ]
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Obtener todos los párrafos
                paragraphs = content_elem.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                if content:
                    break

        # Si no se encontró contenido, intentar con todos los párrafos de la página
        if not content:
            paragraphs = soup.find_all('p')
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:10] if p.get_text(strip=True)])

        # Extraer fecha
        date = None
        time_elem = soup.find('time')
        if time_elem:
            date = time_elem.get('datetime') or time_elem.get_text(strip=True)

        # Extraer imágenes
        images = []
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src:
                # Evitar logos y pequeñas imágenes
                width = img.get('width')
                if width and int(width) < 200:
                    continue

                full_url = urljoin(url, src)
                images.append({
                    'url': full_url,
                    'alt': img.get('alt', ''),
                })

        # Extraer autor
        author = None
        author_selectors = ['.author', '.by-author', 'span[class*="author"]', 'a[rel="author"]']
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                break

        article_data = {
            'url': url,
            'title': title or 'Sin título',
            'content': content or 'Sin contenido',
            'date': date,
            'author': author,
            'images': images[:5],  # Limitar a 5 imágenes
            'scraped_at': datetime.now().isoformat(),
            'word_count': len(content.split()) if content else 0
        }

        return article_data

    def download_image(self, image_url, save_dir='images/original'):
        """
        Descarga una imagen

        Args:
            image_url: URL de la imagen
            save_dir: Directorio donde guardar

        Returns:
            Path del archivo guardado o None
        """
        try:
            response = requests.get(image_url, headers=self.headers, timeout=10, stream=True)
            response.raise_for_status()

            # Crear directorio si no existe
            Path(save_dir).mkdir(parents=True, exist_ok=True)

            # Obtener nombre de archivo
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename:
                filename = f"image_{int(time.time())}.jpg"

            filepath = os.path.join(save_dir, filename)

            # Guardar imagen
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Imagen descargada: {filepath}")
            return filepath

        except Exception as e:
            print(f"Error descargando imagen {image_url}: {e}")
            return None

    def scrape(self, max_articles=20, download_images=True, scrape_from_coins=True):
        """
        Ejecuta el scraping completo

        Args:
            max_articles: Número máximo de artículos
            download_images: Si se descargan las imágenes
            scrape_from_coins: Si True, scrape desde páginas de monedas individuales

        Returns:
            Lista de artículos scrapeados
        """
        print(f"Iniciando scraping de CoinMarketCap...")
        print(f"Monedas objetivo: {', '.join(self.coins)}")

        if scrape_from_coins:
            # Nuevo método: scrapear desde páginas de monedas
            all_news = []
            max_per_coin = max(2, max_articles // len(self.coins))

            for coin in self.coins:
                coin_news = self.scrape_coin_news(coin, max_news=max_per_coin)
                for news in coin_news:
                    article_data = self.scrape_article(news['url'])
                    if article_data:
                        article_data['coin'] = coin
                        article_data['source_page'] = news['found_at']

                        # Descargar imágenes si se solicita
                        if download_images and article_data.get('images'):
                            downloaded_images = []
                            for img in article_data['images'][:3]:
                                img_path = self.download_image(img['url'])
                                if img_path:
                                    downloaded_images.append({
                                        'original_url': img['url'],
                                        'local_path': img_path,
                                        'alt': img['alt']
                                    })
                            article_data['downloaded_images'] = downloaded_images

                        self.articles.append(article_data)

                        if len(self.articles) >= max_articles:
                            break

                # Delay entre monedas
                time.sleep(2)

                if len(self.articles) >= max_articles:
                    break

        else:
            # Método original: scrapear desde página general de noticias
            article_urls = self.scrape_news_list(max_articles)

            if not article_urls:
                print("No se encontraron artículos")
                return []

            for i, url in enumerate(article_urls, 1):
                print(f"\nProcesando artículo {i}/{len(article_urls)}")

                article_data = self.scrape_article(url)

                if article_data:
                    if download_images and article_data.get('images'):
                        downloaded_images = []
                        for img in article_data['images'][:3]:
                            img_path = self.download_image(img['url'])
                            if img_path:
                                downloaded_images.append({
                                    'original_url': img['url'],
                                    'local_path': img_path,
                                    'alt': img['alt']
                                })
                        article_data['downloaded_images'] = downloaded_images

                    self.articles.append(article_data)

                time.sleep(2)

        print(f"\n✓ Scraping completado: {len(self.articles)} artículos extraídos")
        return self.articles

    def save_to_json(self, output_path=None):
        """
        Guarda los artículos en formato JSON

        Args:
            output_path: Ruta donde guardar (opcional)
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data/coinmarketcap/articles_{timestamp}.json"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        data = {
            'scraped_at': datetime.now().isoformat(),
            'article_count': len(self.articles),
            'articles': self.articles
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\nDatos guardados en: {output_path}")
        return output_path


def main():
    """Función principal"""
    # Configuración
    MAX_ARTICLES = 15
    DOWNLOAD_IMAGES = True

    # Monedas principales a scrapear
    COINS = [
        'bitcoin',
        'ethereum',
        'tether',
        'bnb',
        'solana',
        'xrp'
    ]

    # Crear scraper con monedas específicas
    scraper = CoinMarketCapScraper(coins=COINS)

    # Ejecutar scraping desde páginas de monedas
    articles = scraper.scrape(
        max_articles=MAX_ARTICLES,
        download_images=DOWNLOAD_IMAGES,
        scrape_from_coins=True
    )

    # Guardar resultados
    if articles:
        scraper.save_to_json()

        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN DE ARTÍCULOS:")
        print("="*60)

        # Agrupar por moneda
        by_coin = {}
        for article in articles:
            coin = article.get('coin', 'unknown')
            if coin not in by_coin:
                by_coin[coin] = []
            by_coin[coin].append(article)

        for coin, coin_articles in by_coin.items():
            print(f"\n{coin.upper()}: {len(coin_articles)} artículos")
            for i, article in enumerate(coin_articles[:2], 1):
                print(f"  {i}. {article['title'][:60]}...")
                print(f"     Palabras: {article['word_count']}, Imágenes: {len(article.get('images', []))}")
    else:
        print("\nNo se extrajeron artículos")


if __name__ == "__main__":
    main()
