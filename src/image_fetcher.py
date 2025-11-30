"""
Image Fetcher - Astronomical Image Retrieval
OPZIONE C+: Self-healing resilient fallback chain
Curated (HEAD check) → NASA Images → Hubble → SDSS/SkyView → Wikimedia → APOD → Starfield
"""

import requests
import logging
from typing import Optional, Dict
from src import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CURATED STAR IMAGE MAPPING (Priority source for common stars)
# ============================================================================

STAR_IMAGE_MAPPING = {
    # Northern Hemisphere bright stars
    "Vega": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Vega_-_20210629.png/1200px-Vega_-_20210629.png",
        "credit": "Wikimedia Commons / ESO",
        "alt_text": "Vega, a brilliant blue-white star in the constellation Lyra"
    },
    "Polaris": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Polaris_system.jpg/1200px-Polaris_system.jpg",
        "credit": "Wikimedia Commons / NASA",
        "alt_text": "Polaris, the North Star, a triple star system in Ursa Minor"
    },
    "Arcturus": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Arcturus-star.jpg/1200px-Arcturus-star.jpg",
        "credit": "Wikimedia Commons",
        "alt_text": "Arcturus, a bright orange giant star in the constellation Boötes"
    },
    "Deneb": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Deneb_2MASS.jpg/1200px-Deneb_2MASS.jpg",
        "credit": "Wikimedia Commons / 2MASS",
        "alt_text": "Deneb, one of the most luminous stars visible, in the constellation Cygnus"
    },
    "Altair": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Altair_-_Interferometric_Image.jpg/800px-Altair_-_Interferometric_Image.jpg",
        "credit": "Wikimedia Commons / CHARA",
        "alt_text": "Altair, a rapidly rotating star in the constellation Aquila"
    },

    # Southern Hemisphere bright stars
    "Sirius": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Sirius_A_and_B_artwork.jpg/1200px-Sirius_A_and_B_artwork.jpg",
        "credit": "Wikimedia Commons / NASA",
        "alt_text": "Sirius, the brightest star in the night sky, a binary system in Canis Major"
    },
    "Canopus": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Canopus_seen_from_Tokyo.jpg/1200px-Canopus_seen_from_Tokyo.jpg",
        "credit": "Wikimedia Commons",
        "alt_text": "Canopus, the second brightest star in the night sky, in the constellation Carina"
    },
    "Alpha Centauri": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Alpha_Centauri_AB_over_limb_of_Saturn.jpg/1200px-Alpha_Centauri_AB_over_limb_of_Saturn.jpg",
        "credit": "Wikimedia Commons / NASA",
        "alt_text": "Alpha Centauri, the closest star system to our Sun, in the constellation Centaurus"
    },
    "Achernar": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Achernar_Hubble.jpg/800px-Achernar_Hubble.jpg",
        "credit": "Wikimedia Commons / Hubble",
        "alt_text": "Achernar, a bright blue star in the constellation Eridanus"
    },

    # Additional common stars
    "Betelgeuse": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Betelgeuse_captured_by_ALMA.jpg/1200px-Betelgeuse_captured_by_ALMA.jpg",
        "credit": "Wikimedia Commons / ALMA",
        "alt_text": "Betelgeuse, a red supergiant star in the constellation Orion"
    },
    "Rigel": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Rigel_star_system.jpg/1200px-Rigel_star_system.jpg",
        "credit": "Wikimedia Commons",
        "alt_text": "Rigel, a blue supergiant star in the constellation Orion"
    },
    "Procyon": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Procyon.jpg/1200px-Procyon.jpg",
        "credit": "Wikimedia Commons",
        "alt_text": "Procyon, a bright star in the constellation Canis Minor"
    },
    "Capella": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Capella_Hubble.jpg/1200px-Capella_Hubble.jpg",
        "credit": "Wikimedia Commons / Hubble",
        "alt_text": "Capella, a bright yellow star system in the constellation Auriga"
    },
}


def try_curated_star_image(object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to get curated image from our mapping of common stars.

    OPZIONE C+: Self-healing resilient system
    - Checks URL availability with fast HEAD request (2 sec timeout)
    - If URL works → use curated mapping (fast!)
    - If URL fails (403, timeout) → return None, fallback to NASA Images API

    Args:
        object_name: Star name (e.g., "Vega", "Sirius")

    Returns:
        Dict with image info if URL is accessible, None otherwise
    """
    if object_name in STAR_IMAGE_MAPPING:
        star_data = STAR_IMAGE_MAPPING[object_name]
        url = star_data["url"]

        # OPZIONE C+: Quick HEAD check to verify URL is accessible
        try:
            response = requests.head(url, timeout=2, allow_redirects=True)
            if response.status_code == 200:
                logger.info(f"✓ Using curated image for {object_name} (URL verified)")
                return {
                    "url": url,
                    "source": "curated",
                    "alt_text": star_data["alt_text"],
                    "credit": star_data["credit"]
                }
            else:
                logger.warning(f"✗ Curated URL for {object_name} returned {response.status_code}, trying fallback APIs")
                return None
        except Exception as e:
            logger.warning(f"✗ Curated URL for {object_name} failed ({e}), trying fallback APIs")
            return None
    return None


def fetch_image(
    object_name: str,
    object_type: str = "star",
    ra: Optional[float] = None,
    dec: Optional[float] = None
) -> Dict[str, str]:
    """
    Fetch astronomical image using self-healing fallback chain.

    OPZIONE C+: Resilient Hybrid System
    1. Curated star mapping with HEAD check (fast verification, auto-fallback if 403)
    2. NASA Images API (searches by name, no auth)
    3. Hubble Heritage Gallery (searches by name, best quality)
    4. SDSS SkyServer (if RA/Dec available, uses coordinates)
    5. NASA SkyView Virtual Observatory (if RA/Dec available, very reliable)
    6. Wikimedia Commons (searches by name, good coverage)
    7. NASA APOD (moved here - last resort before generic fallback)
    8. Generic starfield (guaranteed fallback)

    Smart behavior: If curated URL fails (403, timeout), automatically falls back
    to NASA Images API without crashing. Zero maintenance, self-healing!

    Args:
        object_name: Name of celestial object
        object_type: Type ("planet", "star", "constellation", "nebula")
        ra: Right Ascension in degrees (optional, for SDSS/SkyView)
        dec: Declination in degrees (optional, for SDSS/SkyView)

    Returns:
        Dict with keys:
            - url: Image URL
            - source: Source name
            - alt_text: Alt text for image
            - credit: Image credit/attribution
    """
    logger.info(f"Fetching image for {object_name} ({object_type})")

    # PRIORITY 1: Try curated mapping (for common stars)
    curated_result = try_curated_star_image(object_name)
    if curated_result:
        logger.info("✓ Image from curated star mapping")
        return curated_result

    # PRIORITY 2: NASA SkyView - Real astronomical images using coordinates
    if ra is not None and dec is not None:
        skyview_result = try_skyview(ra, dec, object_name)
        if skyview_result:
            logger.info("✓ Image from NASA SkyView")
            return skyview_result

    # PRIORITY 3: SDSS SkyServer - Real sky survey images using coordinates
    if ra is not None and dec is not None:
        sdss_result = try_sdss(ra, dec, object_name)
        if sdss_result:
            logger.info("✓ Image from SDSS SkyServer")
            return sdss_result

    # PRIORITY 4: Hubble Heritage (searches by name)
    hubble_result = try_hubble(object_name)
    if hubble_result:
        logger.info("✓ Image from Hubble Heritage")
        return hubble_result

    # PRIORITY 5: NASA Images API - DISABLED (artistic/fake images)
    # nasa_result = try_nasa_images(object_name)
    # if nasa_result:
    #     logger.info("✓ Image from NASA Images API")
    #     return nasa_result

    # PRIORITY 6: Try Wikimedia Commons (searches by name)
    wikimedia_result = try_wikimedia(object_name)
    if wikimedia_result:
        logger.info("✓ Image from Wikimedia Commons")
        return wikimedia_result

    # PRIORITY 7: Try NASA APOD (MOVED HERE - last resort API)
    # NOTE: This returns a random astronomy picture of the day,
    # NOT necessarily related to the object. Only use as last resort.
    apod_result = try_nasa_apod(object_name)
    if apod_result:
        logger.info("⚠️  Image from NASA APOD (may not match object)")
        return apod_result

    # PRIORITY 8: Fallback to generic starfield
    logger.warning("All sources failed, using fallback starfield")
    return {
        "url": config.FALLBACK_IMAGE_URL,
        "source": "fallback",
        "alt_text": f"Beautiful starfield representing {object_name}",
        "credit": "Unsplash starfield"
    }


def try_nasa_images(object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from NASA Images API (no authentication required!).

    Args:
        object_name: Object name to search

    Returns:
        Dict with image info if found, None otherwise
    """
    try:
        url = "https://images-api.nasa.gov/search"
        params = {
            "q": object_name,
            "media_type": "image"
        }

        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Check if we got results
        if data and "collection" in data and "items" in data["collection"]:
            items = data["collection"]["items"]

            if len(items) > 0:
                # Get first result with image
                for item in items[:5]:  # Check first 5 results
                    if "links" in item and len(item["links"]) > 0:
                        image_url = item["links"][0]["href"]
                        description = item.get("data", [{}])[0].get("description", f"{object_name} from NASA")
                        title = item.get("data", [{}])[0].get("title", object_name)

                        return {
                            "url": image_url,
                            "source": "nasa_images",
                            "alt_text": title,
                            "credit": "NASA Images"
                        }

    except Exception as e:
        logger.warning(f"NASA Images API failed: {e}")

    return None


def try_nasa_apod(object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from NASA APOD (Astronomy Picture of the Day).
    Uses DEMO_KEY (no signup required).

    Args:
        object_name: Object name (used in alt text)

    Returns:
        Dict with image info if successful, None otherwise
    """
    try:
        url = "https://api.nasa.gov/planetary/apod"
        params = {
            "api_key": "DEMO_KEY",
            "count": 1  # Get 1 random image
        }

        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            apod = data[0]

            # Only use if it's an image (not video)
            if apod.get("media_type") == "image":
                return {
                    "url": apod["url"],
                    "source": "nasa_apod",
                    "alt_text": apod.get("title", f"Astronomy picture related to {object_name}"),
                    "credit": "NASA APOD"
                }

    except Exception as e:
        logger.warning(f"NASA APOD API failed: {e}")

    return None


def try_hubble(object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from Hubble Heritage API.

    Args:
        object_name: Object name to search

    Returns:
        Dict with image info if found, None otherwise
    """
    try:
        url = f"{config.IMAGE_SOURCES['hubble']}"
        params = {"name": object_name}

        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Check if we got results
        if data and isinstance(data, list) and len(data) > 0:
            # Get first result
            image = data[0]
            image_url = image.get("image_files", [{}])[0].get("file_url")

            if image_url:
                return {
                    "url": image_url,
                    "source": "hubble",
                    "alt_text": image.get("description", f"{object_name} captured by Hubble Space Telescope"),
                    "credit": "NASA/ESA Hubble Space Telescope"
                }

    except Exception as e:
        logger.warning(f"Hubble API failed: {e}")

    return None


def try_sdss(ra: float, dec: float, object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from SDSS SkyServer.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        object_name: Object name for alt text

    Returns:
        Dict with image info if successful, None otherwise
    """
    try:
        # SDSS Image Cutout Service
        # Parameters: ra, dec, scale (arcsec/pixel), width, height
        params = {
            "ra": ra,
            "dec": dec,
            "scale": 0.2,  # 0.2 arcsec/pixel
            "width": 512,
            "height": 512,
            "opt": "G"  # SDSS g-band (green/visual)
        }

        url = config.IMAGE_SOURCES['sdss']
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()

        # If we got an image (status 200 and content), return it
        if response.headers.get('content-type', '').startswith('image/'):
            return {
                "url": response.url,
                "source": "sdss",
                "alt_text": f"Sky view of {object_name} region from SDSS",
                "credit": "Sloan Digital Sky Survey (SDSS)"
            }

    except Exception as e:
        logger.warning(f"SDSS API failed: {e}")

    return None


def try_arcsecond(ra: float, dec: float, object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from Arcsecond.io API.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        object_name: Object name for alt text

    Returns:
        Dict with image info if successful, None otherwise
    """
    try:
        # Arcsecond.io search by coordinates
        url = "https://api.arcsecond.io/exoplanets/"
        params = {
            "ra": ra,
            "dec": dec,
            "radius": 1.0  # 1 degree search radius
        }

        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Check if we got results with images
        if data and isinstance(data, dict) and "results" in data:
            results = data["results"]
            if results and len(results) > 0:
                obj = results[0]
                # Arcsecond.io doesn't provide direct image URLs usually
                # Return object URL as fallback
                object_url = obj.get("url", "")
                if object_url:
                    return {
                        "url": config.FALLBACK_IMAGE_URL,  # No direct image
                        "source": "arcsecond",
                        "alt_text": f"{object_name} - Arcsecond.io catalog entry",
                        "credit": "Arcsecond.io"
                    }

    except Exception as e:
        logger.warning(f"Arcsecond.io API failed: {e}")

    return None


def try_skyview(ra: float, dec: float, object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from NASA SkyView Virtual Observatory.
    Very reliable source with multiple surveys.

    Args:
        ra: Right Ascension in degrees
        dec: Declination in degrees
        object_name: Object name for alt text

    Returns:
        Dict with image info if successful, None otherwise
    """
    try:
        # NASA SkyView image cutout service
        # Using DSS (Digitized Sky Survey) - most reliable
        base_url = "https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl"

        params = {
            "Position": f"{ra},{dec}",
            "Survey": "DSS",  # Digitized Sky Survey (optical)
            "Pixels": "512",
            "Return": "FITS",  # Or GIF for direct image
            "coordinates": "J2000"
        }

        # Actually, SkyView returns FITS files which need processing
        # Better approach: use SkyView's quicklook feature
        quicklook_url = f"https://skyview.gsfc.nasa.gov/current/cgi/pskcall?Position={ra},{dec}&Survey=DSS&Pixels=512&Return=GIF"

        response = requests.get(quicklook_url, timeout=120)
        response.raise_for_status()

        # If we got an image (GIF), return the URL
        if response.headers.get('content-type', '').startswith('image/'):
            return {
                "url": quicklook_url,
                "source": "skyview",
                "alt_text": f"Sky view of {object_name} region from NASA SkyView",
                "credit": "NASA SkyView Virtual Observatory (DSS)"
            }

    except Exception as e:
        logger.warning(f"NASA SkyView API failed: {e}")

    return None


def try_wikimedia(object_name: str) -> Optional[Dict[str, str]]:
    """
    Try to fetch image from Wikimedia Commons.

    Args:
        object_name: Object name to search

    Returns:
        Dict with image info if found, None otherwise
    """
    try:
        # Wikimedia Commons API - search for images
        search_query = f"{object_name} astronomy space telescope"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srnamespace": 6,  # File namespace
            "srlimit": 5
        }

        url = config.IMAGE_SOURCES['wikimedia']
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Get search results
        if "query" in data and "search" in data["query"]:
            results = data["query"]["search"]

            if results:
                # Get first result that looks like an image
                for result in results:
                    title = result.get("title", "")

                    # Get image info
                    info_params = {
                        "action": "query",
                        "format": "json",
                        "titles": title,
                        "prop": "imageinfo",
                        "iiprop": "url"
                    }

                    info_response = requests.get(url, params=info_params, timeout=120)
                    info_response.raise_for_status()
                    info_data = info_response.json()

                    # Extract image URL
                    pages = info_data.get("query", {}).get("pages", {})
                    for page_id, page in pages.items():
                        imageinfo = page.get("imageinfo", [])
                        if imageinfo:
                            image_url = imageinfo[0].get("url")
                            if image_url:
                                return {
                                    "url": image_url,
                                    "source": "wikimedia",
                                    "alt_text": f"{object_name} - {title}",
                                    "credit": "Wikimedia Commons"
                                }

    except Exception as e:
        logger.warning(f"Wikimedia API failed: {e}")

    return None


def get_image_for_object(
    object_name: str,
    object_data: Optional[Dict] = None
) -> Dict[str, str]:
    """
    Convenience function to fetch image with object data from MCP.

    Args:
        object_name: Name of celestial object
        object_data: Optional dict from select_celestial MCP tool

    Returns:
        Dict with image info
    """
    if object_data:
        return fetch_image(
            object_name=object_data.get("object_name", object_name),
            object_type=object_data.get("type", "star"),
            ra=object_data.get("ra"),
            dec=object_data.get("dec")
        )
    else:
        return fetch_image(object_name, "star", None, None)


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_image_fetching():
    """Test image fetching for various objects"""
    print("\n" + "="*80)
    print("Testing Image Fetcher")
    print("="*80 + "\n")

    test_cases = [
        ("Jupiter", "planet", None, None),
        ("Sirius", "star", 101.287, -16.716),
        ("Orion Nebula", "nebula", 83.822, -5.391),
        ("Unknown Object XYZ", "star", None, None),  # Should fallback
    ]

    for object_name, obj_type, ra, dec in test_cases:
        print(f"\nTesting: {object_name}")
        print("-" * 40)

        result = fetch_image(object_name, obj_type, ra, dec)

        print(f"  Source: {result['source']}")
        print(f"  URL: {result['url'][:60]}...")
        print(f"  Credit: {result['credit']}")


if __name__ == "__main__":
    test_image_fetching()
