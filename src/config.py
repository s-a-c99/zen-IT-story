"""
Zen-IT-Story Configuration
All settings, API keys, i18n strings, and constants
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file (override system env vars)
load_dotenv(override=True)

# ============================================================================
# API KEYS (from environment variables)
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ARCSECOND_API_KEY = os.getenv("ARCSECOND_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# ============================================================================
# ASTRONOMY SETTINGS
# ============================================================================

# Celestial object scoring priorities
SCORING_WEIGHTS = {
    "special_event": 100,  # Eclipses, comets, transits
    "planet_bonus": 50,    # Planets are more interesting for kids
    "iconic_bonus": 30,    # Jupiter, Saturn, Mars get extra points
    "novelty": 20,         # Not shown in last 7 days
    # NOTE: Magnitude (brightness) removed - kids don't look outside
}

ICONIC_PLANETS = ["Jupiter", "Saturn", "Mars", "Venus"]

# ============================================================================
# GEOLOCATION
# ============================================================================

# Major cities with pre-mapped coordinates (300 global cities)
CITIES: Dict[str, tuple[float, float]] = {
    # ================== ITALY (30) ==================
    "Roma, Italia": (41.9028, 12.4964),
    "Rome, Italy": (41.9028, 12.4964),  # English alias
    "Milano, Italia": (45.4642, 9.1900),
    "Milan, Italy": (45.4642, 9.1900),  # English alias
    "Napoli, Italia": (40.8518, 14.2681),
    "Naples, Italy": (40.8518, 14.2681),  # English alias
    "Torino, Italia": (45.0703, 7.6869),
    "Turin, Italy": (45.0703, 7.6869),  # English alias
    "Palermo, Italia": (38.1157, 13.3615),
    "Firenze, Italia": (43.7696, 11.2558),
    "Florence, Italy": (43.7696, 11.2558),  # English alias
    "Bologna, Italia": (44.4949, 11.3426),
    "Venezia, Italia": (45.4408, 12.3155),
    "Venice, Italy": (45.4408, 12.3155),  # English alias
    "Genova, Italia": (44.4056, 8.9463),
    "Bari, Italia": (41.1176, 16.8728),
    "Catania, Italia": (37.4979, 15.0873),
    "Messina, Italia": (38.1939, 15.5565),
    "Verona, Italia": (45.4386, 10.9916),
    "Padova, Italia": (45.4064, 11.8768),
    "Trieste, Italia": (45.6452, 13.7777),
    "Brescia, Italia": (45.5313, 10.2197),
    "Parma, Italia": (44.8015, 10.3279),
    "Modena, Italia": (44.6471, 10.9252),
    "Pisa, Italia": (43.7228, 10.4016),
    "Siena, Italia": (43.3186, 11.9314),
    "Lecce, Italia": (40.3539, 18.1716),
    "Salerno, Italia": (40.6861, 14.7664),
    "Perugia, Italia": (43.1122, 12.3900),
    "Ancona, Italia": (43.6159, 13.5007),
    "Ravenna, Italia": (44.4169, 12.1939),
    "Rimini, Italia": (44.0571, 12.5674),
    "Benevento, Italia": (41.1393, 14.7810),
    "Cagliari, Italia": (39.2238, 9.1217),
    "Sassari, Italia": (40.7272, 8.5597),
    "Reggio Calabria, Italia": (38.1156, 15.6564),

    # ================== EUROPE (100) ==================
    # France (12)
    "Paris, France": (48.8566, 2.3522),
    "Lyon, France": (45.7640, 4.8357),
    "Marseille, France": (43.2965, 5.3698),
    "Nice, France": (43.7102, 7.2620),
    "Toulouse, France": (43.6047, 1.4442),
    "Nantes, France": (47.2184, -1.5536),
    "Strasbourg, France": (48.5734, 7.7521),
    "Bordeaux, France": (44.8378, -0.5792),
    "Lille, France": (50.6292, 3.0573),
    "Rennes, France": (48.1113, -1.6800),
    "Le Havre, France": (49.4944, 0.1079),
    "Grenoble, France": (45.1885, 5.7245),

    # Spain (10)
    "Madrid, España": (40.4168, -3.7038),
    "Barcelona, España": (41.3851, 2.1734),
    "Valencia, España": (39.4699, -0.3763),
    "Sevilla, España": (37.3891, -5.9845),
    "Bilbao, España": (43.2633, -2.9349),
    "Málaga, España": (36.7201, -4.4203),
    "Zaragoza, España": (41.6488, -0.8891),
    "Córdoba, España": (37.8882, -4.7794),
    "Murcia, España": (37.9922, -1.1307),
    "Palma de Mallorca, España": (39.5696, 2.6502),

    # Germany (9)
    "Berlin, Germany": (52.5200, 13.4050),
    "Munich, Germany": (48.1351, 11.5820),
    "Hamburg, Germany": (53.5511, 9.9937),
    "Frankfurt, Germany": (50.1109, 8.6821),
    "Cologne, Germany": (50.9375, 6.9603),
    "Stuttgart, Germany": (48.7758, 9.1829),
    "Düsseldorf, Germany": (51.2277, 6.7735),
    "Dortmund, Germany": (51.5141, 7.4653),
    "Essen, Germany": (51.4556, 7.0116),

    # UK & Ireland (9)
    "London, UK": (51.5074, -0.1278),
    "Manchester, UK": (53.4808, -2.2426),
    "Edinburgh, UK": (55.9533, -3.1883),
    "Liverpool, UK": (53.4084, -2.9916),
    "Glasgow, UK": (55.8642, -4.2518),
    "Birmingham, UK": (52.5086, -1.8755),
    "Leeds, UK": (53.8008, -1.5491),
    "Bristol, UK": (51.4545, -2.5879),
    "Dublin, Ireland": (53.3498, -6.2603),

    # Scandinavia (8)
    "Stockholm, Sweden": (59.3293, 18.0686),
    "Copenhagen, Denmark": (55.6761, 12.5683),
    "Oslo, Norway": (59.9139, 10.7522),
    "Helsinki, Finland": (60.1695, 24.9354),
    "Gothenburg, Sweden": (57.7089, 11.9746),
    "Bergen, Norway": (60.3894, 5.3300),
    "Malmö, Sweden": (55.6050, 13.0038),
    "Tallinn, Estonia": (59.4370, 24.7536),

    # Central/Eastern Europe (15)
    "Prague, Czech Republic": (50.0755, 14.4378),
    "Budapest, Hungary": (47.4979, 19.0402),
    "Warsaw, Poland": (52.2297, 21.0122),
    "Vienna, Austria": (48.2082, 16.3738),
    "Kraków, Poland": (50.0647, 19.9450),
    "Wrocław, Poland": (51.1079, 17.0385),
    "Bucharest, Romania": (44.4268, 26.1025),
    "Belgrade, Serbia": (44.8176, 20.4633),
    "Sofia, Bulgaria": (42.6977, 23.3219),
    "Athens, Greece": (37.9838, 23.7275),
    "Bratislava, Slovakia": (48.1486, 17.1077),
    "Ljubljana, Slovenia": (46.0569, 14.5058),
    "Zagreb, Croatia": (45.8150, 15.9819),
    "Riga, Latvia": (56.9496, 24.1052),
    "Vilnius, Lithuania": (54.6872, 25.2797),

    # Southern/Mediterranean Europe (25)
    "Thessaloniki, Greece": (40.6401, 22.9444),
    "Istanbul, Turkey": (41.0082, 28.9784),
    "Lisbon, Portugal": (38.7223, -9.1393),
    "Porto, Portugal": (41.1579, -8.6291),
    "Split, Croatia": (43.5081, 16.4402),
    "Dubrovnik, Croatia": (42.6412, 18.1093),
    "Valletta, Malta": (35.8989, 14.5146),
    "Nicosia, Cyprus": (35.1856, 33.3823),
    "Chania, Crete, Greece": (35.3387, 24.4615),
    "Athens, Greece": (37.9838, 23.7275),
    "Ankara, Turkey": (39.9334, 32.8597),
    "Izmir, Turkey": (38.4161, 27.1302),
    "Antalya, Turkey": (36.9124, 30.5597),
    "Beirut, Lebanon": (33.8869, 35.4955),
    "Damascus, Syria": (33.5138, 36.2765),
    "Baghdad, Iraq": (33.3128, 44.3615),
    "Tehran, Iran": (35.6892, 51.3890),
    "Amman, Jordan": (31.9454, 35.9284),
    "Cairo, Egypt": (30.0444, 31.2357),
    "Alexandria, Egypt": (31.2001, 29.9187),
    "Zadar, Croatia": (23.1291, 113.2644),
    "Tirana, Albania": (41.3275, 19.8187),
    "Pristina, Kosovo": (42.6726, 21.1789),
    "Skopje, North Macedonia": (41.9973, 21.4280),
    "Podgorica, Montenegro": (42.4304, 19.2594),
    "Giza, Egypt": (30.0131, 31.2089),

    # ================== AMERICAS (80) ==================
    # North America - USA (35)
    "New York, USA": (40.7128, -74.0060),
    "Los Angeles, USA": (34.0522, -118.2437),
    "Chicago, USA": (41.8781, -87.6298),
    "Washington DC, USA": (38.9072, -77.0369),
    "Washington, USA": (38.9072, -77.0369),  # Alias for Washington DC
    "Houston, USA": (29.7604, -95.3698),
    "San Francisco, USA": (37.7749, -122.4194),
    "Phoenix, USA": (33.4484, -112.0742),
    "Philadelphia, USA": (39.9526, -75.1652),
    "San Antonio, USA": (29.4241, -98.4936),
    "San Diego, USA": (32.7157, -117.1611),
    "Dallas, USA": (32.7767, -96.7970),
    "Austin, USA": (30.2672, -97.7431),
    "Seattle, USA": (47.6062, -122.3321),
    "Denver, USA": (39.7392, -104.9903),
    "Boston, USA": (42.3601, -71.0589),
    "Miami, USA": (25.7617, -80.1918),
    "Atlanta, USA": (33.7490, -84.3880),
    "Las Vegas, USA": (36.1699, -115.1398),
    "Portland, USA": (45.5152, -122.6784),
    "Detroit, USA": (42.3314, -83.0458),
    "Minneapolis, USA": (44.9778, -93.2650),
    "Nashville, USA": (36.1627, -86.7816),
    "Charlotte, USA": (35.2271, -80.8431),
    "Memphis, USA": (35.1495, -90.0490),
    "Baltimore, USA": (39.2904, -76.6122),
    "New Orleans, USA": (29.9511, -90.2623),
    "Milwaukee, USA": (43.0389, -87.9065),
    "Albuquerque, USA": (35.0844, -106.6504),
    "Tucson, USA": (32.2226, -110.9747),
    "Fresno, USA": (36.7469, -119.7726),
    "Sacramento, USA": (38.5816, -121.4944),
    "Long Beach, USA": (33.7701, -118.1937),
    "Kansas City, USA": (39.0997, -94.5786),
    "Mesa, USA": (33.4152, -111.8313),
    "Virginia Beach, USA": (36.8529, -75.9780),
    "Atlanta, USA": (33.7490, -84.3880),
    "Columbus, USA": (39.9612, -82.9988),

    # Canada (6)
    "Toronto, Canada": (43.6532, -79.3832),
    "Vancouver, Canada": (49.2827, -123.1207),
    "Montreal, Canada": (45.5017, -73.5673),
    "Calgary, Canada": (51.0447, -114.0719),
    "Ottawa, Canada": (45.4215, -75.6972),
    "Winnipeg, Canada": (49.8951, -97.1384),

    # Mexico (8)
    "Mexico City, Mexico": (19.4326, -99.1332),
    "Guadalajara, Mexico": (20.6596, -103.2494),
    "Monterrey, Mexico": (25.6866, -100.3161),
    "Cancún, Mexico": (21.1629, -86.8527),
    "Playa del Carmen, Mexico": (20.6296, -87.0739),
    "Puerto Vallarta, Mexico": (20.6134, -105.2542),
    "Acapulco, Mexico": (16.8634, -99.8901),
    "Merida, Mexico": (20.9674, -89.6238),

    # Central America (6)
    "San José, Costa Rica": (9.9281, -84.0907),
    "Panama City, Panama": (8.9824, -79.5199),
    "San Salvador, El Salvador": (13.6929, -89.2182),
    "Tegucigalpa, Honduras": (14.0723, -87.1921),
    "Guatemala City, Guatemala": (14.6343, -90.5069),
    "Belmopan, Belize": (17.2506, -88.7713),

    # Caribbean (6)
    "Havana, Cuba": (23.1136, -82.3666),
    "San Juan, Puerto Rico": (18.4861, -69.9312),
    "Santo Domingo, Dominican Republic": (18.4861, -69.9312),
    "Kingston, Jamaica": (17.9826, -76.8103),
    "Port-au-Prince, Haiti": (18.9712, -72.2852),
    "Bridgetown, Barbados": (13.1938, -59.5432),

    # South America (25)
    "São Paulo, Brazil": (-23.5505, -46.6333),
    "Rio de Janeiro, Brazil": (-22.9068, -43.1729),
    "Salvador, Brazil": (-12.9714, -38.5014),
    "Brasília, Brazil": (-15.7975, -47.8919),
    "Buenos Aires, Argentina": (-34.6037, -58.3816),
    "Córdoba, Argentina": (-31.4135, -64.1811),
    "Rosario, Argentina": (-32.9468, -60.6393),
    "Santiago, Chile": (-33.4489, -70.6693),
    "Valparaíso, Chile": (-33.0458, -71.6127),
    "Lima, Peru": (-12.0463, -77.0423),
    "Arequipa, Peru": (-16.3988, -71.5350),
    "Bogotá, Colombia": (4.7110, -74.0055),
    "Medellín, Colombia": (6.2442, -75.5812),
    "Caracas, Venezuela": (10.4806, -66.9036),
    "La Paz, Bolivia": (-16.2902, -63.5887),
    "Belo Horizonte, Brazil": (-19.9191, -43.9386),
    "Fortaleza, Brazil": (-3.7319, -38.5267),
    "Recife, Brazil": (-8.0476, -34.8770),
    "Manaus, Brazil": (-3.1190, -60.0217),
    "Curitiba, Brazil": (-25.4284, -49.2733),
    "Quito, Ecuador": (-0.2299, -78.5099),
    "Guayaquil, Ecuador": (-2.1896, -79.8856),
    "Asunción, Paraguay": (-25.2637, -57.5759),
    "Montevideo, Uruguay": (-34.9011, -56.1645),
    "Barranquilla, Colombia": (10.9639, -74.7964),

    # ================== ASIA (60) ==================
    # East Asia (20)
    "Tokyo, Japan": (35.6762, 139.6503),
    "Osaka, Japan": (34.6937, 135.5023),
    "Kyoto, Japan": (35.0116, 135.7681),
    "Yokohama, Japan": (35.4437, 139.6380),
    "Beijing, China": (39.9042, 116.4074),
    "Shanghai, China": (31.2304, 121.4737),
    "Guangzhou, China": (23.1291, 113.2644),
    "Chongqing, China": (29.4316, 106.9123),
    "Hong Kong, China": (22.3193, 114.1694),
    "Seoul, South Korea": (37.5665, 126.9780),
    "Busan, South Korea": (35.1796, 129.0756),
    "Taipei, Taiwan": (25.0330, 121.5654),
    "Bangkok, Thailand": (13.7563, 100.5018),
    "Ho Chi Minh City, Vietnam": (10.8231, 106.6297),
    "Hanoi, Vietnam": (21.0285, 105.8542),
    "Xi'an, China": (34.3416, 108.9398),
    "Nanjing, China": (32.0603, 118.7969),
    "Hangzhou, China": (30.2741, 120.1551),
    "Shenzhen, China": (22.5431, 114.0579),
    "Sapporo, Japan": (43.0642, 141.3469),

    # Southeast Asia (15)
    "Singapore, Singapore": (1.3521, 103.8198),
    "Manila, Philippines": (14.5995, 120.9842),
    "Davao, Philippines": (7.0731, 125.6126),
    "Kuala Lumpur, Malaysia": (3.1390, 101.6869),
    "George Town, Malaysia": (5.4164, 100.3327),
    "Jakarta, Indonesia": (-6.2088, 106.8456),
    "Surabaya, Indonesia": (-7.2575, 112.7521),
    "Yangon, Myanmar": (16.8661, 96.1951),
    "Phnom Penh, Cambodia": (11.5564, 104.9282),
    "Vientiane, Laos": (17.9757, 102.6331),
    "Cebu, Philippines": (10.3157, 123.8854),
    "Bandung, Indonesia": (-6.9175, 107.6062),
    "Penang, Malaysia": (5.3667, 100.3036),
    "Chiang Mai, Thailand": (18.7883, 98.9853),
    "Da Nang, Vietnam": (16.0544, 108.2022),

    # South Asia (12)
    "Delhi, India": (28.7041, 77.1025),
    "Mumbai, India": (19.0760, 72.8777),
    "Bangalore, India": (12.9716, 77.5946),
    "Kolkata, India": (22.5726, 88.3639),
    "Chennai, India": (13.0827, 80.2707),
    "Hyderabad, India": (17.3850, 78.4867),
    "Lahore, Pakistan": (31.5497, 74.3436),
    "Karachi, Pakistan": (24.8607, 67.0011),
    "Dhaka, Bangladesh": (23.8103, 90.4125),
    "Colombo, Sri Lanka": (6.9271, 80.7580),
    "Kathmandu, Nepal": (27.7172, 85.3240),
    "Thimphu, Bhutan": (27.5142, 89.6432),

    # Middle East (12)
    "Dubai, United Arab Emirates": (25.2048, 55.2708),
    "Abu Dhabi, United Arab Emirates": (24.4539, 54.3773),
    "Doha, Qatar": (25.2854, 51.5310),
    "Riyadh, Saudi Arabia": (24.7136, 46.6753),
    "Jeddah, Saudi Arabia": (21.5433, 39.1728),
    "Muscat, Oman": (23.6085, 58.5400),
    "Kuwait City, Kuwait": (29.3759, 47.9774),
    "Amman, Jordan": (31.9454, 35.9284),
    "Beirut, Lebanon": (33.8869, 35.4955),
    "Damascus, Syria": (33.5138, 36.2765),
    "Baghdad, Iraq": (33.3128, 44.3615),
    "Tehran, Iran": (35.6892, 51.3890),

    # Central Asia (6)
    "Almaty, Kazakhstan": (43.2380, 76.9502),
    "Astana, Kazakhstan": (51.1694, 71.4491),
    "Tashkent, Uzbekistan": (41.2995, 69.2401),
    "Samarkand, Uzbekistan": (39.6548, 66.9597),
    "Bishkek, Kyrgyzstan": (42.8746, 74.5698),
    "Dushanbe, Tajikistan": (38.5598, 68.7738),

    # ================== AFRICA (15) ==================
    "Cairo, Egypt": (30.0444, 31.2357),
    "Alexandria, Egypt": (31.2001, 29.9187),
    "Lagos, Nigeria": (6.5244, 3.3792),
    "Abuja, Nigeria": (9.0765, 7.3986),
    "Johannesburg, South Africa": (-26.2023, 28.0436),
    "Cape Town, South Africa": (-33.9249, 18.4241),
    "Nairobi, Kenya": (-1.2921, 36.8219),
    "Kampala, Uganda": (0.3476, 32.5825),
    "Dar es Salaam, Tanzania": (-6.7924, 39.2083),
    "Harare, Zimbabwe": (-17.8252, 31.0335),
    "Accra, Ghana": (5.6037, -0.1870),
    "Casablanca, Morocco": (33.5731, -7.5898),
    "Marrakesh, Morocco": (31.6295, -8.0100),
    "Dakar, Senegal": (14.6928, -17.0467),
    "Addis Ababa, Ethiopia": (9.0320, 38.7469),

    # ================== OCEANIA (15) ==================
    # Australia (8)
    "Sydney, Australia": (-33.8688, 151.2093),
    "Melbourne, Australia": (-37.8136, 144.9631),
    "Brisbane, Australia": (-27.4698, 153.0251),
    "Perth, Australia": (-31.9505, 115.8605),
    "Adelaide, Australia": (-34.9285, 138.5999),
    "Hobart, Australia": (-42.8821, 147.3272),
    "Canberra, Australia": (-35.2809, 149.1300),
    "Gold Coast, Australia": (-28.0028, 153.4314),

    # New Zealand (2)
    "Auckland, New Zealand": (-37.7870, 174.7669),
    "Wellington, New Zealand": (-41.2865, 174.7762),

    # Pacific Islands (5)
    "Honolulu, Hawaii, USA": (21.3099, -157.8581),
    "Suva, Fiji": (-18.1248, 178.4501),
    "Apia, Samoa": (-13.8330, -171.7373),
    "Nadi, Fiji": (-17.7832, 177.4474),
    "Papeete, French Polynesia": (-17.5334, -149.5671),
}

# Free geolocation API (no auth needed)
GEOLOC_API_URL = "https://ipapi.co/json/"

# ============================================================================
# CONTENT SAFETY
# ============================================================================

# Multi-language unsafe words blacklist (ROBUST)
UNSAFE_WORDS: List[str] = [
    # Death/Violence - Italian
    "morte", "morto", "morta", "muore", "uccide", "ucciso", "sangue",
    "violenza", "violento", "ferisce", "ferita", "orrore", "terrore",

    # Death/Violence - English
    "death", "dead", "dies", "died", "kill", "killed", "murder", "blood",
    "violence", "violent", "hurt", "pain", "horror", "terror",

    # Death/Violence - French
    "mort", "morte", "meurt", "tué", "tuée", "sang", "violence", "violent",
    "blessé", "horreur", "terreur",

    # Death/Violence - Spanish
    "muerte", "muerto", "muerta", "muere", "mata", "matado", "sangre",
    "violencia", "violento", "herido", "horror", "terror",

    # Fear/Negative - Italian
    "paura", "spaventoso", "mostro", "demonio", "inferno", "incubo",
    "male", "cattivo", "odio", "triste", "piange",

    # Fear/Negative - English
    "fear", "scary", "monster", "demon", "hell", "nightmare",
    "evil", "bad", "hate", "sad", "cry", "cries",

    # Fear/Negative - French
    "peur", "effrayant", "monstre", "démon", "enfer", "cauchemar",
    "mal", "mauvais", "haine", "triste", "pleure",

    # Fear/Negative - Spanish
    "miedo", "aterrador", "monstruo", "demonio", "infierno", "pesadilla",
    "malo", "mala", "odio", "triste", "llora",

    # Other inappropriate
    "stupid", "stupido", "idiot", "idiota", "ugly", "brutto",
]

# Gemini Safety Settings (STRICT for children)
GEMINI_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# ============================================================================
# INTERNATIONALIZATION (i18n)
# ============================================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "it": "Italiano",
    "fr": "Français",
    "es": "Español",
}

# UI Strings
UI_STRINGS = {
    "en": {
        "title": "🌌 Zen-IT Story",
        "subtitle": "Your personal bedtime astronomy tale",
        "location_label": "Choose your location",
        "language_label": "Language / Lingua / Langue / Idioma",
        "generate_btn": "✨ Generate Tonight's Story",
        "loading": "✨ Creating your cosmic tale...",
        "error": "Oops! The stars are shy tonight. Try again?",
        "share_whatsapp": "Share on WhatsApp",
        "share_email": "Share via Email",
        "copy_text": "Copy Story",
    },
    "it": {
        "title": "🌌 Zen-IT Story",
        "subtitle": "La tua favola astronomica della buonanotte",
        "location_label": "Scegli la tua posizione",
        "language_label": "Language / Lingua / Langue / Idioma",
        "generate_btn": "✨ Genera la Storia di Stasera",
        "loading": "✨ Creando la tua favola cosmica...",
        "error": "Ops! Le stelle sono timide stasera. Riprova?",
        "share_whatsapp": "Condividi su WhatsApp",
        "share_email": "Condividi via Email",
        "copy_text": "Copia Storia",
    },
    "fr": {
        "title": "🌌 Zen-IT Story",
        "subtitle": "Votre conte astronomique du soir",
        "location_label": "Choisissez votre position",
        "language_label": "Language / Lingua / Langue / Idioma",
        "generate_btn": "✨ Générer l'Histoire de Ce Soir",
        "loading": "✨ Création de votre conte cosmique...",
        "error": "Oups! Les étoiles sont timides ce soir. Réessayer?",
        "share_whatsapp": "Partager sur WhatsApp",
        "share_email": "Partager par Email",
        "copy_text": "Copier l'Histoire",
    },
    "es": {
        "title": "🌌 Zen-IT Story",
        "subtitle": "Tu cuento astronómico de buenas noches",
        "location_label": "Elige tu ubicación",
        "language_label": "Language / Lingua / Langue / Idioma",
        "generate_btn": "✨ Generar Historia de Esta Noche",
        "loading": "✨ Creando tu cuento cósmico...",
        "error": "¡Ups! Las estrellas son tímidas esta noche. ¿Intentar de nuevo?",
        "share_whatsapp": "Compartir en WhatsApp",
        "share_email": "Compartir por Email",
        "copy_text": "Copiar Historia",
    },
}

# ============================================================================
# STORY GENERATION SETTINGS
# ============================================================================

# Gemini model to use
GEMINI_MODEL = "gemini-2.5-flash"

# Story format template (multi-language) - SIMPLIFIED
STORY_PROMPT_TEMPLATE = """
You are a gentle storyteller creating a bedtime story for young children about a celestial object they can see tonight.

CELESTIAL OBJECT: {object_name}
TYPE: {object_type}
VISIBLE FROM: {location}
SCIENTIFIC FACTS: {scientific_facts}

TARGET LANGUAGE: {language}
CRITICAL: Write the ENTIRE story in {language} - every word, every title, everything.

STORY STRUCTURE:

Write a gentle bedtime story with these elements:

1. OPENING (2-3 sentences)
   - A child looking at the night sky
   - The celestial object begins to speak or appears magical
   - Tone: wonder, gentleness, invitation

2. MAIN STORY (3-5 paragraphs)
   - The celestial object shares its story
   - Weave in 1-2 scientific facts poetically (e.g., "I'm so big that 1,300 Earths could fit inside me")
   - Express themes: beauty of nature, connection, dreams, patience, wonder
   - The child and celestial object have a gentle dialogue or shared moment

3. CLOSING (1-2 sentences)
   - Reassuring promise: "I'll be here tomorrow night"
   - Peaceful ending for sleep

4. HAIKU (3 lines)
   - Title the section "Goodnight Haiku" (in {language})
   - Italian: 5-7-5 syllables ±1
   - Other languages: short-long-short rhythm
   - Capture the gentle emotion of the story

STYLE:
- Simple, poetic language for ages 2-8
- Calm, warm, loving tone
- NO fear, violence, sadness, or scary elements
- Natural imagery: sky, stars, light, dreams, gentle wind
- Readable in 60-90 seconds
- Like a lullaby in story form

FORMAT AS MARKDOWN:
# [Beautiful Story Title in {language}]

[Story text flowing naturally, without section headers]

### [Goodnight Haiku Title in {language}]
[haiku line 1]
[haiku line 2]
[haiku line 3]

IMPORTANT:
- Everything in {language} - no mixing languages
- Sweet, magical, reassuring
- Perfect for bedtime
"""

# Haiku syllable ranges (flexible for non-Italian)
HAIKU_SYLLABLE_RULES = {
    "it": {"line1": (4, 6), "line2": (6, 8), "line3": (4, 6)},  # Strict 5-7-5 ±1
    "en": {"line1": (4, 6), "line2": (6, 8), "line3": (4, 6)},  # Flexible
    "fr": {"line1": (4, 6), "line2": (6, 8), "line3": (4, 6)},  # Flexible
    "es": {"line1": (4, 6), "line2": (6, 8), "line3": (4, 6)},  # Flexible
}

# ============================================================================
# IMAGE SETTINGS
# ============================================================================

# Image fallback chain
IMAGE_SOURCES = {
    "hubble": "https://hubblesite.org/api/v3/images",
    "sdss": "https://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg",
    "wikimedia": "https://commons.wikimedia.org/w/api.php",
}

# Default fallback image (starfield) - Using reliable CDN
FALLBACK_IMAGE_URL = "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1200"

# ============================================================================
# NOTIFICATIONS SETTINGS (15-min reminder)
# ============================================================================

NOTIFICATION_REMINDER_MINUTES = 15
DEFAULT_BEDTIME_HOUR = 21  # 9 PM
NOTIFICATION_CHECK_INTERVAL = 300  # 5 minutes (in seconds)

# Email template
NOTIFICATION_EMAIL_TEMPLATE = """
🌙 It's almost bedtime!

Your Zen-IT Story is waiting for you tonight.

✨ Generate your personalized astronomical tale: {app_url}

Sweet dreams and clear skies! 🌟
"""

# ============================================================================
# HACKATHON METADATA
# ============================================================================

HACKATHON_TAGS = [
    "building-mcp-track-consumer",
    "mcp-in-action-track-creative",
]

PROJECT_DESCRIPTION = """
Zen-IT Story: AI-powered bedtime astronomy tales for families.
Combines real astronomical data with Gemini-generated narratives + haiku poetry.
Educational, creative, and magical! 🌌✨
"""

# ============================================================================
# ASTRONOMY DICTIONARY (Multi-language)
# ============================================================================

ASTRONOMY_DICTIONARY = {
    "en": {
        "Constellation": "A group of stars that form a pattern in the sky, like connect-the-dots with stars!",
        "Planet": "A large, round object in space that orbits (travels around) a star, like Earth does around our Sun.",
        "Star": "A giant glowing ball of hot gas that creates its own light, like our Sun!",
        "Galaxy": "A huge collection of billions of stars held together by gravity, like a family of stars.",
        "Orbit": "The path that a planet or moon takes as it travels around a star or planet.",
        "Comet": "A 'dirty snowball' of ice, rock, and dust that flies through space and sometimes grows a glowing tail!",
        "Asteroid": "A small, rocky object floating in space. Some are as tiny as pebbles, others are huge!",
        "Moon": "A rock that orbits around a planet, just like our Moon orbits Earth.",
        "Nebula": "A huge cloud of gas and dust in space where new stars are often being born!",
        "Meteor": "A piece of space rock that burns up when it enters Earth's atmosphere - we call it a 'shooting star'!",
        "Meteorite": "A space rock that lands on Earth after surviving its fall through the atmosphere.",
        "Eclipse": "When one space object's shadow falls on another, like when the Moon passes in front of the Sun.",
        "Horizon": "The line where the sky meets the Earth (or sea) on clear nights, where objects can first be seen.",
        "Aurora": "Colorful dancing lights in the sky (like the Northern Lights) caused by the Sun's energy!",
        "Equinox": "A day when day and night are equally long - happens twice a year!",
        "Solstice": "The longest or shortest day of the year, depending on the season.",
        "Light-year": "The distance light travels in one year - used to measure how far away stars are!",
        "Universe": "Everything that exists - all the stars, planets, galaxies, and empty space combined!",
    },
    "it": {
        "Costellazione": "Un gruppo di stelle che formano un motivo nel cielo, come un gioco di collegare i puntini con le stelle!",
        "Pianeta": "Un grande oggetto rotondo nello spazio che orbita (gira) attorno a una stella, come la Terra fa attorno al nostro Sole.",
        "Stella": "Una gigantesca palla di gas caldo che crea la sua propria luce, come il nostro Sole!",
        "Galassia": "Un'enorme raccolta di miliardi di stelle tenute insieme dalla gravità, come una famiglia di stelle.",
        "Orbita": "Il percorso che un pianeta o una luna segue mentre viaggia attorno a una stella o a un pianeta.",
        "Cometa": "Una 'palla di neve sporca' di ghiaccio, roccia e polvere che vola nello spazio e a volte sviluppa una coda luminosa!",
        "Asteroide": "Un piccolo oggetto roccioso che galleggia nello spazio. Alcuni sono piccoli come sassolini, altri sono giganteschi!",
        "Luna": "Una roccia che orbita attorno a un pianeta, proprio come la nostra Luna orbita la Terra.",
        "Nebulosa": "Un'enorme nuvola di gas e polvere nello spazio dove spesso nascono nuove stelle!",
        "Meteora": "Un pezzo di roccia spaziale che brucia quando entra nell'atmosfera terrestre - la chiamiamo 'stella cadente'!",
        "Meteorite": "Una roccia spaziale che atterra sulla Terra dopo aver sopravvissuto alla sua caduta attraverso l'atmosfera.",
        "Eclissi": "Quando l'ombra di un oggetto spaziale cade su un altro, come quando la Luna passa davanti al Sole.",
        "Orizzonte": "La linea dove il cielo incontra la Terra (o il mare) nelle notti serene, dove gli oggetti possono essere visti per primi.",
        "Aurora": "Luci colorate che danzano nel cielo (come l'Aurora Boreale) causate dall'energia del Sole!",
        "Equinozio": "Un giorno in cui il giorno e la notte sono ugualmente lunghi - accade due volte all'anno!",
        "Solstizio": "Il giorno più lungo o più corto dell'anno, a seconda della stagione.",
        "Anno-luce": "La distanza che la luce percorre in un anno - usata per misurare quanto lontane sono le stelle!",
        "Universo": "Tutto quello che esiste - tutte le stelle, i pianeti, le galassie e lo spazio vuoto combinati!",
    },
    "fr": {
        "Constellation": "Un groupe d'étoiles qui forment un motif dans le ciel, comme un jeu de relier les points avec des étoiles!",
        "Planète": "Un grand objet rond dans l'espace qui orbite (se déplace autour) une étoile, comme la Terre le fait autour de notre Soleil.",
        "Étoile": "Une gigantesque boule de gaz chaud qui crée sa propre lumière, comme notre Soleil!",
        "Galaxie": "Une énorme collection de milliards d'étoiles maintenues ensemble par la gravité, comme une famille d'étoiles.",
        "Orbite": "Le chemin qu'une planète ou une lune suit en voyageant autour d'une étoile ou d'une planète.",
        "Comète": "Une 'boule de neige sale' de glace, de roche et de poussière qui vole dans l'espace et développe parfois une queue brillante!",
        "Astéroïde": "Un petit objet rocheux flottant dans l'espace. Certains sont minuscules, d'autres sont gigantesques!",
        "Lune": "Une roche qui orbite autour d'une planète, tout comme notre Lune orbite la Terre.",
        "Nébuleuse": "Un immense nuage de gaz et de poussière dans l'espace où de nouvelles étoiles naissent souvent!",
        "Météore": "Un morceau de roche spatiale qui brûle en entrant dans l'atmosphère terrestre - nous l'appelons une 'étoile filante'!",
        "Météorite": "Une roche spatiale qui atterrit sur Terre après avoir survécu à sa chute à travers l'atmosphère.",
        "Éclipse": "Quand l'ombre d'un objet spatial tombe sur un autre, comme quand la Lune passe devant le Soleil.",
        "Horizon": "La ligne où le ciel rencontre la Terre (ou la mer) par nuit claire, où les objets peuvent d'abord être vus.",
        "Aurore": "Des lumières colorées qui dansent dans le ciel (comme les aurores boréales) causées par l'énergie du Soleil!",
        "Équinoxe": "Un jour où le jour et la nuit sont également longs - se produit deux fois par an!",
        "Solstice": "Le jour le plus long ou le plus court de l'année, selon la saison.",
        "Année-lumière": "La distance que la lumière parcourt en un an - utilisée pour mesurer la distance des étoiles!",
        "Univers": "Tout ce qui existe - toutes les étoiles, les planètes, les galaxies et l'espace vide combinés!",
    },
    "es": {
        "Constelación": "Un grupo de estrellas que forman un patrón en el cielo, ¡como conectar los puntos con estrellas!",
        "Planeta": "Un objeto grande y redondo en el espacio que orbita (gira alrededor de) una estrella, como la Tierra lo hace alrededor de nuestro Sol.",
        "Estrella": "Una gigantesca bola de gas caliente que crea su propia luz, ¡como nuestro Sol!",
        "Galaxia": "Una enorme colección de miles de millones de estrellas mantenidas juntas por la gravedad, ¡como una familia de estrellas!",
        "Órbita": "El camino que sigue un planeta o una luna mientras viaja alrededor de una estrella o planeta.",
        "Cometa": "Una 'bola de nieve sucia' de hielo, roca y polvo que vuela por el espacio y a veces desarrolla una cola brillante!",
        "Asteroide": "Un pequeño objeto rocoso flotando en el espacio. ¡Algunos son tan pequeños como guijarros, otros son gigantescos!",
        "Luna": "Una roca que orbita alrededor de un planeta, ¡como nuestra Luna orbita la Tierra!",
        "Nebulosa": "Una enorme nube de gas y polvo en el espacio donde a menudo nacen nuevas estrellas!",
        "Meteoror": "Un pedazo de roca espacial que se quema al entrar en la atmósfera terrestre, ¡la llamamos una 'estrella fugaz'!",
        "Meteorito": "Una roca espacial que aterriza en la Tierra después de sobrevivir su caída a través de la atmósfera.",
        "Eclipse": "Cuando la sombra de un objeto espacial cae sobre otro, como cuando la Luna pasa enfrente del Sol.",
        "Horizonte": "La línea donde el cielo se encuentra con la Tierra (o el mar) en noches claras, donde los objetos pueden verse primero.",
        "Aurora": "Luces de colores que bailan en el cielo (como las Auroras Boreales) causadas por la energía del Sol!",
        "Equinoccio": "Un día cuando el día y la noche tienen la misma duración, ¡ocurre dos veces al año!",
        "Solsticio": "El día más largo o más corto del año, dependiendo de la estación.",
        "Año-luz": "La distancia que viaja la luz en un año, ¡usada para medir qué tan lejos están las estrellas!",
        "Universo": "Todo lo que existe - ¡todas las estrellas, planetas, galaxias y espacio vacío combinados!",
    }
}

# ============================================================================
# POETIC ERROR MESSAGES (Multi-language)
# ============================================================================

POETIC_ERROR_MESSAGES = {
    "en": {
        "location_error": "The stars are being shy tonight! Please try a different location.",
        "story_generation_error": "The Moon is playing hide and seek with the story! Please try again.",
        "api_error": "A comet just flew across the servers! Let's try again in a moment.",
        "network_error": "The cosmic winds are a bit strong tonight! Please check your connection.",
        "timeout_error": "Even the fastest star needs a break! Please try again.",
        "generic_error": "The universe is having a little nap right now. Please try again soon!",
    },
    "it": {
        "location_error": "Le stelle sono timide stasera! Per favore, prova una posizione diversa.",
        "story_generation_error": "La Luna sta giocando a nascondino con la storia! Riprova.",
        "api_error": "Una cometa ha attraversato i server! Riproviamo tra un momento.",
        "network_error": "I venti cosmici sono forti stasera! Per favore, controlla la tua connessione.",
        "timeout_error": "Anche la stella più veloce ha bisogno di una pausa! Riprova.",
        "generic_error": "L'universo sta facendo un piccolo pisolino ora. Riprova presto!",
    },
    "fr": {
        "location_error": "Les étoiles sont timides ce soir! Veuillez essayer un endroit différent.",
        "story_generation_error": "La Lune joue à cache-cache avec l'histoire! Réessayez.",
        "api_error": "Une comète vient de traverser les serveurs! Réessayons dans un instant.",
        "network_error": "Les vents cosmiques sont forts ce soir! Vérifiez votre connexion.",
        "timeout_error": "Même la plus rapide des étoiles a besoin d'une pause! Réessayez.",
        "generic_error": "L'univers fait une petite sieste en ce moment. Réessayez bientôt!",
    },
    "es": {
        "location_error": "¡Las estrellas están tímidas esta noche! Por favor, intenta con una ubicación diferente.",
        "story_generation_error": "¡La Luna está jugando al escondite con la historia! Intenta de nuevo.",
        "api_error": "¡Un cometa acaba de atravesar los servidores! Intentemos de nuevo en un momento.",
        "network_error": "¡Los vientos cósmicos están fuertes esta noche! Por favor, verifica tu conexión.",
        "timeout_error": "¡Incluso la estrella más rápida necesita un descanso! Intenta de nuevo.",
        "generic_error": "¡El universo está tomando una pequeña siesta ahora! ¡Intenta de nuevo pronto!",
    }
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate critical configuration on startup"""
    errors = []

    if not GEMINI_API_KEY:
        errors.append("❌ GEMINI_API_KEY not set! Add it to environment or .env file")

    if errors:
        print("\n".join(errors))
        print("\n⚠️  Some features may not work without proper configuration.")
        print("See .env.example for required variables.\n")
    else:
        print("✅ Configuration validated successfully!")

if __name__ == "__main__":
    validate_config()
