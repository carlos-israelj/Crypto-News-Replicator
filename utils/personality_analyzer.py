"""
Analizador de personalidad y estilo de escritura
Analiza tweets para extraer patrones de escritura, vocabulario, tono, etc.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import List, Dict


class PersonalityAnalyzer:
    def __init__(self, tweets_data):
        """
        Inicializa el analizador de personalidad

        Args:
            tweets_data: Lista de tweets o path a archivo JSON
        """
        if isinstance(tweets_data, str):
            # Cargar desde archivo
            with open(tweets_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tweets = data.get('tweets', [])
                self.username = data.get('username', 'unknown')
        else:
            self.tweets = tweets_data
            self.username = 'unknown'

        self.analysis = {}

    def analyze(self):
        """
        Realiza el análisis completo de personalidad

        Returns:
            Diccionario con el análisis completo
        """
        print(f"Analizando {len(self.tweets)} tweets de @{self.username}...")

        # Filtrar tweets originales (no retweets)
        original_tweets = [t for t in self.tweets if not t.get('is_retweet', False)]
        print(f"Tweets originales: {len(original_tweets)}")

        # Diferentes análisis - MUCHO MÁS DETALLADOS
        self.analysis = {
            'username': self.username,
            'total_tweets': len(self.tweets),
            'original_tweets': len(original_tweets),
            'style_patterns': self._analyze_style(original_tweets),
            'vocabulary': self._analyze_vocabulary(original_tweets),
            'topics': self._analyze_topics(original_tweets),
            'tone': self._analyze_tone(original_tweets),
            'structure': self._analyze_structure(original_tweets),
            'engagement': self._analyze_engagement(original_tweets),
            'examples': self._get_top_tweets(original_tweets),
            # NUEVOS ANÁLISIS MÁS ESPECÍFICOS
            'content_type': self._analyze_content_type(original_tweets),
            'linguistic_register': self._analyze_linguistic_register(original_tweets),
            'narrative_style': self._analyze_narrative_style(original_tweets),
            'opening_patterns': self._analyze_opening_patterns(original_tweets),
            'closing_patterns': self._analyze_closing_patterns(original_tweets),
            'data_usage': self._analyze_data_usage(original_tweets),
            'sentence_patterns': self._analyze_sentence_patterns(original_tweets)
        }

        return self.analysis

    def _analyze_style(self, tweets: List[Dict]) -> Dict:
        """Analiza el estilo de escritura"""
        texts = [t['text'] for t in tweets]

        # Uso de emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos
            "\U0001F680-\U0001F6FF"  # transporte
            "\U0001F1E0-\U0001F1FF"  # banderas
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        tweets_with_emoji = sum(1 for t in texts if emoji_pattern.search(t))

        # Uso de hashtags
        tweets_with_hashtags = sum(1 for t in texts if '#' in t)
        hashtags = []
        for text in texts:
            hashtags.extend(re.findall(r'#\w+', text))

        # Uso de menciones
        tweets_with_mentions = sum(1 for t in texts if '@' in t)

        # Longitud promedio
        avg_length = sum(len(t) for t in texts) / len(texts) if texts else 0

        # Uso de mayúsculas
        all_caps_words = []
        for text in texts:
            all_caps_words.extend([w for w in text.split() if w.isupper() and len(w) > 1])

        # Uso de puntuación enfática
        exclamation_count = sum(t.count('!') for t in texts)
        question_count = sum(t.count('?') for t in texts)

        return {
            'emoji_usage': {
                'percentage': (tweets_with_emoji / len(tweets) * 100) if tweets else 0,
                'count': tweets_with_emoji
            },
            'hashtag_usage': {
                'percentage': (tweets_with_hashtags / len(tweets) * 100) if tweets else 0,
                'count': tweets_with_hashtags,
                'most_common': Counter(hashtags).most_common(10)
            },
            'mention_usage': {
                'percentage': (tweets_with_mentions / len(tweets) * 100) if tweets else 0
            },
            'avg_tweet_length': round(avg_length, 2),
            'caps_usage': {
                'total_caps_words': len(all_caps_words),
                'common_caps_words': Counter(all_caps_words).most_common(5)
            },
            'punctuation': {
                'exclamation_marks': exclamation_count,
                'question_marks': question_count,
                'avg_exclamations_per_tweet': round(exclamation_count / len(tweets), 2) if tweets else 0
            }
        }

    def _analyze_vocabulary(self, tweets: List[Dict]) -> Dict:
        """Analiza el vocabulario utilizado"""
        all_text = ' '.join([t['text'] for t in tweets])

        # Palabras más comunes (excluyendo stopwords básicas)
        stopwords = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber',
                    'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo',
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'it', 'this', 'that'}

        # Limpiar y tokenizar
        words = re.findall(r'\b[a-záéíóúñA-ZÁÉÍÓÚÑ]+\b', all_text.lower())
        filtered_words = [w for w in words if w not in stopwords and len(w) > 2]

        # Palabras de crypto/tech
        crypto_keywords = ['crypto', 'bitcoin', 'btc', 'ethereum', 'eth', 'blockchain', 'defi',
                          'nft', 'web3', 'token', 'coin', 'trading', 'market', 'bull', 'bear']
        crypto_word_count = sum(1 for w in filtered_words if w in crypto_keywords)

        return {
            'total_words': len(words),
            'unique_words': len(set(filtered_words)),
            'most_common_words': Counter(filtered_words).most_common(20),
            'crypto_focus': {
                'crypto_word_count': crypto_word_count,
                'percentage': (crypto_word_count / len(filtered_words) * 100) if filtered_words else 0
            }
        }

    def _analyze_topics(self, tweets: List[Dict]) -> Dict:
        """Analiza los temas principales"""
        texts = [t['text'].lower() for t in tweets]

        # Categorías de temas
        topics = {
            'crypto': ['crypto', 'bitcoin', 'ethereum', 'btc', 'eth', 'blockchain', 'defi', 'nft'],
            'trading': ['trading', 'market', 'price', 'bull', 'bear', 'pump', 'dump', 'long', 'short'],
            'technology': ['tech', 'ai', 'software', 'code', 'developer', 'programming'],
            'finance': ['money', 'investment', 'profit', 'loss', 'finance', 'portfolio'],
            'social': ['community', 'people', 'team', 'together', 'fam']
        }

        topic_counts = {}
        for topic, keywords in topics.items():
            count = sum(
                1 for text in texts
                if any(keyword in text for keyword in keywords)
            )
            topic_counts[topic] = {
                'count': count,
                'percentage': (count / len(tweets) * 100) if tweets else 0
            }

        return topic_counts

    def _analyze_tone(self, tweets: List[Dict]) -> Dict:
        """Analiza el tono de los tweets"""
        texts = [t['text'].lower() for t in tweets]

        # Palabras positivas y negativas (básico)
        positive_words = ['good', 'great', 'amazing', 'awesome', 'love', 'best', 'win', 'up',
                         'bueno', 'genial', 'increíble', 'amor', 'mejor', 'ganar']
        negative_words = ['bad', 'worst', 'hate', 'down', 'loss', 'fail', 'scam',
                         'malo', 'peor', 'odio', 'pérdida', 'fallar', 'estafa']

        positive_count = sum(
            sum(1 for word in positive_words if word in text)
            for text in texts
        )
        negative_count = sum(
            sum(1 for word in negative_words if word in text)
            for text in texts
        )

        # Humor/sarcasmo (indicadores básicos)
        humor_indicators = ['lol', 'lmao', 'haha', 'jaja', '😂', '🤣']
        humor_count = sum(1 for text in texts if any(ind in text for ind in humor_indicators))

        return {
            'positive_sentiment': positive_count,
            'negative_sentiment': negative_count,
            'sentiment_ratio': (positive_count / negative_count) if negative_count > 0 else positive_count,
            'humor_percentage': (humor_count / len(tweets) * 100) if tweets else 0
        }

    def _analyze_structure(self, tweets: List[Dict]) -> Dict:
        """Analiza la estructura de los tweets"""
        texts = [t['text'] for t in tweets]

        # Threads (tweets que empiezan con números)
        thread_pattern = re.compile(r'^\d+[/\.]')
        thread_tweets = sum(1 for t in texts if thread_pattern.match(t))

        # Tweets con links
        link_pattern = re.compile(r'https?://\S+')
        tweets_with_links = sum(1 for t in texts if link_pattern.search(t))

        # Tweets con preguntas
        tweets_with_questions = sum(1 for t in texts if '?' in t)

        # Uso de líneas/separadores
        separator_tweets = sum(1 for t in texts if '---' in t or '===' in t or '___' in t)

        return {
            'thread_usage': {
                'count': thread_tweets,
                'percentage': (thread_tweets / len(tweets) * 100) if tweets else 0
            },
            'link_usage': {
                'count': tweets_with_links,
                'percentage': (tweets_with_links / len(tweets) * 100) if tweets else 0
            },
            'question_usage': {
                'count': tweets_with_questions,
                'percentage': (tweets_with_questions / len(tweets) * 100) if tweets else 0
            },
            'visual_separators': separator_tweets
        }

    def _analyze_engagement(self, tweets: List[Dict]) -> Dict:
        """Analiza métricas de engagement"""
        if not tweets:
            return {}

        likes = [t.get('like_count', 0) for t in tweets]
        retweets = [t.get('retweet_count', 0) for t in tweets]
        replies = [t.get('reply_count', 0) for t in tweets]

        return {
            'avg_likes': round(sum(likes) / len(likes), 2) if likes else 0,
            'avg_retweets': round(sum(retweets) / len(retweets), 2) if retweets else 0,
            'avg_replies': round(sum(replies) / len(replies), 2) if replies else 0,
            'max_likes': max(likes) if likes else 0,
            'max_retweets': max(retweets) if retweets else 0
        }

    def _get_top_tweets(self, tweets: List[Dict], n=5) -> List[Dict]:
        """Obtiene los tweets con mejor engagement"""
        # Ordenar por engagement (suma de likes + retweets)
        sorted_tweets = sorted(
            tweets,
            key=lambda t: t.get('like_count', 0) + t.get('retweet_count', 0),
            reverse=True
        )

        return [
            {
                'text': t['text'],
                'likes': t.get('like_count', 0),
                'retweets': t.get('retweet_count', 0),
                'timestamp': t.get('timestamp')
            }
            for t in sorted_tweets[:n]
        ]

    def _analyze_content_type(self, tweets: List[Dict]) -> Dict:
        """Analiza el TIPO de contenido que publica"""
        texts = [t['text'].lower() for t in tweets]

        # Patrones para diferentes tipos de contenido
        types = {
            'informative': {
                'keywords': ['según', 'reporta', 'anuncia', 'confirma', 'informa',
                           'according', 'reports', 'announces', 'confirms', 'breaking'],
                'count': 0
            },
            'opinion': {
                'keywords': ['creo', 'pienso', 'considero', 'mi opinión', 'personalmente',
                           'i think', 'i believe', 'in my opinion', 'personally', 'imo'],
                'count': 0
            },
            'prediction': {
                'keywords': ['predicción', 'espero', 'llegará', 'alcanzará', 'veremos',
                           'prediction', 'expect', 'will reach', 'will hit', "we'll see"],
                'count': 0
            },
            'educational': {
                'keywords': ['cómo', 'qué es', 'explicación', 'guía', 'tutorial',
                           'how to', 'what is', 'explanation', 'guide', 'tutorial'],
                'count': 0
            },
            'analysis': {
                'keywords': ['análisis', 'porque', 'razón', 'debido a', 'factor',
                           'analysis', 'because', 'reason', 'due to', 'factor'],
                'count': 0
            }
        }

        for text in texts:
            for content_type, data in types.items():
                if any(keyword in text for keyword in data['keywords']):
                    types[content_type]['count'] += 1

        # Calcular porcentajes
        total = len(tweets)
        for content_type in types:
            types[content_type]['percentage'] = (types[content_type]['count'] / total * 100) if total > 0 else 0

        return types

    def _analyze_linguistic_register(self, tweets: List[Dict]) -> Dict:
        """Analiza el registro lingüístico (formal vs casual vs coloquial)"""
        texts = [t['text'] for t in tweets]

        # Indicadores de registro formal
        formal_indicators = ['mediante', 'asimismo', 'no obstante', 'por consiguiente',
                           'however', 'therefore', 'furthermore', 'consequently']

        # Indicadores de registro casual/coloquial
        casual_indicators = ['jaja', 'lol', 'bro', 'vibes', 'lit', 'ngl', 'tbh',
                           'tipo', 'osea', 'we', 'pana']

        # Contracciones (más casual)
        contractions = ["'ll", "'re", "'ve", "'d", "n't", "gonna", "wanna"]

        formal_count = sum(
            sum(1 for ind in formal_indicators if ind in text.lower())
            for text in texts
        )

        casual_count = sum(
            sum(1 for ind in casual_indicators if ind in text.lower())
            for text in texts
        )

        contraction_count = sum(
            sum(1 for cont in contractions if cont in text)
            for text in texts
        )

        total_words = sum(len(text.split()) for text in texts)

        return {
            'formal_score': formal_count,
            'casual_score': casual_count + contraction_count,
            'register_type': 'formal' if formal_count > casual_count else 'casual',
            'formality_ratio': formal_count / casual_count if casual_count > 0 else formal_count,
            'uses_contractions': contraction_count > 0,
            'contraction_frequency': (contraction_count / total_words * 100) if total_words > 0 else 0
        }

    def _analyze_narrative_style(self, tweets: List[Dict]) -> Dict:
        """Analiza el estilo narrativo (primera persona, tercera, imperativo)"""
        texts = [t['text'].lower() for t in tweets]

        # Primera persona
        first_person = ['yo', 'mi', 'mis', 'me', 'conmigo', 'i', 'my', 'me', 'mine']
        first_person_count = sum(
            sum(1 for word in first_person if f' {word} ' in f' {text} ')
            for text in texts
        )

        # Segunda persona / Imperativo (habla directamente al lector)
        second_person = ['tú', 'tu', 'te', 'contigo', 'you', 'your', 'yourself']
        imperative_markers = ['no olvides', 'recuerda', 'mira', "don't forget", 'remember', 'check', 'watch']
        second_person_count = sum(
            sum(1 for word in second_person + imperative_markers if word in text)
            for text in texts
        )

        # Tercera persona / objetivo
        third_person_markers = ['el precio', 'bitcoin', 'ethereum', 'el mercado',
                               'the price', 'the market', 'analysts', 'reports']
        third_person_count = sum(
            sum(1 for marker in third_person_markers if marker in text)
            for text in texts
        )

        total = first_person_count + second_person_count + third_person_count

        return {
            'first_person_usage': {
                'count': first_person_count,
                'percentage': (first_person_count / total * 100) if total > 0 else 0
            },
            'second_person_usage': {
                'count': second_person_count,
                'percentage': (second_person_count / total * 100) if total > 0 else 0
            },
            'third_person_usage': {
                'count': third_person_count,
                'percentage': (third_person_count / total * 100) if total > 0 else 0
            },
            'dominant_style': max(
                [('first_person', first_person_count),
                 ('second_person', second_person_count),
                 ('third_person', third_person_count)],
                key=lambda x: x[1]
            )[0]
        }

    def _analyze_opening_patterns(self, tweets: List[Dict]) -> Dict:
        """Analiza cómo empieza típicamente los mensajes"""
        texts = [t['text'] for t in tweets]

        opening_words = []
        opening_patterns = {
            'question': 0,  # Empieza con pregunta
            'number': 0,    # Empieza con número
            'emoji': 0,     # Empieza con emoji
            'exclamation': 0,  # Empieza con exclamación
            'statement': 0   # Declaración directa
        }

        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )

        for text in texts:
            first_word = text.split()[0] if text.split() else ''
            opening_words.append(first_word.lower().strip('.,!?'))

            # Clasificar tipo de apertura
            if text.strip().startswith('?') or any(text.lower().startswith(q) for q in ['qué', 'cómo', 'cuándo', 'what', 'how', 'when', 'why', 'where']):
                opening_patterns['question'] += 1
            elif text[0].isdigit():
                opening_patterns['number'] += 1
            elif emoji_pattern.match(text):
                opening_patterns['emoji'] += 1
            elif text.startswith('!') or text.lower().startswith(('wow', 'omg', 'breaking')):
                opening_patterns['exclamation'] += 1
            else:
                opening_patterns['statement'] += 1

        # Palabras más comunes para empezar
        opening_words_clean = [w for w in opening_words if len(w) > 2]
        common_openings = Counter(opening_words_clean).most_common(10)

        total = len(tweets)
        for pattern in opening_patterns:
            opening_patterns[pattern] = {
                'count': opening_patterns[pattern],
                'percentage': (opening_patterns[pattern] / total * 100) if total > 0 else 0
            }

        return {
            'patterns': opening_patterns,
            'common_first_words': common_openings,
            'dominant_opening': max(opening_patterns.items(), key=lambda x: x[1]['count'])[0]
        }

    def _analyze_closing_patterns(self, tweets: List[Dict]) -> Dict:
        """Analiza cómo termina típicamente los mensajes"""
        texts = [t['text'] for t in tweets]

        closing_patterns = {
            'emoji': 0,
            'question': 0,
            'exclamation': 0,
            'period': 0,
            'ellipsis': 0,
            'call_to_action': 0
        }

        cta_markers = ['screenshot', 'rt', 'share', 'follow', 'check', 'link', 'comparte', 'sígueme']

        for text in texts:
            text_end = text.strip()[-20:] if len(text) > 20 else text.strip()

            if text.strip().endswith(('?', '¿')):
                closing_patterns['question'] += 1
            elif text.strip().endswith(('!', '¡')):
                closing_patterns['exclamation'] += 1
            elif text.strip().endswith('...'):
                closing_patterns['ellipsis'] += 1
            elif text.strip().endswith('.'):
                closing_patterns['period'] += 1

            if any(cta in text_end.lower() for cta in cta_markers):
                closing_patterns['call_to_action'] += 1

        total = len(tweets)
        for pattern in closing_patterns:
            closing_patterns[pattern] = {
                'count': closing_patterns[pattern],
                'percentage': (closing_patterns[pattern] / total * 100) if total > 0 else 0
            }

        return {
            'patterns': closing_patterns,
            'dominant_closing': max(closing_patterns.items(), key=lambda x: x[1]['count'])[0]
        }

    def _analyze_data_usage(self, tweets: List[Dict]) -> Dict:
        """Analiza uso de números, estadísticas y datos"""
        texts = [t['text'] for t in tweets]

        # Números y estadísticas
        number_pattern = re.compile(r'\d+')
        percentage_pattern = re.compile(r'\d+%')
        price_pattern = re.compile(r'\$\d+')

        tweets_with_numbers = sum(1 for text in texts if number_pattern.search(text))
        tweets_with_percentages = sum(1 for text in texts if percentage_pattern.search(text))
        tweets_with_prices = sum(1 for text in texts if price_pattern.search(text))

        # Extraer todos los números
        all_numbers = []
        for text in texts:
            all_numbers.extend(number_pattern.findall(text))

        total = len(tweets)

        return {
            'uses_numbers': tweets_with_numbers > 0,
            'number_frequency': (tweets_with_numbers / total * 100) if total > 0 else 0,
            'percentage_usage': (tweets_with_percentages / total * 100) if total > 0 else 0,
            'price_mentions': (tweets_with_prices / total * 100) if total > 0 else 0,
            'data_heavy': tweets_with_numbers / total > 0.5 if total > 0 else False,
            'total_numbers_used': len(all_numbers)
        }

    def _analyze_sentence_patterns(self, tweets: List[Dict]) -> Dict:
        """Analiza patrones de estructura de oraciones"""
        texts = [t['text'] for t in tweets]

        sentence_lengths = []
        for text in texts:
            # Dividir en oraciones aproximadamente
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            sentence_lengths.extend([len(s.split()) for s in sentences])

        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        # Complejidad de oraciones
        complex_markers = [',', ';', ':', 'que', 'porque', 'mientras', 'aunque',
                          'which', 'that', 'because', 'while', 'although']

        simple_sentences = 0
        complex_sentences = 0

        for text in texts:
            has_complex_marker = any(marker in text.lower() for marker in complex_markers)
            if has_complex_marker:
                complex_sentences += 1
            else:
                simple_sentences += 1

        return {
            'avg_sentence_length_words': round(avg_sentence_length, 1),
            'sentence_complexity': 'complex' if complex_sentences > simple_sentences else 'simple',
            'simple_vs_complex_ratio': simple_sentences / complex_sentences if complex_sentences > 0 else simple_sentences
        }

    def save_analysis(self, output_path=None):
        """Guarda el análisis en un archivo JSON"""
        if output_path is None:
            output_path = f"models/training_data/{self.username}_analysis.json"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, ensure_ascii=False, indent=2)

        print(f"\nAnálisis guardado en: {output_path}")
        return output_path

    def print_summary(self):
        """Imprime un resumen del análisis"""
        if not self.analysis:
            print("No hay análisis disponible. Ejecuta analyze() primero.")
            return

        print("\n" + "="*60)
        print(f"ANÁLISIS DE PERSONALIDAD: @{self.username}")
        print("="*60)

        print(f"\nTweets totales: {self.analysis['total_tweets']}")
        print(f"Tweets originales: {self.analysis['original_tweets']}")

        style = self.analysis['style_patterns']
        print(f"\n--- ESTILO ---")
        print(f"Longitud promedio: {style['avg_tweet_length']} caracteres")
        print(f"Uso de emojis: {style['emoji_usage']['percentage']:.1f}%")
        print(f"Uso de hashtags: {style['hashtag_usage']['percentage']:.1f}%")
        print(f"Exclamaciones por tweet: {style['punctuation']['avg_exclamations_per_tweet']}")

        vocab = self.analysis['vocabulary']
        print(f"\n--- VOCABULARIO ---")
        print(f"Palabras únicas: {vocab['unique_words']}")
        print(f"Enfoque en crypto: {vocab['crypto_focus']['percentage']:.1f}%")
        print(f"Palabras más comunes: {', '.join([w for w, _ in vocab['most_common_words'][:5]])}")

        topics = self.analysis['topics']
        print(f"\n--- TEMAS PRINCIPALES ---")
        sorted_topics = sorted(topics.items(), key=lambda x: x[1]['percentage'], reverse=True)
        for topic, data in sorted_topics[:3]:
            print(f"{topic.capitalize()}: {data['percentage']:.1f}%")

        tone = self.analysis['tone']
        print(f"\n--- TONO ---")
        print(f"Ratio sentimiento (pos/neg): {tone['sentiment_ratio']:.2f}")
        print(f"Tweets con humor: {tone['humor_percentage']:.1f}%")

        print("\n" + "="*60)


def main():
    """Función principal para probar el analizador"""
    import sys

    if len(sys.argv) > 1:
        tweets_file = sys.argv[1]
    else:
        # Buscar el archivo más reciente
        data_dir = Path("data/x_tweets")
        if not data_dir.exists():
            print("No se encontró el directorio data/x_tweets")
            return

        json_files = list(data_dir.glob("*.json"))
        if not json_files:
            print("No se encontraron archivos JSON")
            return

        tweets_file = max(json_files, key=lambda p: p.stat().st_mtime)
        print(f"Usando archivo: {tweets_file}")

    # Crear analizador
    analyzer = PersonalityAnalyzer(str(tweets_file))

    # Analizar
    analyzer.analyze()

    # Mostrar resumen
    analyzer.print_summary()

    # Guardar análisis
    analyzer.save_analysis()


if __name__ == "__main__":
    main()
