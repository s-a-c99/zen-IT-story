"""
Story Generator - Gemini API Integration
Generates bedtime astronomy stories with haiku using Google's Gemini API
"""

import google.generativeai as genai
import os
import logging
import re
import syllables
from typing import Dict, Tuple, Optional, List
from src import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set! Story generation will fail.")


def generate_story(
    object_name: str,
    object_type: str,
    location: str,
    scientific_facts: str,
    language: str = "en"
) -> Dict[str, str]:
    """
    Generate a bedtime astronomy story using Gemini API.

    Args:
        object_name: Name of celestial object (e.g., "Jupiter", "Altair")
        object_type: Type of object ("planet", "star", "constellation")
        location: User's location (city name)
        scientific_facts: Scientific facts about the object
        language: Target language code ("en", "it", "fr", "es")

    Returns:
        Dict with keys:
            - title: Story title
            - story: Full story text (3 acts)
            - haiku: Extracted haiku (3 lines)
            - haiku_title: Title for haiku section
            - full_text: Complete formatted output
            - success: Boolean indicating if generation succeeded
            - error: Error message if failed
    """
    logger.info(f"Generating story: {object_name} ({object_type}) in {language}")

    # Validate language
    if language not in config.SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language {language}, defaulting to 'en'")
        language = "en"

    # Build the prompt using config template
    prompt = config.STORY_PROMPT_TEMPLATE.format(
        object_name=object_name,
        object_type=object_type,
        location=location,
        scientific_facts=scientific_facts,
        language=config.SUPPORTED_LANGUAGES[language]
    )

    try:
        # Initialize Gemini model
        model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            safety_settings=config.GEMINI_SAFETY_SETTINGS
        )

        # Generate story
        response = model.generate_content(prompt)

        if not response.text:
            raise ValueError("Empty response from Gemini API")

        story_text = response.text

        # Parse and validate the story
        parsed = parse_story(story_text, language)

        if not parsed["success"]:
            logger.warning(f"Story parsing failed: {parsed['error']}")
            # Still return the raw story even if parsing failed
            return {
                "title": f"The Tale of {object_name}",
                "story": story_text,
                "haiku": "",
                "haiku_title": "",
                "full_text": story_text,
                "success": True,
                "error": None
            }

        # Validate haiku (if present)
        if parsed["haiku"]:
            haiku_valid = validate_haiku(parsed["haiku"], language)
            if not haiku_valid:
                logger.warning(f"Haiku validation failed for language {language}")

        # Apply safety filter
        if not safety_filter(parsed["full_text"]):
            logger.error("Story contains unsafe content! Returning fallback.")
            return get_fallback_story(object_name, language)

        logger.info(f"Story generated successfully ({len(story_text)} chars)")
        return parsed

    except Exception as e:
        logger.error(f"Story generation failed: {e}")
        # Log detailed error but return graceful fallback
        logger.debug(f"Full exception: {str(e)}", exc_info=True)
        return get_fallback_story(object_name, language)


def parse_story(story_text: str, language: str) -> Dict[str, str]:
    """
    Parse story text to extract title, acts, and haiku.

    Returns:
        Dict with parsed components or error information
    """
    try:
        # Extract title (first markdown heading)
        title_match = re.search(r'^#\s+(.+)$', story_text, re.MULTILINE)
        title = title_match.group(1) if title_match else f"A Celestial Tale"

        # Extract haiku section - improved pattern to handle various formats
        # Try multiple patterns for flexibility
        haiku_title = ""
        haiku = ""

        # Pattern 1: Three lines after "Haiku" heading
        haiku_pattern1 = r'###?\s+(.+?[Hh]aiku.*?)\s*\n\s*(.+?)\s*\n\s*(.+?)\s*\n\s*(.+?)(?:\s*\n\n|\s*$)'
        haiku_match = re.search(haiku_pattern1, story_text, re.DOTALL)

        if haiku_match:
            haiku_title = haiku_match.group(1).strip()
            haiku = f"{haiku_match.group(2).strip()}\n{haiku_match.group(3).strip()}\n{haiku_match.group(4).strip()}"
        else:
            # Pattern 2: Haiku all on one line (Gemini sometimes does this)
            haiku_pattern2 = r'###?\s+(.+?[Hh]aiku.*?)\s*\n\s*(.+?)(?:\s*\n\n|\s*$)'
            haiku_match = re.search(haiku_pattern2, story_text, re.DOTALL)

            if haiku_match:
                haiku_title = haiku_match.group(1).strip()
                haiku_text = haiku_match.group(2).strip()

                # Try to split by common delimiters
                if '/' in haiku_text:
                    haiku_lines = [line.strip() for line in haiku_text.split('/')]
                elif ',' in haiku_text and haiku_text.count(',') >= 2:
                    # Split by commas but keep last part together
                    parts = haiku_text.split(',')
                    if len(parts) >= 3:
                        haiku_lines = [parts[0].strip(), parts[1].strip(), ','.join(parts[2:]).strip()]
                    else:
                        haiku_lines = [p.strip() for p in parts]
                else:
                    # Assume it's already formatted with line breaks
                    haiku_lines = [line.strip() for line in haiku_text.split('\n') if line.strip()]

                if len(haiku_lines) >= 3:
                    haiku = '\n'.join(haiku_lines[:3])
                else:
                    haiku = haiku_text

        # Remove title and haiku to get just the story
        story = story_text
        if title_match:
            story = story.replace(title_match.group(0), "", 1)
        if haiku_match:
            story = story.replace(haiku_match.group(0), "")

        story = story.strip()

        return {
            "title": title,
            "story": story,
            "haiku": haiku,
            "haiku_title": haiku_title,
            "full_text": story_text,
            "success": True,
            "error": None
        }

    except Exception as e:
        return {
            "title": "",
            "story": story_text,
            "haiku": "",
            "haiku_title": "",
            "full_text": story_text,
            "success": False,
            "error": str(e)
        }


def validate_haiku(haiku: str, language: str) -> bool:
    """
    Validate haiku structure based on language rules.

    Args:
        haiku: Three-line haiku text
        language: Language code

    Returns:
        Boolean indicating if haiku is valid
    """
    try:
        lines = [line.strip() for line in haiku.split('\n') if line.strip()]

        if len(lines) != 3:
            logger.warning(f"Haiku must have 3 lines, got {len(lines)}")
            return False

        # Get syllable rules for language
        rules = config.HAIKU_SYLLABLE_RULES.get(language, config.HAIKU_SYLLABLE_RULES["en"])

        # Count syllables for each line
        for i, line in enumerate(lines):
            line_num = f"line{i+1}"
            min_syl, max_syl = rules[line_num]

            # Count syllables (works best for English)
            try:
                syl_count = syllables.estimate(line)
                if not (min_syl <= syl_count <= max_syl):
                    logger.warning(f"Haiku line {i+1}: {syl_count} syllables (expected {min_syl}-{max_syl})")
                    # Don't fail, just warn - syllable counting isn't perfect for all languages
            except Exception as e:
                logger.warning(f"Syllable counting failed: {e}")

        return True

    except Exception as e:
        logger.warning(f"Haiku validation error: {e}")
        return False


def safety_filter(text: str) -> bool:
    """
    Check if story text contains unsafe words.

    Returns:
        True if safe, False if contains unsafe content
    """
    text_lower = text.lower()

    # Use word boundaries to avoid false positives
    # (e.g., "hell" should not match "hello" or "shell")
    for unsafe_word in config.UNSAFE_WORDS:
        # Create pattern with word boundaries \b
        pattern = r'\b' + re.escape(unsafe_word) + r'\b'
        if re.search(pattern, text_lower):
            logger.warning(f"Unsafe word detected: {unsafe_word}")
            return False

    return True


def get_fallback_story(object_name: str, language: str) -> Dict[str, str]:
    """
    Return a pre-written fallback story if generation fails.

    Args:
        object_name: Name of celestial object
        language: Language code

    Returns:
        Dict with fallback story components
    """
    logger.info(f"Using fallback story for {object_name} in {language}")

    # Multilingual fallback stories
    fallback_stories = {
        "en": {
            "title": f"The Tale of {object_name}",
            "story": f"""Once upon a time, in the vast cosmic ocean of stars, there lived a special celestial friend named {object_name}.

Every night, {object_name} would light up the dark sky, waiting for children just like you to look up and notice its gentle glow. It loved to watch over the world below, keeping everyone safe as they dreamed.

{object_name} had many friends in the sky - other stars, planets, and even the Moon would come to visit. Together, they would paint beautiful patterns across the night, creating a magical show just for you.

Tonight, as you close your eyes, remember that {object_name} is up there, shining brightly and watching over you. It will be there tomorrow night, and the night after that, always ready to be your friend in the sky.""",
            "haiku": "Stars shine above—\nquiet wonder fills the night,\ndreams take gentle flight.",
            "haiku_title": "Goodnight Haiku"
        },
        "it": {
            "title": f"La Storia di {object_name}",
            "story": f"""C'era una volta, nel vasto oceano cosmico di stelle, un amico celeste speciale di nome {object_name}.

Ogni notte, {object_name} illuminava il cielo buio, aspettando che bambini come te alzassero gli occhi per notare il suo dolce bagliore. Amava vegliare sul mondo qui sotto, proteggendo tutti mentre sognavano.

{object_name} aveva tanti amici nel cielo - altre stelle, pianeti, e persino la Luna venivano a fargli visita. Insieme, dipingevano bellissimi disegni nel cielo notturno, creando uno spettacolo magico solo per te.

Stanotte, mentre chiudi gli occhi, ricorda che {object_name} è lassù, che brilla intensamente e veglia su di te. Sarà lì domani notte, e la notte dopo, sempre pronto a essere il tuo amico nel cielo.""",
            "haiku": "Stelle brillano—\nmeraviglia silenziosa,\nsogni volano via.",
            "haiku_title": "Haiku della Buonanotte"
        },
        "fr": {
            "title": f"L'Histoire de {object_name}",
            "story": f"""Il était une fois, dans le vaste océan cosmique d'étoiles, un ami céleste spécial nommé {object_name}.

Chaque nuit, {object_name} illuminait le ciel sombre, attendant que des enfants comme toi lèvent les yeux pour remarquer sa douce lueur. Il aimait veiller sur le monde en bas, gardant tout le monde en sécurité pendant leurs rêves.

{object_name} avait beaucoup d'amis dans le ciel - d'autres étoiles, des planètes, et même la Lune venaient lui rendre visite. Ensemble, ils peignaient de magnifiques motifs à travers la nuit, créant un spectacle magique rien que pour toi.

Ce soir, en fermant les yeux, souviens-toi que {object_name} est là-haut, brillant intensément et veillant sur toi. Il sera là demain soir, et le soir d'après, toujours prêt à être ton ami dans le ciel.""",
            "haiku": "Les étoiles brillent—\nsilencieuse merveille,\nrêves prennent vol.",
            "haiku_title": "Haïku de Bonne Nuit"
        },
        "es": {
            "title": f"El Cuento de {object_name}",
            "story": f"""Había una vez, en el vasto océano cósmico de estrellas, un amigo celestial especial llamado {object_name}.

Cada noche, {object_name} iluminaba el cielo oscuro, esperando que niños como tú miraran hacia arriba para notar su suave resplandor. Le encantaba cuidar del mundo de abajo, manteniendo a todos seguros mientras soñaban.

{object_name} tenía muchos amigos en el cielo - otras estrellas, planetas, e incluso la Luna venían a visitarlo. Juntos, pintaban hermosos patrones en el cielo nocturno, creando un espectáculo mágico solo para ti.

Esta noche, al cerrar los ojos, recuerda que {object_name} está allá arriba, brillando intensamente y cuidándote. Estará allí mañana por la noche, y la noche siguiente, siempre listo para ser tu amigo en el cielo.""",
            "haiku": "Estrellas brillan—\nmaravilla silenciosa,\nsueños alzan vuelo.",
            "haiku_title": "Haiku de Buenas Noches"
        }
    }

    # Get fallback for language, default to English
    fallback = fallback_stories.get(language, fallback_stories["en"])

    return {
        "title": fallback["title"],
        "story": fallback["story"],
        "haiku": fallback["haiku"],
        "haiku_title": fallback["haiku_title"],
        "full_text": f"# {fallback['title']}\n\n{fallback['story']}\n\n### {fallback['haiku_title']}\n\n{fallback['haiku']}",
        "success": True,
        "error": None
    }


def format_story_for_display(story_dict: Dict[str, str], language: str = "en") -> str:
    """
    Format parsed story for beautiful display in Gradio UI as HTML.

    Args:
        story_dict: Parsed story dictionary
        language: Language code

    Returns:
        HTML-formatted story text
    """
    # Convert story to HTML
    title_html = f"<h1 style='color: #fbbf24; font-size: 2.5em; margin-bottom: 20px;'>{story_dict['title']}</h1>\n\n"

    # If haiku wasn't parsed but exists in story text, extract it here
    story_text = story_dict['story']
    haiku_title = story_dict.get('haiku_title', '')
    haiku = story_dict.get('haiku', '')

    if not haiku:
        # Try to extract haiku from story text as fallback
        haiku_pattern = r'###?\s*(.+?[Hh]aiku.*?)\s*\n\s*(.+?)(?:\n\n|$)'
        haiku_match = re.search(haiku_pattern, story_text, re.DOTALL)

        if haiku_match:
            haiku_title = haiku_match.group(1).strip()
            haiku_content = haiku_match.group(2).strip()

            # Split into lines
            haiku_lines = [line.strip() for line in haiku_content.split('\n') if line.strip()]
            if len(haiku_lines) >= 3:
                haiku = '\n'.join(haiku_lines[:3])
            else:
                haiku = haiku_content

            # Remove haiku from story text
            story_text = story_text.replace(haiku_match.group(0), '').strip()

    # Convert story paragraphs to HTML
    story_paragraphs = story_text.split('\n\n')
    story_html = ""
    for para in story_paragraphs:
        if para.strip() and not para.strip().startswith('#'):  # Skip any remaining headers
            story_html += f"<p style='font-size: 1.1em; line-height: 1.8; margin-bottom: 16px; color: #e2e8f0;'>{para.strip()}</p>\n\n"

    # Format haiku in a beautiful colored box
    haiku_html = ""
    if haiku:
        if not haiku_title:
            haiku_title = "Goodnight Haiku"

        haiku_lines = haiku.split('\n')

        # Create elegant haiku box with gradient background
        haiku_html = f"""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px; margin: 30px 0; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
    <h3 style='color: #fbbf24; margin-bottom: 16px; font-size: 1.3em;'>🌸 {haiku_title}</h3>
    <div style='color: white; font-style: italic; font-size: 1.1em; line-height: 1.8;'>
"""
        for line in haiku_lines:
            if line.strip():
                haiku_html += f"        <p style='margin: 8px 0;'>{line.strip()}</p>\n"

        haiku_html += """    </div>
</div>
"""

    return title_html + story_html + haiku_html


def format_story_for_sharing(story_dict: Dict[str, str], object_name: str, location: str) -> str:
    """
    Format story for social media sharing.

    Args:
        story_dict: Parsed story dictionary
        object_name: Name of celestial object
        location: User's location

    Returns:
        Formatted text for sharing
    """
    share_text = f"🌌 {story_dict['title']}\n\n"

    # Include first paragraph only
    story_preview = story_dict['story'][:200] + "..."

    share_text += f"{story_preview}\n\n"

    if story_dict['haiku']:
        share_text += f"✨ Haiku:\n{story_dict['haiku']}\n\n"

    share_text += f"📍 Seen from: {location}\n"
    share_text += f"⭐ Tonight's star: {object_name}\n\n"
    share_text += "🌟 Generated by Zen-IT-Story\n"
    share_text += "#astronomy #bedtimestories #AI"

    return share_text


def generate_fun_facts(
    object_name: str,
    object_type: str,
    language: str = "en"
) -> List[str]:
    """
    Generate 3 child-friendly "Did You Know?" facts about a celestial object.

    Args:
        object_name: Name of celestial object (e.g., "Jupiter", "Mars")
        object_type: Type of object ("planet", "star", "constellation")
        language: Target language code ("en", "it", "fr", "es")

    Returns:
        List of 3 fun facts in the selected language
    """
    logger.info(f"Generating fun facts for {object_name} in {language}")

    # Facts database - organized by object and language
    facts_db = {
        "Jupiter": {
            "en": [
                "Jupiter is SO big that 1,300 Earths could fit inside it! It's like a giant cosmic playground.",
                "Jupiter has a storm called the Great Red Spot that has been raging for over 400 years!",
                "Jupiter spins super fast - a day on Jupiter is only 10 hours long, even though it's huge!"
            ],
            "it": [
                "Giove è così grande che dentro potrebbe stare 1.300 volte la Terra! È come un immenso parco giochi cosmico.",
                "Giove ha una tempesta chiamata la Grande Macchia Rossa che infuria da oltre 400 anni!",
                "Giove gira velocissimo - un giorno su Giove dura solo 10 ore, anche se è gigantesco!"
            ],
            "fr": [
                "Jupiter est si grande que 1 300 Terres pourraient y tenir! C'est comme une immense cour de récréation cosmique.",
                "Jupiter a une tempête appelée la Grande Tache Rouge qui fait rage depuis plus de 400 ans!",
                "Jupiter tourne très vite - une journée sur Jupiter ne dure que 10 heures, même si elle est énorme!"
            ],
            "es": [
                "¡Júpiter es tan grande que dentro cabrían 1.300 Tierras! Es como un gigantesco patio de juegos cósmico.",
                "¡Júpiter tiene una tormenta llamada la Gran Mancha Roja que ha estado rugiendo durante más de 400 años!",
                "¡Júpiter gira muy rápido - un día en Júpiter dura solo 10 horas, aunque sea gigantesco!"
            ]
        },
        "Mars": {
            "en": [
                "Mars is called the Red Planet because its soil is covered in rusty iron! It looks like a giant red ball in the sky.",
                "Mars has the biggest volcano in our whole solar system - it's called Olympus Mons!",
                "A year on Mars is almost twice as long as a year on Earth - imagine waiting that long for your birthday!"
            ],
            "it": [
                "Marte si chiama il Pianeta Rosso perché il suo terreno è coperto di ferro arrugginito! Sembra una gigantesca palla rossa nel cielo.",
                "Marte ha il vulcano più grande di tutto il nostro sistema solare - si chiama Olympus Mons!",
                "Un anno su Marte è quasi il doppio di un anno sulla Terra - immagina aspettare così a lungo il tuo compleanno!"
            ],
            "fr": [
                "Mars s'appelle la Planète Rouge parce que son sol est couvert de fer rouillé! Elle ressemble à une gigantesque boule rouge dans le ciel.",
                "Mars a le plus grand volcan de tout notre système solaire - il s'appelle Olympus Mons!",
                "Une année sur Mars est presque deux fois plus longue qu'une année sur Terre - imagine d'attendre si longtemps ton anniversaire!"
            ],
            "es": [
                "¡Marte se llama el Planeta Rojo porque su suelo está cubierto de hierro oxidado! Se ve como una gigantesca bola roja en el cielo.",
                "¡Marte tiene el volcán más grande de todo nuestro sistema solar - se llama Olympus Mons!",
                "¡Un año en Marte es casi el doble de un año en la Tierra - imagina esperar tanto tiempo para tu cumpleaños!"
            ]
        },
        "Saturn": {
            "en": [
                "Saturn has beautiful rings made of billions of pieces of ice and rock! They sparkle like a cosmic necklace.",
                "Saturn is so light that it would float in water if you could find a bathtub big enough!",
                "Saturn has 82 moons orbiting around it - that's like having 82 little friends spinning in space!"
            ],
            "it": [
                "Saturno ha bellissimi anelli fatti di miliardi di pezzi di ghiaccio e roccia! Brillano come una collana cosmica.",
                "Saturno è così leggero che galleggerebbe nell'acqua se potessi trovare una vasca abbastanza grande!",
                "Saturno ha 82 lune che gli orbitano intorno - è come avere 82 piccoli amici che girano nello spazio!"
            ],
            "fr": [
                "Saturne a de beaux anneaux faits de milliards de morceaux de glace et de roche! Ils brillent comme un collier cosmique.",
                "Saturne est si légère qu'elle flotterait dans l'eau si vous pouviez trouver une baignoire assez grande!",
                "Saturne a 82 lunes qui tournent autour d'elle - c'est comme avoir 82 petits amis qui tournoient dans l'espace!"
            ],
            "es": [
                "¡Saturno tiene hermosos anillos hechos de miles de millones de piezas de hielo y roca! Brillan como un collar cósmico.",
                "¡Saturno es tan ligero que flotaría en el agua si pudieras encontrar una bañera lo suficientemente grande!",
                "¡Saturno tiene 82 lunas orbitando alrededor - es como tener 82 pequeños amigos girando en el espacio!"
            ]
        },
        "Venus": {
            "en": [
                "Venus is the hottest planet in our solar system - hotter than Mercury, even though it's farther from the Sun!",
                "Venus shines so brightly that sometimes you can see it in the daytime! It's called the Morning or Evening Star.",
                "A day on Venus is longer than a year on Venus - time works in a very strange way there!"
            ],
            "it": [
                "Venere è il pianeta più caldo del nostro sistema solare - più caldo di Mercurio, anche se è più lontano dal Sole!",
                "Venere brilla così tanto che a volte puoi vederla durante il giorno! Si chiama la Stella del Mattino o della Sera.",
                "Un giorno su Venere è più lungo di un anno su Venere - il tempo funziona in modo molto strano lì!"
            ],
            "fr": [
                "Vénus est la planète la plus chaude de notre système solaire - plus chaude que Mercure, même si elle est plus loin du Soleil!",
                "Vénus brille si intensément que parfois on peut la voir pendant la journée! On l'appelle l'Étoile du Matin ou du Soir.",
                "Un jour sur Vénus est plus long qu'une année sur Vénus - le temps fonctionne de façon très étrange là-bas!"
            ],
            "es": [
                "¡Venus es el planeta más caliente de nuestro sistema solar - más caliente que Mercurio, aunque esté más lejos del Sol!",
                "¡Venus brilla tan intensamente que a veces puedes verla durante el día! Se llama la Estrella de la Mañana o de la Tarde.",
                "¡Un día en Venus es más largo que un año en Venus - ¡el tiempo funciona de manera muy extraña allí!"
            ]
        },
        "Mercury": {
            "en": [
                "Mercury is the closest planet to the Sun and also the fastest - it zooms around the Sun like a cosmic speedster!",
                "Mercury has no atmosphere, so there's nothing to protect it from space rocks - it's all covered in craters!",
                "Mercury is tiny - you could fit it inside the Sun over 6 million times!"
            ],
            "it": [
                "Mercurio è il pianeta più vicino al Sole ed è anche il più veloce - gira intorno al Sole come un corridore cosmico!",
                "Mercurio non ha atmosfera, quindi non c'è niente a proteggerlo dalle rocce spaziali - è tutto coperto di crateri!",
                "Mercurio è minuscolo - potresti far stare il Sole dentro di esso oltre 6 milioni di volte!"
            ],
            "fr": [
                "Mercure est la planète la plus proche du Soleil et aussi la plus rapide - elle fonce autour du Soleil comme un coureur cosmique!",
                "Mercure n'a pas d'atmosphère, donc rien ne la protège des roches spatiales - elle est entièrement couverte de cratères!",
                "Mercure est minuscule - vous pourriez faire tenir le Soleil à l'intérieur plus de 6 millions de fois!"
            ],
            "es": [
                "¡Mercurio es el planeta más cercano al Sol y también el más rápido - ¡se dispara alrededor del Sol como un velocista cósmico!",
                "¡Mercurio no tiene atmósfera, así que nada lo protege de las rocas espaciales - ¡está completamente cubierto de cráteres!",
                "¡Mercurio es diminuto - ¡podrías meter el Sol dentro más de 6 millones de veces!"
            ]
        },
        "default": {
            "en": [
                "Every star you see at night is actually a sun, just like ours! Some are much bigger and brighter.",
                "The light from distant stars takes many years to reach your eyes - you're looking at the past when you see them!",
                "Our universe is so big that we've only discovered a tiny fraction of all the stars and planets that exist!"
            ],
            "it": [
                "Ogni stella che vedi di notte è in realtà un sole, proprio come il nostro! Alcuni sono molto più grandi e luminosi.",
                "La luce dalle stelle lontane impiega molti anni per raggiungere i tuoi occhi - stai guardando il passato quando le vedi!",
                "L'universo è così grande che abbiamo scoperto solo una piccola frazione di tutte le stelle e i pianeti che esistono!"
            ],
            "fr": [
                "Chaque étoile que vous voyez la nuit est en fait un soleil, comme le nôtre! Certains sont beaucoup plus grands et plus brillants.",
                "La lumière des étoiles lointaines prend de nombreuses années pour atteindre vos yeux - vous regardez le passé quand vous les voyez!",
                "Notre univers est si grand que nous n'avons découvert qu'une infime partie de toutes les étoiles et planètes qui existent!"
            ],
            "es": [
                "¡Cada estrella que ves de noche es en realidad un sol, como el nuestro! Algunos son mucho más grandes y brillantes.",
                "¡La luz de las estrellas lejanas tarda muchos años en llegar a tus ojos - ¡estás mirando el pasado cuando las ves!",
                "¡Nuestro universo es tan grande que solo hemos descubierto una pequeña fracción de todas las estrellas y planetas que existen!"
            ]
        }
    }

    # Get facts for the object, fallback to default
    normalized_name = object_name.capitalize()
    object_facts = facts_db.get(normalized_name, facts_db["default"])

    # Get language-specific facts, fallback to English
    lang_facts = object_facts.get(language, object_facts.get("en", facts_db["default"]["en"]))

    # Return 3 facts
    return lang_facts[:3]


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_story_generation():
    """Test story generation with sample data"""
    print("\n" + "="*80)
    print("Testing Story Generator")
    print("="*80 + "\n")

    test_cases = [
        ("Jupiter", "planet", "Rome, Italy", "The largest planet in our solar system", "en"),
        ("Altair", "star", "Paris, France", "A bright star in the summer sky", "fr"),
        ("Mars", "planet", "Madrid, Spain", "The red planet", "es"),
        ("Vega", "star", "Milano, Italy", "A blue-white star", "it"),
    ]

    for object_name, obj_type, location, facts, lang in test_cases:
        print(f"\nTesting: {object_name} in {lang}")
        print("-" * 40)

        story = generate_story(object_name, obj_type, location, facts, lang)

        if story["success"]:
            print(f"✓ Success! Title: {story['title']}")
            print(f"  Story length: {len(story['story'])} chars")
            print(f"  Haiku present: {'Yes' if story['haiku'] else 'No'}")
        else:
            print(f"✗ Failed: {story['error']}")


if __name__ == "__main__":
    # Validate config
    config.validate_config()

    # Run tests
    test_story_generation()
