"""
Zen-IT-Story Astronomy API Integration Module
Complete API integration layer with fallback chains and error handling
"""

import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import quote

import requests

from src.config import (
    ARCSECOND_API_KEY,
    CITIES,
    FALLBACK_IMAGE_URL,
    GEOLOC_API_URL,
    ICONIC_PLANETS,
    IMAGE_SOURCES,
    SCORING_WEIGHTS,
)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CACHING LAYER
# ============================================================================

_cache: Dict[str, Tuple[Any, float]] = {}
CACHE_TTL = 3600

def _get_cache_key(*args) -> str:
    key_str = "_".join(str(arg) for arg in args)
    return hashlib.md5(key_str.encode()).hexdigest()

def _get_from_cache(cache_key: str) -> Optional[Any]:
    if cache_key in _cache:
        value, timestamp = _cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            logger.info(f"Cache hit: {cache_key}")
            return value
        else:
            del _cache[cache_key]
            logger.info(f"Cache expired: {cache_key}")
    return None

def _set_to_cache(cache_key: str, value: Any) -> None:
    _cache[cache_key] = (value, time.time())
    logger.info(f"Cache set: {cache_key}")

# ============================================================================
# HTTP HELPERS
# ============================================================================

def _make_request(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 30,
    retry: bool = True
) -> Optional[requests.Response]:
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        logger.error(f"Timeout requesting {url}")
        if retry:
            logger.info(f"Retrying {url}...")
            return _make_request(url, params, headers, timeout, retry=False)
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        if retry:
            logger.info(f"Retrying {url}...")
            time.sleep(1)
            return _make_request(url, params, headers, timeout, retry=False)
        return None

# ============================================================================
# LOCATION PARSING - CRITICAL FUNCTIONS
# ============================================================================

def parse_location_input(location: str) -> Tuple[Optional[float], Optional[float], str]:
    """Parse location input string into coordinates and city name."""
    if not location or not location.strip():
        return None, None, ""
    
    location = location.strip()
    
    if location in CITIES:
        lat, lon = CITIES[location]
        logger.info(f"Exact match: {location} -> ({lat}, {lon})")
        return lat, lon, location
    
    location_lower = location.lower()
    for city_name, (lat, lon) in CITIES.items():
        if city_name.lower() == location_lower:
            logger.info(f"Case-insensitive match: {location} -> {city_name}")
            return lat, lon, city_name
    
    for city_name, (lat, lon) in CITIES.items():
        city_part = city_name.split(",")[0].strip().lower()
        if location_lower == city_part or city_part in location_lower or location_lower in city_part:
            logger.info(f"Partial match: {location} -> {city_name}")
            return lat, lon, city_name
    
    try:
        parts = location.replace(" ", "").split(",")
        if len(parts) == 2:
            lat = float(parts[0])
            lon = float(parts[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                logger.info(f"Coordinates parsed: ({lat}, {lon})")
                return lat, lon, f"Location ({lat:.2f}, {lon:.2f})"
    except (ValueError, IndexError):
        pass
    
    logger.warning(f"Could not parse location: {location}")
    return None, None, ""


def get_user_location_from_ip() -> Dict[str, Any]:
    """Get user location from IP address."""
    try:
        response = _make_request(GEOLOC_API_URL, timeout=3)
        
        if response is None:
            return {
                "error": True,
                "message": "Geolocation service unavailable",
                "latitude": None,
                "longitude": None,
                "city": None,
                "country": None
            }
        
        data = response.json()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if latitude is None or longitude is None:
            return {
                "error": True,
                "message": "Could not determine coordinates",
                "latitude": None,
                "longitude": None,
                "city": None,
                "country": None
            }
        
        return {
            "error": False,
            "latitude": latitude,
            "longitude": longitude,
            "city": data.get("city", "Unknown"),
            "country": data.get("country_name", data.get("country_code", "Unknown")),
            "timezone": data.get("timezone")
        }
        
    except Exception as e:
        logger.error(f"IP geolocation failed: {e}")
        return {
            "error": True,
            "message": str(e),
            "latitude": None,
            "longitude": None,
            "city": None,
            "country": None
        }


def format_location_display(city_name: str, lat: float, lon: float, language: str = "en") -> str:
    """Format location for display in the story."""
    directions = {
        "en": {"N": "N", "S": "S", "E": "E", "W": "W", "from": "Tonight's sky from"},
        "it": {"N": "N", "S": "S", "E": "E", "W": "O", "from": "Il cielo di stasera da"},
        "fr": {"N": "N", "S": "S", "E": "E", "W": "O", "from": "Le ciel ce soir depuis"},
        "es": {"N": "N", "S": "S", "E": "E", "W": "O", "from": "El cielo esta noche desde"},
    }
    
    d = directions.get(language, directions["en"])
    lat_dir = d["N"] if lat >= 0 else d["S"]
    lon_dir = d["E"] if lon >= 0 else d["W"]
    coord_str = f"{abs(lat):.1f} {lat_dir}, {abs(lon):.1f} {lon_dir}"
    
    return f"📍 **{d['from']} {city_name}**\n*({coord_str})*"


# ============================================================================
# VISIBLE PLANETS API
# ============================================================================

def get_visible_planets(
    latitude: float,
    longitude: float,
    date: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """Get visible planets at given location and date."""
    cache_key = _get_cache_key("visible_planets", latitude, longitude, date or "today")
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    url = "https://api.visibleplanets.dev/v3"
    params = {"latitude": latitude, "longitude": longitude}
    if date:
        params["date"] = date

    logger.info(f"Fetching visible planets for lat={latitude}, lon={longitude}, date={date}")
    response = _make_request(url, params=params)

    if response is None:
        return None

    try:
        data = response.json()
        planets = []
        for planet_name, planet_data in data.items():
            if isinstance(planet_data, dict):
                planet_info = {"name": planet_name.capitalize(), **planet_data}
                planets.append(planet_info)

        _set_to_cache(cache_key, planets)
        logger.info(f"Found {len(planets)} planets")
        return planets

    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse visible planets response: {e}")
        return None


# ============================================================================
# ARCSECOND API
# ============================================================================

def get_object_metadata(object_name: str) -> Optional[Dict[str, Any]]:
    """Get astronomical object metadata from Arcsecond.io."""
    cache_key = _get_cache_key("arcsecond", object_name.lower())
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    name_variations = [object_name, object_name.upper(), object_name.lower(), object_name.capitalize()]
    headers = {}
    if ARCSECOND_API_KEY:
        headers["Authorization"] = f"Token {ARCSECOND_API_KEY}"

    for name_variant in name_variations:
        url = f"https://api.arcsecond.io/objects/{quote(name_variant)}/"
        logger.info(f"Fetching metadata for {name_variant} from Arcsecond")

        response = _make_request(url, headers=headers)

        if response is not None:
            try:
                data = response.json()
                metadata = {
                    "name": data.get("name", object_name),
                    "ra": data.get("coordinates", {}).get("rightascension"),
                    "dec": data.get("coordinates", {}).get("declination"),
                    "distance": data.get("distance"),
                    "object_type": data.get("type", "unknown"),
                    "magnitude": data.get("magnitude"),
                    "constellation": data.get("constellation"),
                    "facts": data
                }
                _set_to_cache(cache_key, metadata)
                logger.info(f"Successfully fetched metadata for {object_name}")
                return metadata
            except (ValueError, KeyError) as e:
                logger.error(f"Failed to parse Arcsecond response for {name_variant}: {e}")
                continue

    logger.warning(f"Could not find object {object_name} on Arcsecond")
    return None


# ============================================================================
# IMAGE FETCHER (FALLBACK CHAIN)
# ============================================================================

def _search_hubble_heritage(object_name: str) -> Optional[str]:
    """Search Hubble Heritage Gallery for object images."""
    try:
        url = IMAGE_SOURCES["hubble"]
        params = {"page": "all", "collection_name": object_name}
        logger.info(f"Searching Hubble Heritage for {object_name}")
        response = _make_request(url, params=params, timeout=120)

        if response is None:
            return None

        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                if "image_files" in item and len(item["image_files"]) > 0:
                    image_files = item["image_files"]
                    if image_files:
                        largest = max(image_files, key=lambda x: x.get("file_size", 0))
                        image_url = largest.get("file_url")
                        if image_url:
                            logger.info(f"Found Hubble image: {image_url}")
                            return image_url
        return None
    except Exception as e:
        logger.error(f"Hubble Heritage search failed: {e}")
        return None


def _generate_sdss_image(ra: Optional[float], dec: Optional[float]) -> Optional[str]:
    """Generate SDSS SkyServer thumbnail image from RA/Dec coordinates."""
    if ra is None or dec is None:
        return None
    try:
        base_url = IMAGE_SOURCES["sdss"]
        params = {"ra": ra, "dec": dec, "scale": 0.4, "width": 512, "height": 512, "opt": "G"}
        url = base_url + "?" + "&".join(f"{k}={v}" for k, v in params.items())
        response = _make_request(url, timeout=120)
        if response and response.status_code == 200:
            logger.info(f"Generated SDSS image for RA={ra}, Dec={dec}")
            return url
        return None
    except Exception as e:
        logger.error(f"SDSS image generation failed: {e}")
        return None


def _search_wikimedia_commons(object_name: str) -> Optional[str]:
    """Search Wikimedia Commons for astronomy images."""
    try:
        url = IMAGE_SOURCES["wikimedia"]
        search_term = f"{object_name} astronomy"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_term,
            "srnamespace": "6",
            "srlimit": "5"
        }
        
        logger.info(f"Searching Wikimedia Commons for {search_term}")
        response = _make_request(url, params=params, timeout=120)

        if response is None:
            return None

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        if not search_results:
            return None

        for result in search_results:
            title = result.get("title", "")
            params2 = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url"
            }
            response2 = _make_request(url, params=params2, timeout=30)
            if response2:
                data2 = response2.json()
                pages = data2.get("query", {}).get("pages", {})
                for page in pages.values():
                    imageinfo = page.get("imageinfo", [])
                    if imageinfo and len(imageinfo) > 0:
                        image_url = imageinfo[0].get("url")
                        if image_url:
                            logger.info(f"Found Wikimedia image: {image_url}")
                            return image_url
        return None
    except Exception as e:
        logger.error(f"Wikimedia Commons search failed: {e}")
        return None


def get_object_image(
    object_name: str,
    ra: Optional[float] = None,
    dec: Optional[float] = None
) -> str:
    """Get astronomical image with fallback chain."""
    cache_key = _get_cache_key("image", object_name, ra, dec)
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    logger.info(f"Searching for image of {object_name}")

    image_url = _search_hubble_heritage(object_name)
    if image_url:
        _set_to_cache(cache_key, image_url)
        return image_url

    if ra is not None and dec is not None:
        image_url = _generate_sdss_image(ra, dec)
        if image_url:
            _set_to_cache(cache_key, image_url)
            return image_url

    image_url = _search_wikimedia_commons(object_name)
    if image_url:
        _set_to_cache(cache_key, image_url)
        return image_url

    logger.warning(f"Using fallback image for {object_name}")
    _set_to_cache(cache_key, FALLBACK_IMAGE_URL)
    return FALLBACK_IMAGE_URL


# ============================================================================
# GEOLOCATION API (Legacy wrapper)
# ============================================================================

def get_user_location() -> Optional[Dict[str, Any]]:
    """Get user location from IP address (legacy function)."""
    result = get_user_location_from_ip()
    if result.get("error"):
        return None
    return {
        "city": result["city"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result["country"],
        "timezone": result.get("timezone")
    }


# ============================================================================
# CELESTIAL OBJECT SCORING
# ============================================================================

_recently_shown: Dict[str, float] = {}

def _is_recently_shown(object_name: str, days: int = 7) -> bool:
    if object_name not in _recently_shown:
        return False
    last_shown = _recently_shown[object_name]
    days_ago = (time.time() - last_shown) / 86400
    return days_ago < days

def _mark_as_shown(object_name: str) -> None:
    _recently_shown[object_name] = time.time()

def score_celestial_object(
    object_name: str,
    object_type: str = "unknown",
    is_special_event: bool = False
) -> float:
    """Score celestial object based on configured priorities."""
    score = 0.0

    if is_special_event:
        score += SCORING_WEIGHTS["special_event"]
        logger.info(f"{object_name}: +{SCORING_WEIGHTS['special_event']} (special event)")

    if object_type.lower() == "planet" or object_name.capitalize() in ICONIC_PLANETS:
        score += SCORING_WEIGHTS["planet_bonus"]
        logger.info(f"{object_name}: +{SCORING_WEIGHTS['planet_bonus']} (planet)")

    if object_name.capitalize() in ICONIC_PLANETS:
        score += SCORING_WEIGHTS["iconic_bonus"]
        logger.info(f"{object_name}: +{SCORING_WEIGHTS['iconic_bonus']} (iconic)")

    if not _is_recently_shown(object_name):
        score += SCORING_WEIGHTS["novelty"]
        logger.info(f"{object_name}: +{SCORING_WEIGHTS['novelty']} (novel)")
    else:
        logger.info(f"{object_name}: Recently shown, no novelty bonus")

    logger.info(f"{object_name} total score: {score}")
    return score


def select_best_object(
    latitude: float,
    longitude: float,
    date: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Select the best celestial object to feature tonight."""
    logger.info(f"Selecting best object for lat={latitude}, lon={longitude}, date={date}")

    planets = get_visible_planets(latitude, longitude, date)
    if not planets:
        logger.warning("No visible planets found")
        return None

    visible = [p for p in planets if p.get("aboveHorizon", False)]
    if not visible:
        logger.warning("No planets above horizon")
        visible = planets

    scored_objects = []
    for planet in visible:
        name = planet.get("name", "Unknown")
        is_special = False
        score = score_celestial_object(object_name=name, object_type="planet", is_special_event=is_special)
        scored_objects.append({
            "name": name,
            "type": "planet",
            "score": score,
            "altitude": planet.get("altitude"),
            "azimuth": planet.get("azimuth"),
            "magnitude": planet.get("magnitude"),
            "aboveHorizon": planet.get("aboveHorizon", False),
            "metadata": planet
        })

    scored_objects.sort(key=lambda x: x["score"], reverse=True)

    if scored_objects:
        best_object = scored_objects[0]
        logger.info(f"Selected: {best_object['name']} (score: {best_object['score']})")
        _mark_as_shown(best_object["name"])
        return best_object

    return None


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def get_tonight_story_data(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    date: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get complete data for tonight's story."""
    if latitude is None or longitude is None:
        location = get_user_location()
        if location:
            latitude = location["latitude"]
            longitude = location["longitude"]
            city = location["city"]
        else:
            logger.error("Could not determine user location")
            return None
    else:
        location = {"latitude": latitude, "longitude": longitude, "city": "Unknown"}
        for city_name, (lat, lon) in CITIES.items():
            if abs(lat - latitude) < 0.1 and abs(lon - longitude) < 0.1:
                location["city"] = city_name
                break

    best_object = select_best_object(latitude, longitude, date)
    if not best_object:
        logger.error("Could not select celestial object")
        return None

    metadata = get_object_metadata(best_object["name"])
    ra = metadata.get("ra") if metadata else None
    dec = metadata.get("dec") if metadata else None
    image_url = get_object_image(best_object["name"], ra, dec)

    story_data = {
        "object": best_object,
        "location": location,
        "metadata": metadata or {},
        "image_url": image_url,
        "date": date or datetime.now().strftime("%Y-%m-%d")
    }

    logger.info(f"Story data compiled for {best_object['name']}")
    return story_data


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_cache() -> None:
    """Clear all cached data."""
    global _cache, _recently_shown
    _cache.clear()
    _recently_shown.clear()
    logger.info("Cache cleared")

def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics."""
    return {"cache_entries": len(_cache), "recently_shown": len(_recently_shown)}
