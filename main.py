"""
Script principal del Crypto News Replicator
Orquesta todo el proceso: scraping, análisis de personalidad, y generación de contenido
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.x_scraper import XScraper
from scrapers.coinmarketcap_scraper import CoinMarketCapScraper
from utils.personality_analyzer import PersonalityAnalyzer
from utils.style_replicator import StyleReplicator


class CryptoNewsReplicator:
    def __init__(self):
        """Inicializa el replicador de noticias crypto"""
        # Cargar variables de entorno
        load_dotenv()

        self.config = {
            'x_username': os.getenv('X_USERNAME', 'zuler'),
            'x_max_tweets': int(os.getenv('X_MAX_TWEETS', 200)),
            'x_scroll_count': int(os.getenv('X_SCROLL_COUNT', 20)),
            'x_headless': os.getenv('X_HEADLESS', 'true').lower() == 'true',
            'cmc_max_articles': int(os.getenv('CMC_MAX_ARTICLES', 20)),
            'cmc_download_images': os.getenv('CMC_DOWNLOAD_IMAGES', 'true').lower() == 'true',
            'model_provider': os.getenv('MODEL_PROVIDER', 'anthropic'),
            'model_name': os.getenv('MODEL_NAME', 'claude-3-5-sonnet-20241022'),
            'model_temperature': float(os.getenv('MODEL_TEMPERATURE', 0.7)),
        }

        self.project_root = Path(__file__).parent
        self.tweets_file = None
        self.analysis_file = None
        self.articles_file = None

    def step_1_scrape_x_profile(self):
        """Paso 1: Scrapear perfil de X (@zuler)"""
        print("\n" + "="*60)
        print("PASO 1: SCRAPING DE PERFIL DE X")
        print("="*60)

        scraper = XScraper(
            username=self.config['x_username'],
            headless=self.config['x_headless']
        )

        tweets = scraper.scrape(
            max_tweets=self.config['x_max_tweets'],
            scroll_count=self.config['x_scroll_count']
        )

        if tweets:
            self.tweets_file = scraper.save_to_json()
            print(f"\n✓ Scraping de X completado: {len(tweets)} tweets extraídos")
            return True
        else:
            print("\n✗ No se pudieron extraer tweets")
            return False

    def step_2_analyze_personality(self):
        """Paso 2: Analizar personalidad y estilo"""
        print("\n" + "="*60)
        print("PASO 2: ANÁLISIS DE PERSONALIDAD")
        print("="*60)

        if not self.tweets_file:
            # Buscar archivo más reciente
            data_dir = self.project_root / "data" / "x_tweets"
            json_files = list(data_dir.glob("*.json"))
            if not json_files:
                print("✗ No se encontraron archivos de tweets")
                return False
            self.tweets_file = max(json_files, key=lambda p: p.stat().st_mtime)
            print(f"Usando archivo: {self.tweets_file}")

        # Crear analizador
        analyzer = PersonalityAnalyzer(str(self.tweets_file))

        # Analizar
        analyzer.analyze()
        analyzer.print_summary()

        # Guardar análisis
        self.analysis_file = analyzer.save_analysis()

        print(f"\n✓ Análisis completado")
        return True

    def step_3_scrape_coinmarketcap(self):
        """Paso 3: Scrapear artículos de CoinMarketCap"""
        print("\n" + "="*60)
        print("PASO 3: SCRAPING DE COINMARKETCAP")
        print("="*60)

        scraper = CoinMarketCapScraper()

        articles = scraper.scrape(
            max_articles=self.config['cmc_max_articles'],
            download_images=self.config['cmc_download_images']
        )

        if articles:
            self.articles_file = scraper.save_to_json()
            print(f"\n✓ Scraping de CoinMarketCap completado: {len(articles)} artículos")
            return True
        else:
            print("\n✗ No se pudieron extraer artículos")
            return False

    def step_4_generate_content(self):
        """Paso 4: Generar contenido con el estilo aprendido"""
        print("\n" + "="*60)
        print("PASO 4: GENERACIÓN DE CONTENIDO")
        print("="*60)

        # Verificar que tenemos análisis
        if not self.analysis_file:
            analysis_dir = self.project_root / "models" / "training_data"
            json_files = list(analysis_dir.glob("*_analysis.json"))
            if not json_files:
                print("✗ No se encontró análisis de personalidad")
                return False
            self.analysis_file = max(json_files, key=lambda p: p.stat().st_mtime)

        # Verificar que tenemos artículos
        if not self.articles_file:
            articles_dir = self.project_root / "data" / "coinmarketcap"
            json_files = list(articles_dir.glob("*.json"))
            if not json_files:
                print("✗ No se encontraron artículos de CoinMarketCap")
                return False
            self.articles_file = max(json_files, key=lambda p: p.stat().st_mtime)

        # Cargar artículos
        with open(self.articles_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
            articles = articles_data.get('articles', [])

        # Crear replicador de estilo
        replicator = StyleReplicator(
            str(self.analysis_file),
            api_provider=self.config['model_provider']
        )

        print(f"Generando contenido para {len(articles)} artículos...\n")

        # Generar contenido para cada artículo
        generated_content = []
        for i, article in enumerate(articles, 1):
            print(f"Procesando artículo {i}/{len(articles)}: {article['title'][:50]}...")

            try:
                result = replicator.generate_from_coinmarketcap(article)
                result['original_article'] = {
                    'title': article['title'],
                    'url': article['url'],
                    'date': article.get('date'),
                    'images': article.get('downloaded_images', [])
                }
                generated_content.append(result)

                # Mostrar preview
                print(f"  Tweet generado: {result['tweet'][:80]}...")

            except Exception as e:
                print(f"  ✗ Error generando contenido: {e}")
                continue

        # Guardar contenido generado
        if generated_content:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.project_root / "output" / f"generated_content_{timestamp}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            output_data = {
                'generated_at': datetime.now().isoformat(),
                'source_profile': self.config['x_username'],
                'model_used': self.config['model_name'],
                'article_count': len(generated_content),
                'content': generated_content
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"\n✓ Contenido generado guardado en: {output_file}")

            # Mostrar algunos ejemplos
            self._show_examples(generated_content)

            return True
        else:
            print("\n✗ No se pudo generar contenido")
            return False

    def _show_examples(self, generated_content, n=3):
        """Muestra ejemplos del contenido generado"""
        print("\n" + "="*60)
        print(f"EJEMPLOS DE CONTENIDO GENERADO (mostrando {min(n, len(generated_content))})")
        print("="*60)

        for i, content in enumerate(generated_content[:n], 1):
            print(f"\n--- Ejemplo {i} ---")
            print(f"Original: {content['original_title']}")
            print(f"URL: {content['original_url']}")
            print(f"\nTweet generado:")
            print(f"  {content['tweet']}")
            print(f"\nIntro de thread:")
            print(f"  {content['thread_intro']}")

    def run_full_pipeline(self):
        """Ejecuta el pipeline completo"""
        print("\n" + "="*70)
        print("  CRYPTO NEWS REPLICATOR - PIPELINE COMPLETO")
        print("="*70)

        success = True

        # Paso 1: Scrapear X
        if not self.step_1_scrape_x_profile():
            print("\n⚠ Advertencia: Falló el scraping de X, intentando continuar con datos existentes...")
            success = False

        # Paso 2: Analizar personalidad
        if not self.step_2_analyze_personality():
            print("\n✗ Error crítico en análisis de personalidad")
            return False

        # Paso 3: Scrapear CoinMarketCap
        if not self.step_3_scrape_coinmarketcap():
            print("\n⚠ Advertencia: Falló el scraping de CoinMarketCap, intentando continuar con datos existentes...")
            success = False

        # Paso 4: Generar contenido
        if not self.step_4_generate_content():
            print("\n✗ Error en generación de contenido")
            return False

        print("\n" + "="*70)
        if success:
            print("  ✓ PIPELINE COMPLETADO EXITOSAMENTE")
        else:
            print("  ⚠ PIPELINE COMPLETADO CON ADVERTENCIAS")
        print("="*70 + "\n")

        return True


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Crypto News Replicator - Extrae y replica noticias con personalidad personalizada'
    )
    parser.add_argument(
        '--step',
        type=int,
        choices=[1, 2, 3, 4],
        help='Ejecutar solo un paso específico (1: scrape X, 2: analizar, 3: scrape CMC, 4: generar)'
    )
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Saltar scraping y usar datos existentes'
    )

    args = parser.parse_args()

    # Crear replicador
    replicator = CryptoNewsReplicator()

    # Ejecutar según argumentos
    if args.step:
        # Ejecutar paso específico
        steps = {
            1: replicator.step_1_scrape_x_profile,
            2: replicator.step_2_analyze_personality,
            3: replicator.step_3_scrape_coinmarketcap,
            4: replicator.step_4_generate_content
        }
        success = steps[args.step]()
        sys.exit(0 if success else 1)

    elif args.skip_scraping:
        # Solo análisis y generación
        success = (
            replicator.step_2_analyze_personality() and
            replicator.step_4_generate_content()
        )
        sys.exit(0 if success else 1)

    else:
        # Pipeline completo
        success = replicator.run_full_pipeline()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
