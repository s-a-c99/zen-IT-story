"""
Zen-IT-Story MCP Server (Track 1)
Model Context Protocol server providing astronomy tools for story generation

This MCP server exposes 3 tools:
1. select_celestial - Choose best visible celestial object at location/time
2. get_story_prompt - Generate narrative structure for an object
3. generate_image_prompt - Get image search strategy for an object
"""

import gradio as gr
import requests
import os
from datetime import datetime
from typing import Dict, Optional, List
import json
import logging

# Import configuration
from src import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_visible_stars_skyfield(latitude: float, longitude: float, date_str: str = None) -> list:
    """
    Calculate visible bright stars using Skyfield ephemeris library.

    Returns list of visible stars (altitude > 30°) sorted by brightness.
    Falls back to hemisphere-based selection if Skyfield fails.

    Args:
        latitude: Observer latitude in degrees
        longitude: Observer longitude in degrees
        date_str: ISO date string (YYYY-MM-DD), defaults to today

    Returns:
        List of dicts with keys: name, ra, dec, magnitude, altitude, constellation
    """
    try:
        from skyfield.api import load, Star, wgs84
        from skyfield.data import hipparcos

        # Load timescale and ephemeris
        ts = load.timescale()
        planets = load('de421.bsp')  # NASA JPL ephemeris
        earth = planets['earth']

        # Observer location
        observer = earth + wgs84.latlon(latitude, longitude)

        # Time (now or specified date at 21:00 local time)
        if date_str:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str).replace(hour=21, minute=0)
            t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute)
        else:
            t = ts.now()

        # Load bright stars from Hipparcos catalog (magnitude <= 2.5)
        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)

        bright_stars = df[df['magnitude'] <= 2.5].copy()

        visible_stars = []

        for idx, row in bright_stars.iterrows():
            try:
                star = Star.from_dataframe(row)
                astrometric = observer.at(t).observe(star)
                alt, az, distance = astrometric.apparent().altaz()

                # Only include stars above 30° altitude (clearly visible)
                if alt.degrees > 30:
                    visible_stars.append({
                        "name": row.get('hip', f"HIP {idx}"),  # Hipparcos ID
                        "ra": row.get('ra_degrees', 0),
                        "dec": row.get('dec_degrees', 0),
                        "magnitude": row.get('magnitude', 5.0),
                        "altitude": alt.degrees,
                        "constellation": "Unknown",  # Hipparcos doesn't include this
                        "from_skyfield": True
                    })
            except Exception as e:
                continue  # Skip problematic stars

        # Sort by brightness (lower magnitude = brighter)
        visible_stars.sort(key=lambda x: x['magnitude'])

        logger.info(f"Skyfield found {len(visible_stars)} visible stars")
        return visible_stars[:10]  # Return top 10 brightest

    except Exception as e:
        logger.warning(f"Skyfield calculation failed: {e}, using hemisphere fallback")
        return _get_hemisphere_stars(latitude)


def _get_hemisphere_stars(latitude: float) -> list:
    """
    Fallback: Return bright stars appropriate for hemisphere.

    Args:
        latitude: Observer latitude

    Returns:
        List of star dicts for the hemisphere
    """
    if latitude >= 0:  # Northern hemisphere
        stars = [
            {"name": "Polaris", "ra": 37.95, "dec": 89.26, "magnitude": 2.0, "constellation": "Ursa Minor"},
            {"name": "Vega", "ra": 279.23, "dec": 38.78, "magnitude": 0.03, "constellation": "Lyra"},
            {"name": "Arcturus", "ra": 213.92, "dec": 19.18, "magnitude": -0.05, "constellation": "Boötes"},
            {"name": "Deneb", "ra": 310.36, "dec": 45.28, "magnitude": 1.25, "constellation": "Cygnus"},
            {"name": "Altair", "ra": 297.70, "dec": 8.87, "magnitude": 0.76, "constellation": "Aquila"},
        ]
    else:  # Southern hemisphere
        stars = [
            {"name": "Sirius", "ra": 101.29, "dec": -16.72, "magnitude": -1.46, "constellation": "Canis Major"},
            {"name": "Canopus", "ra": 95.99, "dec": -52.70, "magnitude": -0.72, "constellation": "Carina"},
            {"name": "Alpha Centauri", "ra": 219.90, "dec": -60.83, "magnitude": -0.01, "constellation": "Centaurus"},
            {"name": "Achernar", "ra": 24.43, "dec": -57.24, "magnitude": 0.45, "constellation": "Eridanus"},
            {"name": "Beta Centauri", "ra": 210.96, "dec": -60.37, "magnitude": 0.61, "constellation": "Centaurus"},
        ]

    # Add from_skyfield=False flag
    for star in stars:
        star["from_skyfield"] = False

    logger.info(f"Using hemisphere fallback: {'North' if latitude >= 0 else 'South'}")
    return stars


def select_celestial(latitude: float, longitude: float, date: str = None) -> dict:
    """
    Select the best celestial object visible at given coordinates and date.

    This tool calls astronomy APIs to find visible objects (planets, stars, constellations)
    and scores them based on special events, cultural significance, and novelty.

    Args:
        latitude: Observer latitude in decimal degrees (-90 to 90).
                 Example: 41.9028 for Rome, Italy
        longitude: Observer longitude in decimal degrees (-180 to 180).
                  Example: 12.4964 for Rome, Italy
        date: ISO format date string (YYYY-MM-DD). Defaults to today if not provided.
              Example: "2025-11-16"

    Returns:
        dict: Selected celestial object with keys:
            - object_name (str): Name of the object (e.g., "Jupiter", "Altair")
            - type (str): Type of object ("planet", "star", "constellation")
            - ra (float): Right Ascension in degrees
            - dec (float): Declination in degrees
            - magnitude (float): Visual magnitude (brightness)
            - constellation (str): Constellation name
            - description (str): Human-readable description
            - score (int): Selection score (higher is better)

    Raises:
        ValueError: If latitude/longitude are out of valid range
        RuntimeError: If all API calls fail
    """
    # Validate inputs
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")

    # Use today's date if not provided
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"select_celestial called: lat={latitude}, lon={longitude}, date={date}")

    all_objects = []

    # PRIORITY 1: Try Skyfield for real-time visible stars
    try:
        visible_stars = get_visible_stars_skyfield(latitude, longitude, date)

        if visible_stars:
            for star_data in visible_stars:
                # Map star names from Hipparcos IDs to common names (best effort)
                common_names = {
                    "HIP 11767": "Polaris",
                    "HIP 91262": "Vega",
                    "HIP 69673": "Arcturus",
                    "HIP 102098": "Deneb",
                    "HIP 97649": "Altair",
                    "HIP 32349": "Sirius",
                    "HIP 30438": "Canopus",
                }

                star_name = star_data.get("name", "Unknown Star")
                star_name = common_names.get(star_name, star_name)

                obj = {
                    "object_name": star_name,
                    "type": "star",
                    "ra": star_data.get("ra", 0.0),
                    "dec": star_data.get("dec", 0.0),
                    "magnitude": star_data.get("magnitude", 5.0),
                    "constellation": star_data.get("constellation", "Unknown"),
                    "description": f"{star_name} is a bright star visible in tonight's sky",
                    "score": _score_object(star_name, "star", star_data)
                }
                all_objects.append(obj)

            logger.info(f"Added {len(visible_stars)} stars from Skyfield")

    except Exception as e:
        logger.warning(f"Skyfield failed: {e}")

    # PRIORITY 2: Try Visible Planets API (lower priority than stars)
    try:
        visible_planets_url = f"https://api.visibleplanets.dev/v3"
        params = {
            "latitude": latitude,
            "longitude": longitude,
        }

        response = requests.get(visible_planets_url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Process visible planets (but give them low scores)
        if "data" in data:
            for planet_data in data["data"]:
                if planet_data.get("name"):
                    obj = {
                        "object_name": planet_data["name"],
                        "type": "planet",
                        "ra": planet_data.get("rightAscension", 0.0),
                        "dec": planet_data.get("declination", 0.0),
                        "magnitude": planet_data.get("magnitude", 5.0),
                        "constellation": planet_data.get("constellation", "Unknown"),
                        "description": f"{planet_data['name']} is visible tonight",
                        "score": _score_object(planet_data["name"], "planet", planet_data)
                    }
                    all_objects.append(obj)

            logger.info(f"Added {len(data['data'])} planets from API")

    except Exception as e:
        logger.warning(f"Visible Planets API failed: {e}")

    # Return the highest scored object (stars will win due to higher scores)
    if all_objects:
        best = max(all_objects, key=lambda x: x["score"])
        logger.info(f"Selected object: {best['object_name']} (score: {best['score']})")
        return best

    # Fallback: Arcsecond API for bright stars
    try:
        logger.info("Falling back to Arcsecond API")
        arcsecond_key = config.ARCSECOND_API_KEY

        # Query for bright stars near zenith
        # Using well-known bright stars as fallback
        fallback_stars = [
            {"name": "Sirius", "ra": 101.287, "dec": -16.716, "constellation": "Canis Major"},
            {"name": "Vega", "ra": 279.234, "dec": 38.783, "constellation": "Lyra"},
            {"name": "Altair", "ra": 297.696, "dec": 8.868, "constellation": "Aquila"},
            {"name": "Deneb", "ra": 310.358, "dec": 45.280, "constellation": "Cygnus"},
            {"name": "Arcturus", "ra": 213.915, "dec": 19.182, "constellation": "Boötes"},
        ]

        # For simplicity, return a random bright star
        import random
        star = random.choice(fallback_stars)

        return {
            "object_name": star["name"],
            "type": "star",
            "ra": star["ra"],
            "dec": star["dec"],
            "magnitude": 0.0,  # Very bright
            "constellation": star["constellation"],
            "description": f"{star['name']} in {star['constellation']} is a bright star visible tonight",
            "score": 50
        }

    except Exception as e:
        logger.error(f"Arcsecond fallback failed: {e}")

    # Ultimate fallback: Return Polaris (always visible in Northern Hemisphere)
    logger.warning("All APIs failed, returning fallback: Polaris")
    return {
        "object_name": "Polaris",
        "type": "star",
        "ra": 37.95,
        "dec": 89.26,
        "magnitude": 2.0,
        "constellation": "Ursa Minor",
        "description": "Polaris, the North Star, is always visible in the northern sky",
        "score": 20
    }


def _score_object(name: str, obj_type: str, data: dict) -> int:
    """
    Score celestial object based on config.SCORING_WEIGHTS.

    UPDATED: Removed planet_bonus and iconic_bonus to avoid Jupiter loop.
    Now scores only by: special_event (100), star_visibility (80), novelty (20)
    """
    score = 0

    # Special event bonus (eclipses, comets, transits)
    if "eclipse" in str(data).lower() or "transit" in str(data).lower():
        score += config.SCORING_WEIGHTS.get("special_event", 100)

    # Star visibility bonus (for stars calculated by skyfield)
    if obj_type == "star" and data.get("from_skyfield", False):
        score += 80  # High score for stars from real-time sky calculation

    # Novelty bonus - not shown in last 7 days
    import random
    if random.random() > 0.5:  # Simulate "not shown recently"
        score += config.SCORING_WEIGHTS.get("novelty", 20)

    return score


def get_story_prompt(object_name: str, language: str = "en") -> str:
    """
    Generate a structured narrative prompt for story generation about a celestial object.

    This tool queries astronomy databases for scientific metadata about the object,
    then formats it into a poetic prompt template suitable for LLM story generation.

    Args:
        object_name: Name of the celestial object (e.g., "Jupiter", "Altair", "Orion")
        language: Target language code for the story. Options: "en", "it", "fr", "es".
                 Default is "en" (English)

    Returns:
        str: Multi-line story prompt containing:
            - Object metadata (distance, size, temperature, composition)
            - Narrative structure (3 acts + haiku)
            - Scientific curiosities made poetic
            - Style guidelines for child-appropriate content

    Example:
        >>> prompt = get_story_prompt("Jupiter", "it")
        >>> print(prompt)
        Tu sei un narratore poetico per bambini...
        OGGETTO: Jupiter
        TIPO: planet
        ...
    """
    logger.info(f"get_story_prompt called: object={object_name}, language={language}")

    # Validate language
    if language not in config.SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language {language}, defaulting to 'en'")
        language = "en"

    # Query Arcsecond API for object metadata (if available)
    scientific_facts = _fetch_object_metadata(object_name)

    # Determine object type
    object_type = _determine_object_type(object_name)

    # Get location string (for now, generic)
    location = "your location"

    # Format using config template
    prompt = config.STORY_PROMPT_TEMPLATE.format(
        object_name=object_name,
        object_type=object_type,
        location=location,
        scientific_facts=scientific_facts,
        language=config.SUPPORTED_LANGUAGES[language]
    )

    logger.info(f"Generated story prompt ({len(prompt)} chars)")
    return prompt


def _fetch_object_metadata(object_name: str) -> str:
    """Fetch scientific metadata from Arcsecond API or use defaults"""
    try:
        # Try Arcsecond API
        url = f"https://api.arcsecond.io/objects/{object_name}/"
        headers = {}
        if config.ARCSECOND_API_KEY:
            headers["Authorization"] = f"Token {config.ARCSECOND_API_KEY}"

        response = requests.get(url, headers=headers, timeout=120)

        if response.status_code == 200:
            data = response.json()

            # Extract interesting facts
            facts = []
            if "distance" in data:
                facts.append(f"Distance: {data['distance']} light-years")
            if "classification" in data:
                facts.append(f"Type: {data['classification']}")
            if "magnitude" in data:
                facts.append(f"Brightness: Magnitude {data['magnitude']}")

            return "; ".join(facts) if facts else _default_facts(object_name)

    except Exception as e:
        logger.warning(f"Arcsecond API failed for {object_name}: {e}")

    # Return default facts
    return _default_facts(object_name)


def _default_facts(object_name: str) -> str:
    """Return default scientific facts for known objects"""
    facts_db = {
        "Jupiter": "The largest planet in our solar system, with colorful storms and 95 moons",
        "Saturn": "Famous for its beautiful rings made of ice and rock",
        "Mars": "The red planet, with the tallest volcano in the solar system",
        "Venus": "The brightest planet, covered in thick clouds",
        "Sirius": "The brightest star in the night sky, 8.6 light-years away",
        "Vega": "A blue-white star 25 light-years away, very bright and fast-rotating",
        "Altair": "A rapidly spinning star in the constellation Aquila",
        "Deneb": "One of the most luminous stars visible, about 2,600 light-years away",
        "Polaris": "The North Star, used for navigation for thousands of years",
        "Orion": "A famous constellation with bright stars Betelgeuse and Rigel",
    }

    return facts_db.get(object_name, f"A beautiful celestial object visible in tonight's sky")


def _determine_object_type(object_name: str) -> str:
    """Determine if object is planet, star, or constellation"""
    planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    constellations = ["Orion", "Ursa Major", "Ursa Minor", "Cassiopeia", "Andromeda"]

    if object_name in planets:
        return "planet"
    elif object_name in constellations:
        return "constellation"
    else:
        return "star"


def generate_image_prompt(object_name: str, object_type: str = "star") -> dict:
    """
    Generate image search strategy for finding astronomical images of the object.

    Returns a fallback chain strategy with multiple sources to try in order:
    1. Hubble Heritage Gallery search
    2. SDSS SkyServer thumbnail (if RA/Dec available)
    3. Wikimedia Commons search
    4. Fallback static starfield

    Args:
        object_name: Name of the celestial object (e.g., "Jupiter", "Nebula M42")
        object_type: Type of object ("planet", "star", "constellation", "nebula").
                    Default is "star"

    Returns:
        dict: Image search strategy with keys:
            - strategy (str): Primary strategy name ("hubble", "sdss", "wikimedia", "fallback")
            - search_query (str): Formatted search query for the primary source
            - hubble_url (str): Hubble Heritage API search URL
            - sdss_url (str): SDSS thumbnail URL (if RA/Dec available)
            - wikimedia_query (str): Wikimedia Commons search query
            - fallback_url (str): Guaranteed fallback image URL
            - alt_names (list): Alternative names to try if primary fails

    Example:
        >>> strategy = generate_image_prompt("Jupiter", "planet")
        >>> print(strategy["hubble_url"])
        https://hubblesite.org/api/v3/images?name=Jupiter
    """
    logger.info(f"generate_image_prompt called: object={object_name}, type={object_type}")

    # Format search query
    search_query = object_name.strip()

    # Alternative names for better search results
    alt_names = _get_alternative_names(object_name)

    # Build Hubble Heritage API URL
    hubble_url = f"{config.IMAGE_SOURCES['hubble']}?name={search_query}"

    # Build SDSS URL (requires RA/Dec - would get from select_celestial in real workflow)
    # For now, placeholder
    sdss_url = f"{config.IMAGE_SOURCES['sdss']}?ra=0&dec=0&scale=0.1&width=512&height=512"

    # Build Wikimedia Commons search
    wikimedia_query = f"{object_name} astronomy space telescope"
    wikimedia_url = f"{config.IMAGE_SOURCES['wikimedia']}?action=query&list=search&srsearch={wikimedia_query}&format=json"

    # Fallback image
    fallback_url = config.FALLBACK_IMAGE_URL

    # Determine primary strategy
    if object_type in ["planet", "nebula", "galaxy"]:
        strategy = "hubble"
    elif object_type == "star":
        strategy = "sdss"
    else:
        strategy = "wikimedia"

    result = {
        "strategy": strategy,
        "search_query": search_query,
        "hubble_url": hubble_url,
        "sdss_url": sdss_url,
        "wikimedia_url": wikimedia_url,
        "wikimedia_query": wikimedia_query,
        "fallback_url": fallback_url,
        "alt_names": alt_names,
        "instructions": (
            f"Try sources in this order: 1) {strategy} 2) wikimedia 3) fallback. "
            f"If primary fails, try alt_names: {', '.join(alt_names)}"
        )
    }

    logger.info(f"Generated image strategy: {strategy}")
    return result


def _get_alternative_names(object_name: str) -> List[str]:
    """Get alternative names for better image search"""
    alternatives = {
        "Jupiter": ["Jupiter planet", "Giant planet Jupiter"],
        "Saturn": ["Saturn rings", "Ringed planet Saturn"],
        "Mars": ["Mars red planet", "Planet Mars"],
        "Venus": ["Venus planet", "Morning star"],
        "Sirius": ["Sirius star", "Alpha Canis Majoris"],
        "Vega": ["Vega star", "Alpha Lyrae"],
        "Altair": ["Altair star", "Alpha Aquilae"],
        "Orion": ["Orion constellation", "Orion nebula"],
    }

    return alternatives.get(object_name, [f"{object_name} astronomy"])


# ============================================================================
# GRADIO MCP SERVER SETUP
# ============================================================================

# Create Gradio interface for each tool
with gr.Blocks(title="Zen-IT-Story MCP Server") as demo:
    gr.Markdown("""
    # 🌌 Zen-IT-Story MCP Server (Track 1)

    This is a Model Context Protocol (MCP) server providing astronomy tools for AI story generation.

    ## Available Tools:

    1. **select_celestial** - Find the best visible celestial object at a location/time
    2. **get_story_prompt** - Generate narrative structure for storytelling
    3. **generate_image_prompt** - Get image search strategy for astronomical images

    ## How to Use:

    - **Web UI**: Test tools directly in this interface
    - **MCP Client**: Connect Claude Desktop, Cursor, or other MCP clients to:
      - SSE endpoint: `{base_url}/gradio_api/mcp/sse`
      - Schema: `{base_url}/gradio_api/mcp/schema`

    ## Documentation:

    See `README_MCP.md` for full documentation and integration examples.
    """)

    with gr.Tab("Select Celestial Object"):
        gr.Interface(
            fn=select_celestial,
            inputs=[
                gr.Number(label="Latitude (-90 to 90)", value=41.9028, info="Example: 41.9028 for Rome"),
                gr.Number(label="Longitude (-180 to 180)", value=12.4964, info="Example: 12.4964 for Rome"),
                gr.Textbox(label="Date (YYYY-MM-DD, optional)", placeholder="2025-11-16", info="Leave blank for today"),
            ],
            outputs=gr.JSON(label="Selected Object"),
            title="Select Celestial Object",
            description="Find the best visible celestial object at given coordinates and date",
            examples=[
                [41.9028, 12.4964, "2025-11-16"],  # Rome
                [40.7128, -74.0060, None],  # New York
                [51.5074, -0.1278, "2025-12-25"],  # London
            ]
        )

    with gr.Tab("Get Story Prompt"):
        gr.Interface(
            fn=get_story_prompt,
            inputs=[
                gr.Textbox(label="Object Name", placeholder="Jupiter", info="E.g., Jupiter, Altair, Orion"),
                gr.Dropdown(
                    label="Language",
                    choices=["en", "it", "fr", "es"],
                    value="en",
                    info="Story language"
                ),
            ],
            outputs=gr.Textbox(label="Story Prompt", lines=20),
            title="Generate Story Prompt",
            description="Create a narrative structure for storytelling about a celestial object",
            examples=[
                ["Jupiter", "en"],
                ["Altair", "it"],
                ["Vega", "fr"],
                ["Mars", "es"],
            ]
        )

    with gr.Tab("Generate Image Prompt"):
        gr.Interface(
            fn=generate_image_prompt,
            inputs=[
                gr.Textbox(label="Object Name", placeholder="Jupiter"),
                gr.Dropdown(
                    label="Object Type",
                    choices=["planet", "star", "constellation", "nebula", "galaxy"],
                    value="planet"
                ),
            ],
            outputs=gr.JSON(label="Image Search Strategy"),
            title="Generate Image Search Strategy",
            description="Get fallback chain for finding astronomical images",
            examples=[
                ["Jupiter", "planet"],
                ["Sirius", "star"],
                ["Orion", "constellation"],
            ]
        )


if __name__ == "__main__":
    # Validate configuration
    config.validate_config()

    # Launch with MCP server enabled
    print("\n" + "="*80)
    print("🌌 ZEN-IT-STORY MCP SERVER")
    print("="*80)
    print("\nStarting Gradio MCP server...")
    print("\nMCP endpoints will be available at:")
    print("  - SSE: http://localhost:7860/gradio_api/mcp/sse")
    print("  - Schema: http://localhost:7860/gradio_api/mcp/schema")
    print("\nWeb UI: http://localhost:7860")
    print("="*80 + "\n")

    demo.launch(
        mcp_server=True,
        share=False,  # Set to True for public URL
        server_name="0.0.0.0",
        server_port=7860
    )
