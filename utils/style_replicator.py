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
            self.client = genai.GenerativeModel('models/gemini-2.5-flash')
            self.model = "models/gemini-2.5-flash"
        else:
            raise ValueError(f"API provider no soportado: {api_provider}")

    def _detect_language(self, text: str) -> str:
        """Detecta el idioma del texto (simple heuristic)"""
        # Palabras comunes en inglés vs español
        english_words = {'the', 'and', 'is', 'to', 'in', 'that', 'it', 'for', 'as', 'with'}
        spanish_words = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'por', 'con', 'para'}

        words = text.lower().split()[:100]  # Primeras 100 palabras
        english_count = sum(1 for w in words if w in english_words)
        spanish_count = sum(1 for w in words if w in spanish_words)

        return 'english' if english_count > spanish_count else 'spanish'

    def build_style_prompt(self, target_language: str = 'auto') -> str:
        """
        Construye un prompt detallado basado en el análisis de personalidad

        Args:
            target_language: 'english', 'spanish' o 'auto'

        Returns:
            String con el prompt de estilo
        """
        style = self.analysis.get('style_patterns', {})
        vocab = self.analysis.get('vocabulary', {})
        topics = self.analysis.get('topics', {})
        tone = self.analysis.get('tone', {})
        structure = self.analysis.get('structure', {})
        examples = self.analysis.get('examples', [])

        # Construcción del prompt - Mucho más específico
        lang_instruction = ""
        if target_language == 'english':
            lang_instruction = "\n**IMPORTANTE: You MUST write in ENGLISH, matching the original content language.**"
        elif target_language == 'spanish':
            lang_instruction = "\n**IMPORTANTE: Debes escribir en ESPAÑOL, respetando el idioma del contenido original.**"

        prompt_parts = [
            f"You are a content writer who EXACTLY replicates the unique writing style of @{self.username}.",
            lang_instruction,
            "\n\n=== CORE WRITING STYLE PATTERNS ===",
        ]

        # Longitud y estructura - más específico
        avg_length = style.get('avg_tweet_length', 0)
        prompt_parts.append(f"\n• LENGTH: Target ~{avg_length:.0f} characters per message")
        prompt_parts.append(f"• Keep messages concise and punchy" if avg_length < 150 else "• Allow longer, detailed messages")

        # Emojis - muy específico
        emoji_pct = style.get('emoji_usage', {}).get('percentage', 0)
        if emoji_pct > 50:
            prompt_parts.append(f"\n• EMOJIS: Use 1-3 emojis per message ({emoji_pct:.0f}% usage)")
            prompt_parts.append("  Common placements: end of message, after key points, for emphasis")
        elif emoji_pct > 20:
            prompt_parts.append(f"\n• EMOJIS: Moderate use - 1 emoji occasionally ({emoji_pct:.0f}% usage)")
        else:
            prompt_parts.append(f"\n• EMOJIS: Minimal/no emoji use ({emoji_pct:.0f}% usage)")

        # Hashtags - muy específico
        hashtag_pct = style.get('hashtag_usage', {}).get('percentage', 0)
        if hashtag_pct > 20:
            top_hashtags = style.get('hashtag_usage', {}).get('most_common', [])[:5]
            hashtag_list = ', '.join([h for h, _ in top_hashtags])
            prompt_parts.append(f"\n• HASHTAGS: Use frequently ({hashtag_pct:.0f}%)")
            prompt_parts.append(f"  Preferred tags: {hashtag_list}")
            prompt_parts.append("  Placement: Usually at end of message")
        elif hashtag_pct > 5:
            prompt_parts.append(f"\n• HASHTAGS: Occasional use ({hashtag_pct:.0f}%)")
        else:
            prompt_parts.append(f"\n• HASHTAGS: Rarely/never use hashtags")

        # Puntuación - mucho más específico
        punct = style.get('punctuation', {})
        avg_excl = punct.get('avg_exclamations_per_tweet', 0)
        if avg_excl > 1.5:
            prompt_parts.append(f"\n• PUNCTUATION: Heavy exclamation use! ({avg_excl:.1f} per message)")
            prompt_parts.append("  Shows enthusiasm and energy in writing")
        elif avg_excl > 0.5:
            prompt_parts.append(f"\n• PUNCTUATION: Moderate exclamation use ({avg_excl:.1f} per message)")
        else:
            prompt_parts.append(f"\n• PUNCTUATION: Minimal exclamation marks, more measured tone")

        # Mayúsculas - muy específico
        caps = style.get('caps_usage', {})
        if caps.get('total_caps_words', 0) > 10:
            common_caps = caps.get('common_caps_words', [])[:3]
            if common_caps:
                caps_words = ', '.join([w for w, _ in common_caps])
                prompt_parts.append(f"\n• CAPS FOR EMPHASIS: {caps_words}")
                prompt_parts.append("  Use ALL CAPS for key words/phrases to grab attention")

        # Vocabulario - mucho más específico
        common_words = vocab.get('most_common_words', [])[:15]
        if common_words:
            word_list = ', '.join([w for w, _ in common_words[:10]])
            prompt_parts.append(f"\n\n=== VOCABULARY & WORD CHOICE ===")
            prompt_parts.append(f"\n• KEY WORDS: {word_list}")
            prompt_parts.append("• Incorporate these words naturally when relevant")

        # Enfoque en crypto - más específico
        crypto_pct = vocab.get('crypto_focus', {}).get('percentage', 0)
        if crypto_pct > 20:
            prompt_parts.append(f"\n• TOPIC FOCUS: Heavy crypto/blockchain focus ({crypto_pct:.0f}%)")
            prompt_parts.append("• Use technical crypto terms confidently")
        elif crypto_pct > 5:
            prompt_parts.append(f"\n• TOPIC FOCUS: Moderate crypto coverage ({crypto_pct:.0f}%)")

        # Tono - muy específico y accionable
        prompt_parts.append(f"\n\n=== TONE & ATTITUDE ===")
        sentiment_ratio = tone.get('sentiment_ratio', 1)
        if sentiment_ratio > 3:
            prompt_parts.append("\n• SENTIMENT: Highly positive and optimistic")
            prompt_parts.append("• Frame news positively, focus on opportunities")
            prompt_parts.append("• Use bullish language, growth mindset")
        elif sentiment_ratio > 1.5:
            prompt_parts.append("\n• SENTIMENT: Generally positive with balanced perspective")
        elif sentiment_ratio < 0.5:
            prompt_parts.append("\n• SENTIMENT: Critical/skeptical voice")
            prompt_parts.append("• Question narratives, point out risks")
        else:
            prompt_parts.append("\n• SENTIMENT: Balanced, analytical tone")

        humor_pct = tone.get('humor_percentage', 0)
        if humor_pct > 15:
            prompt_parts.append(f"\n• HUMOR: Frequent use of humor/sarcasm ({humor_pct:.0f}%)")
            prompt_parts.append("• Don't be afraid to be witty or use wordplay")

        # Estructura - más específico
        prompt_parts.append(f"\n\n=== MESSAGE STRUCTURE ===")
        question_pct = structure.get('question_usage', {}).get('percentage', 0)
        if question_pct > 25:
            prompt_parts.append(f"\n• QUESTIONS: Use rhetorical questions frequently ({question_pct:.0f}%)")
            prompt_parts.append("• Engage readers with 'What if...?', 'Why...?', 'How...?'")
        elif question_pct > 10:
            prompt_parts.append(f"\n• QUESTIONS: Occasional questions to engage ({question_pct:.0f}%)")

        # NUEVO: Tipo de contenido - MUY ESPECÍFICO
        content_type = self.analysis.get('content_type', {})
        if content_type:
            prompt_parts.append(f"\n\n=== CONTENT TYPE & PURPOSE ===")
            # Build type distribution from the content_type data
            type_dist = {
                'informative': content_type.get('informative', {}).get('percentage', 0),
                'opinion': content_type.get('opinion', {}).get('percentage', 0),
                'prediction': content_type.get('prediction', {}).get('percentage', 0),
                'educational': content_type.get('educational', {}).get('percentage', 0),
                'analysis': content_type.get('analysis', {}).get('percentage', 0)
            }
            # Determine primary type (highest percentage)
            primary_type = max(type_dist.items(), key=lambda x: x[1])[0] if any(type_dist.values()) else 'unknown'

            if primary_type == 'informative':
                info_pct = type_dist.get('informative', 0)
                prompt_parts.append(f"\n• PRIMARY TYPE: Informative/News-focused ({info_pct:.0f}%)")
                prompt_parts.append("• Role: Share facts, report developments, announce news")
                prompt_parts.append("• Avoid: Heavy opinion, speculation, personal takes")
                prompt_parts.append("• Focus: What happened, key details, objective reporting")
            elif primary_type == 'opinion':
                opinion_pct = type_dist.get('opinion', 0)
                prompt_parts.append(f"\n• PRIMARY TYPE: Opinion/Commentary ({opinion_pct:.0f}%)")
                prompt_parts.append("• Role: Share perspective, personal takes, reactions")
                prompt_parts.append("• Use: 'I think', 'In my view', subjective language")
            elif primary_type == 'prediction':
                pred_pct = type_dist.get('prediction', 0)
                prompt_parts.append(f"\n• PRIMARY TYPE: Prediction/Forecasting ({pred_pct:.0f}%)")
                prompt_parts.append("• Role: Future outlook, price targets, trend analysis")
                prompt_parts.append("• Use: 'will', 'expect', 'likely', forward-looking language")
            elif primary_type == 'educational':
                edu_pct = type_dist.get('educational', 0)
                prompt_parts.append(f"\n• PRIMARY TYPE: Educational/Tutorial ({edu_pct:.0f}%)")
                prompt_parts.append("• Role: Teach, explain concepts, provide guides")
                prompt_parts.append("• Use: 'How to', step-by-step, explanatory language")
            elif primary_type == 'analysis':
                analysis_pct = type_dist.get('analysis', 0)
                prompt_parts.append(f"\n• PRIMARY TYPE: Deep Analysis ({analysis_pct:.0f}%)")
                prompt_parts.append("• Role: Break down events, explain causes, connect dots")
                prompt_parts.append("• Use: 'Because', 'factor', 'reason', analytical language")

        # NUEVO: Registro lingüístico - MUY ESPECÍFICO
        linguistic = self.analysis.get('linguistic_register', {})
        if linguistic:
            prompt_parts.append(f"\n\n=== LINGUISTIC REGISTER ===")
            register = linguistic.get('register', 'neutral')
            formality = linguistic.get('formality_ratio', 1.0)

            if register == 'formal':
                prompt_parts.append(f"\n• REGISTER: Formal/Professional (ratio: {formality:.2f})")
                prompt_parts.append("• Use: Technical terms, complete sentences, proper grammar")
                prompt_parts.append("• Avoid: Slang, contractions, casual expressions")
                formal_words = linguistic.get('formal_indicators', [])[:3]
                if formal_words:
                    prompt_parts.append(f"• Formal markers: {', '.join(formal_words)}")
            elif register == 'casual':
                prompt_parts.append(f"\n• REGISTER: Casual/Conversational (ratio: {formality:.2f})")
                prompt_parts.append("• Use: Contractions, relaxed grammar, conversational tone")
                prompt_parts.append("• Mix: Some technical terms with accessible language")
                casual_words = linguistic.get('casual_indicators', [])[:3]
                if casual_words:
                    prompt_parts.append(f"• Casual markers: {', '.join(casual_words)}")
            elif register == 'colloquial':
                prompt_parts.append(f"\n• REGISTER: Colloquial/Street (ratio: {formality:.2f})")
                prompt_parts.append("• Use: Slang, crypto-slang, internet speak")
                prompt_parts.append("• Examples: 'gm', 'wagmi', 'lfg', 'rekt', etc.")
                colloquial_words = linguistic.get('casual_indicators', [])[:5]
                if colloquial_words:
                    prompt_parts.append(f"• Common slang: {', '.join(colloquial_words)}")

            contraction_pct = linguistic.get('contraction_frequency', 0)
            if contraction_pct > 30:
                prompt_parts.append(f"\n• CONTRACTIONS: Heavy use ({contraction_pct:.0f}%) - don't, can't, it's, etc.")
            elif contraction_pct > 10:
                prompt_parts.append(f"\n• CONTRACTIONS: Moderate use ({contraction_pct:.0f}%)")
            else:
                prompt_parts.append(f"\n• CONTRACTIONS: Minimal/none ({contraction_pct:.0f}%) - write out fully")

        # NUEVO: Estilo narrativo - MUY ESPECÍFICO
        narrative = self.analysis.get('narrative_style', {})
        if narrative:
            prompt_parts.append(f"\n\n=== NARRATIVE PERSPECTIVE ===")
            dominant = narrative.get('dominant_style', 'third_person')
            first_pct = narrative.get('first_person_usage', {}).get('percentage', 0)
            second_pct = narrative.get('second_person_usage', {}).get('percentage', 0)

            if dominant == 'first_person':
                prompt_parts.append(f"\n• PERSPECTIVE: First Person - 'I', 'my', 'we' ({first_pct:.0f}%)")
                prompt_parts.append("• Share personal views, experiences, reactions")
                prompt_parts.append("• Example: 'I think Bitcoin will...', 'My take on...'")
            elif dominant == 'second_person':
                prompt_parts.append(f"\n• PERSPECTIVE: Second Person - 'you', imperatives ({second_pct:.0f}%)")
                prompt_parts.append("• Direct address to reader, give advice/commands")
                prompt_parts.append("• Example: 'You should watch...', 'Remember that...'")
            else:
                prompt_parts.append(f"\n• PERSPECTIVE: Third Person - objective, reporter style")
                prompt_parts.append("• Focus on events, markets, external actors")
                prompt_parts.append("• Example: 'Bitcoin reached...', 'The market shows...'")

        # NUEVO: Patrones de apertura - MUY ESPECÍFICO
        openings = self.analysis.get('opening_patterns', {})
        if openings:
            total = self.analysis.get('total_tweets', 1)
            patterns = openings.get('patterns', {})
            question_opens = patterns.get('question', {}).get('count', 0)
            number_opens = patterns.get('number', {}).get('count', 0)
            emoji_opens = patterns.get('emoji', {}).get('count', 0)
            exclamation_opens = patterns.get('exclamation', {}).get('count', 0)

            if total > 0:
                prompt_parts.append(f"\n\n=== OPENING STRATEGIES ===")

                if question_opens / total > 0.2:
                    prompt_parts.append(f"\n• QUESTIONS: Often starts with questions ({question_opens}/{total})")
                    prompt_parts.append("• Example: '¿Sabías que...?', 'What if...?', 'Why is...'")

                if number_opens / total > 0.15:
                    prompt_parts.append(f"\n• NUMBERS: Frequently opens with data ({number_opens}/{total})")
                    prompt_parts.append("• Example: '70% of...', '$50K...', '3 reasons...'")

                if emoji_opens / total > 0.2:
                    prompt_parts.append(f"\n• EMOJIS: Sometimes leads with emoji ({emoji_opens}/{total})")
                    prompt_parts.append("• Creates visual hook before text")

                if exclamation_opens / total > 0.15:
                    prompt_parts.append(f"\n• EXCLAMATIONS: Strong opening energy ({exclamation_opens}/{total})")
                    prompt_parts.append("• Example: '¡BREAKING!', '🚨 ALERT!', 'HUGE!'")

                common_first = openings.get('common_first_words', [])[:5]
                if common_first:
                    words = ', '.join([f"'{w}' ({c}x)" for w, c in common_first])
                    prompt_parts.append(f"\n• COMMON OPENERS: {words}")

        # NUEVO: Patrones de cierre - MUY ESPECÍFICO
        closings = self.analysis.get('closing_patterns', {})
        if closings:
            total = self.analysis.get('total_tweets', 1)
            patterns = closings.get('patterns', {})
            emoji_ends = patterns.get('emoji', {}).get('count', 0)
            question_ends = patterns.get('question', {}).get('count', 0)
            exclamation_ends = patterns.get('exclamation', {}).get('count', 0)
            ellipsis_ends = patterns.get('ellipsis', {}).get('count', 0)
            cta = patterns.get('call_to_action', {}).get('count', 0)

            if total > 0:
                prompt_parts.append(f"\n\n=== CLOSING STRATEGIES ===")

                if emoji_ends / total > 0.3:
                    prompt_parts.append(f"\n• EMOJI CLOSES: Frequently ends with emoji ({emoji_ends}/{total})")
                    prompt_parts.append("• Creates friendly, casual finish")

                if question_ends / total > 0.15:
                    prompt_parts.append(f"\n• QUESTION CLOSES: Often ends with question ({question_ends}/{total})")
                    prompt_parts.append("• Engages reader, prompts response")

                if exclamation_ends / total > 0.2:
                    prompt_parts.append(f"\n• EXCLAMATION CLOSES: Energetic endings ({exclamation_ends}/{total})")
                    prompt_parts.append("• Leaves reader with excitement")

                if ellipsis_ends / total > 0.1:
                    prompt_parts.append(f"\n• ELLIPSIS CLOSES: Trailing thought... ({ellipsis_ends}/{total})")
                    prompt_parts.append("• Creates suspense, continuation effect")

                if cta / total > 0.1:
                    prompt_parts.append(f"\n• CALL-TO-ACTION: Often prompts reader action ({cta}/{total})")
                    prompt_parts.append("• Example: 'Check it out', 'Read more', 'What do you think?'")

        # NUEVO: Uso de datos - MUY ESPECÍFICO
        data_usage = self.analysis.get('data_usage', {})
        if data_usage:
            prompt_parts.append(f"\n\n=== DATA & NUMBERS USAGE ===")

            number_freq_pct = data_usage.get('number_frequency', 0)
            percentage_pct = data_usage.get('percentage_usage', 0)
            price_pct = data_usage.get('price_mentions', 0)
            is_data_heavy = data_usage.get('data_heavy', False)

            if is_data_heavy:
                prompt_parts.append(f"\n• STYLE: Data-heavy, quantitative ({number_freq_pct:.0f}% of messages use numbers)")
                prompt_parts.append("• Back claims with stats, percentages, prices")
                prompt_parts.append("• Example: '$70K', '150% gain', '2.5M volume'")
            elif number_freq_pct > 30:
                prompt_parts.append(f"\n• STYLE: Moderate data use ({number_freq_pct:.0f}% use numbers)")
                prompt_parts.append("• Mix narrative with key figures")
            else:
                prompt_parts.append(f"\n• STYLE: Minimal data ({number_freq_pct:.0f}% use numbers)")
                prompt_parts.append("• Focus on narrative over numbers")

            if percentage_pct > 20:
                prompt_parts.append(f"\n• PERCENTAGES: Frequently uses % ({percentage_pct:.0f}%)")

            if price_pct > 30:
                prompt_parts.append(f"\n• PRICES: Often mentions prices/values ({price_pct:.0f}%)")

        # NUEVO: Patrones de oraciones - MUY ESPECÍFICO
        sentences = self.analysis.get('sentence_patterns', {})
        if sentences:
            prompt_parts.append(f"\n\n=== SENTENCE STRUCTURE ===")

            avg_words = sentences.get('avg_sentence_length_words', 0)
            complexity = sentences.get('simple_vs_complex_ratio', 1.0)

            if avg_words < 8:
                prompt_parts.append(f"\n• LENGTH: Very short, punchy sentences ({avg_words:.1f} words avg)")
                prompt_parts.append("• Style: Rapid-fire, tweet-optimized, high impact")
            elif avg_words < 12:
                prompt_parts.append(f"\n• LENGTH: Short to medium sentences ({avg_words:.1f} words avg)")
                prompt_parts.append("• Style: Concise but complete thoughts")
            else:
                prompt_parts.append(f"\n• LENGTH: Longer, detailed sentences ({avg_words:.1f} words avg)")
                prompt_parts.append("• Style: Explanatory, comprehensive coverage")

            if complexity > 2:
                prompt_parts.append(f"\n• COMPLEXITY: Mostly complex/compound sentences (ratio: {complexity:.1f})")
                prompt_parts.append("• Use clauses, conjunctions, detailed structure")
            elif complexity > 1:
                prompt_parts.append(f"\n• COMPLEXITY: Mix of simple and complex (ratio: {complexity:.1f})")
                prompt_parts.append("• Balance short punches with detailed explanations")
            else:
                prompt_parts.append(f"\n• COMPLEXITY: Mostly simple sentences (ratio: {complexity:.1f})")
                prompt_parts.append("• Direct, straightforward, easy to scan")

        # Ejemplos - mucho más detallado
        if examples:
            prompt_parts.append("\n\n=== ACTUAL WRITING EXAMPLES ===")
            prompt_parts.append("\nStudy these real examples to understand the exact voice and patterns:")
            for i, example in enumerate(examples[:4], 1):
                text = example.get('text', '')
                likes = example.get('likes', 0)
                prompt_parts.append(f"\n\nExample {i} ({likes} likes):")
                prompt_parts.append(f'"{text}"')
                # Analyze what makes this work
                if i == 1 and len(examples) > 0:
                    prompt_parts.append("\n→ Notice: Opening hook, word choice, punctuation rhythm")

        # Instrucciones finales - MUCHO MÁS ESPECÍFICAS
        prompt_parts.append("\n\n=== CRITICAL INSTRUCTIONS ===")
        prompt_parts.append("\n1. MATCH THE EXACT VOICE: Write as if you ARE @" + self.username)
        prompt_parts.append("\n2. LANGUAGE: Write in the SAME language as the source content (English articles → English output)")
        prompt_parts.append("\n3. AUTHENTICITY: Sound natural, not like you're copying - internalize the patterns")
        prompt_parts.append("\n4. SPECIFIC PATTERNS:")
        prompt_parts.append("   - Match sentence length distribution")
        prompt_parts.append("   - Use similar opening strategies")
        prompt_parts.append("   - Mirror punctuation intensity")
        prompt_parts.append("   - Incorporate characteristic vocabulary")
        prompt_parts.append("\n5. DON'T: Generic crypto bro talk - be SPECIFIC to this person's voice")

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
        # Detectar idioma del source text
        detected_lang = self._detect_language(source_text)

        # Construir prompt con idioma específico
        style_prompt = self.build_style_prompt(target_language=detected_lang)

        # User prompt más específico sobre el idioma
        lang_reminder = "IN ENGLISH" if detected_lang == 'english' else "EN ESPAÑOL"

        user_prompt = f"""Based on the style guide above, rewrite this {content_type} content {lang_reminder}:

ORIGINAL CONTENT:
{source_text}

YOUR REWRITE (matching @{self.username}'s voice, {lang_reminder}):"""

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

        # Crear resumen del artículo (inglés o español)
        source_text = f"Title: {title}\n\nContent: {content[:800]}"

        # Generar contenido en diferentes formatos
        # Tweet: corto, punchy, con hook
        tweet_prompt = f"{source_text}\n\nCreate a standalone tweet announcing this news (max 280 chars)."

        # Thread: primer tweet de un hilo, debe enganchar
        thread_prompt = f"{source_text}\n\nCreate the opening tweet of a thread about this (max 280 chars, should hook readers)."

        # Article intro: más detallado
        article_prompt = f"{source_text}\n\nWrite a brief intro paragraph summarizing this news."

        result = {
            'original_title': title,
            'original_url': url,
            'tweet': self.generate_content(tweet_prompt, content_type="tweet", max_tokens=150),
            'thread_intro': self.generate_content(thread_prompt, content_type="thread intro", max_tokens=150),
            'article_intro': self.generate_content(article_prompt, content_type="article intro", max_tokens=300)
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
