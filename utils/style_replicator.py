"""
Replicador de estilo de escritura
Usa el análisis de personalidad para generar contenido con el mismo estilo
"""

import json
import os
from pathlib import Path
from typing import Optional
from anthropic import Anthropic
import openai
import google.generativeai as genai


class StyleReplicator:
    def __init__(self, analysis_file: str, api_provider: str = "google"):
        """
        Inicializa el replicador de estilo

        Args:
            analysis_file: Path al archivo de análisis de personalidad
            api_provider: "anthropic", "openai" o "google"
        """
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)

        self.api_provider = api_provider
        self.username = self.analysis.get('username', 'unknown')

        # Inicializar cliente de API
        if api_provider == "anthropic":
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY no encontrada en variables de entorno")
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
        elif api_provider == "openai":
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY no encontrada en variables de entorno")
            openai.api_key = api_key
            self.model = "gpt-4-turbo-preview"
        elif api_provider == "google":
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY no encontrada en variables de entorno")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            self.model = "gemini-1.5-flash"
        else:
            raise ValueError(f"API provider no soportado: {api_provider}")

    def build_style_prompt(self) -> str:
        """
        Construye un prompt detallado basado en el análisis de personalidad

        Returns:
            String con el prompt de estilo
        """
        style = self.analysis.get('style_patterns', {})
        vocab = self.analysis.get('vocabulary', {})
        topics = self.analysis.get('topics', {})
        tone = self.analysis.get('tone', {})
        structure = self.analysis.get('structure', {})
        examples = self.analysis.get('examples', [])

        # Construcción del prompt
        prompt_parts = [
            f"Eres un escritor que replica el estilo de @{self.username}.",
            "\nCaracterísticas clave del estilo:",
        ]

        # Longitud y estructura
        avg_length = style.get('avg_tweet_length', 0)
        prompt_parts.append(f"\n- Longitud promedio de escritura: {avg_length:.0f} caracteres")

        # Emojis
        emoji_pct = style.get('emoji_usage', {}).get('percentage', 0)
        if emoji_pct > 30:
            prompt_parts.append(f"- USA emojis frecuentemente ({emoji_pct:.0f}% de los mensajes)")
        elif emoji_pct > 10:
            prompt_parts.append(f"- Usa emojis moderadamente ({emoji_pct:.0f}% de los mensajes)")
        else:
            prompt_parts.append(f"- Usa pocos emojis ({emoji_pct:.0f}% de los mensajes)")

        # Hashtags
        hashtag_pct = style.get('hashtag_usage', {}).get('percentage', 0)
        if hashtag_pct > 20:
            top_hashtags = style.get('hashtag_usage', {}).get('most_common', [])[:5]
            hashtag_list = ', '.join([h for h, _ in top_hashtags])
            prompt_parts.append(f"- Usa hashtags frecuentemente. Hashtags comunes: {hashtag_list}")

        # Puntuación
        punct = style.get('punctuation', {})
        avg_excl = punct.get('avg_exclamations_per_tweet', 0)
        if avg_excl > 1:
            prompt_parts.append(f"- Usa signos de exclamación con frecuencia (promedio: {avg_excl:.1f} por mensaje)")

        # Mayúsculas
        caps = style.get('caps_usage', {})
        if caps.get('total_caps_words', 0) > 10:
            common_caps = caps.get('common_caps_words', [])[:3]
            if common_caps:
                caps_words = ', '.join([w for w, _ in common_caps])
                prompt_parts.append(f"- Usa MAYÚSCULAS para énfasis. Palabras comunes: {caps_words}")

        # Vocabulario
        common_words = vocab.get('most_common_words', [])[:10]
        if common_words:
            word_list = ', '.join([w for w, _ in common_words])
            prompt_parts.append(f"\n- Vocabulario frecuente: {word_list}")

        # Enfoque en crypto
        crypto_pct = vocab.get('crypto_focus', {}).get('percentage', 0)
        if crypto_pct > 20:
            prompt_parts.append(f"- Fuerte enfoque en temas de crypto/blockchain ({crypto_pct:.0f}% del contenido)")

        # Temas principales
        sorted_topics = sorted(topics.items(), key=lambda x: x[1].get('percentage', 0), reverse=True)
        top_topics = [topic for topic, data in sorted_topics[:3] if data.get('percentage', 0) > 10]
        if top_topics:
            topics_list = ', '.join(top_topics)
            prompt_parts.append(f"- Temas principales: {topics_list}")

        # Tono
        sentiment_ratio = tone.get('sentiment_ratio', 1)
        if sentiment_ratio > 2:
            prompt_parts.append("- Tono generalmente POSITIVO y optimista")
        elif sentiment_ratio < 0.5:
            prompt_parts.append("- Tono a veces crítico o escéptico")

        humor_pct = tone.get('humor_percentage', 0)
        if humor_pct > 15:
            prompt_parts.append(f"- Usa humor frecuentemente ({humor_pct:.0f}% de los mensajes)")

        # Estructura
        question_pct = structure.get('question_usage', {}).get('percentage', 0)
        if question_pct > 20:
            prompt_parts.append(f"- Hace preguntas con frecuencia ({question_pct:.0f}% de los mensajes)")

        link_pct = structure.get('link_usage', {}).get('percentage', 0)
        if link_pct > 30:
            prompt_parts.append(f"- Incluye links frecuentemente ({link_pct:.0f}% de los mensajes)")

        # Ejemplos
        if examples:
            prompt_parts.append("\n\nEjemplos de escritura real:")
            for i, example in enumerate(examples[:3], 1):
                text = example.get('text', '')[:200]  # Limitar longitud
                prompt_parts.append(f"\nEjemplo {i}: \"{text}\"")

        # Instrucciones finales
        prompt_parts.append("\n\nCuando escribas contenido:")
        prompt_parts.append("1. Replica estos patrones de estilo de manera natural")
        prompt_parts.append("2. Mantén la personalidad y tono característicos")
        prompt_parts.append("3. Usa vocabulario y estructuras similares")
        prompt_parts.append("4. NO copies contenido literalmente, adapta el estilo al nuevo tema")

        return ''.join(prompt_parts)

    def generate_content(self, source_text: str, content_type: str = "tweet",
                        temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Genera contenido replicando el estilo

        Args:
            source_text: Texto original a reescribir
            content_type: Tipo de contenido ("tweet", "thread", "article")
            temperature: Temperatura para generación (0-1)
            max_tokens: Máximo de tokens a generar

        Returns:
            Contenido generado con el estilo replicado
        """
        # Construir prompt
        style_prompt = self.build_style_prompt()

        user_prompt = f"""Basándote en el estilo descrito, reescribe el siguiente contenido de {content_type}:

CONTENIDO ORIGINAL:
{source_text}

CONTENIDO REESCRITO (con el estilo de @{self.username}):"""

        # Generar con la API correspondiente
        if self.api_provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=style_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text

        elif self.api_provider == "openai":
            response = openai.ChatCompletion.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": style_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content

        elif self.api_provider == "google":
            # Para Gemini, combinar system y user prompt
            full_prompt = f"{style_prompt}\n\n{user_prompt}"
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text

    def generate_from_coinmarketcap(self, article_data: dict) -> dict:
        """
        Genera contenido a partir de un artículo de CoinMarketCap

        Args:
            article_data: Datos del artículo (título, contenido, etc.)

        Returns:
            Diccionario con el contenido generado
        """
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        url = article_data.get('url', '')

        # Crear resumen del artículo
        source_text = f"Título: {title}\n\nContenido: {content[:500]}..."

        # Generar contenido en diferentes formatos
        result = {
            'original_title': title,
            'original_url': url,
            'tweet': self.generate_content(source_text, content_type="tweet", max_tokens=280),
            'thread_intro': self.generate_content(
                source_text,
                content_type="thread",
                max_tokens=280
            ),
            'article_intro': self.generate_content(
                source_text,
                content_type="article",
                max_tokens=500
            )
        }

        return result


def main():
    """Función de prueba"""
    import sys

    # Buscar archivo de análisis más reciente
    analysis_dir = Path("models/training_data")
    if not analysis_dir.exists():
        print("No se encontró el directorio models/training_data")
        return

    json_files = list(analysis_dir.glob("*_analysis.json"))
    if not json_files:
        print("No se encontraron archivos de análisis")
        print("Ejecuta primero el personality_analyzer.py")
        return

    analysis_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Usando análisis: {analysis_file}\n")

    # Crear replicador
    replicator = StyleReplicator(str(analysis_file), api_provider="anthropic")

    # Mostrar prompt de estilo
    print("="*60)
    print("PROMPT DE ESTILO GENERADO:")
    print("="*60)
    print(replicator.build_style_prompt())
    print("\n" + "="*60)

    # Ejemplo de uso
    if len(sys.argv) > 1:
        test_text = ' '.join(sys.argv[1:])
        print(f"\nTexto original: {test_text}")
        print("\nGenerando versión con estilo...")

        generated = replicator.generate_content(test_text)
        print(f"\nTexto generado:\n{generated}")


if __name__ == "__main__":
    main()
