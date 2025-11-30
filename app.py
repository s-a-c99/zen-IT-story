"""
Zen-IT Story: Final Gradio UI for MCP Hackathon 2025
AI-powered bedtime astronomy stories for families

GRADIO 6.0 COMPATIBLE VERSION
"""

import gradio as gr
import logging
import os
import urllib.parse
import json
import io
import requests
from datetime import datetime
from typing import Tuple, Optional, List, Dict
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Import our modules
from src import config
from src import astronomy_api
from src import story_generator
from src import image_fetcher
from src.mcp_server import select_celestial, get_story_prompt, generate_image_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CITY AUTOCOMPLETE DATA (60+ cities)
# ============================================================================

POPULAR_CITIES = [
    "Paris, France", "London, UK", "New York, USA", "Tokyo, Japan",
    "Roma, Italia", "Berlin, Germany", "Madrid, Spain", "Amsterdam, Netherlands",
    "Vienna, Austria", "Prague, Czech Republic", "Barcelona, Spain", "Lisbon, Portugal",
    "Athens, Greece", "Stockholm, Sweden", "Copenhagen, Denmark", "Oslo, Norway",
    "Helsinki, Finland", "Warsaw, Poland", "Budapest, Hungary", "Dublin, Ireland",
    "Brussels, Belgium", "Zurich, Switzerland", "Milan, Italy", "Munich, Germany",
    "Venice, Italy", "Florence, Italy", "Naples, Italy", "Turin, Italy",
    "Los Angeles, USA", "San Francisco, USA", "Chicago, USA", "Boston, USA",
    "Seattle, USA", "Miami, USA", "Las Vegas, USA", "Washington DC, USA",
    "Toronto, Canada", "Vancouver, Canada", "Montreal, Canada", "Sydney, Australia",
    "Melbourne, Australia", "Auckland, New Zealand", "Singapore", "Hong Kong",
    "Seoul, South Korea", "Beijing, China", "Shanghai, China", "Bangkok, Thailand",
    "Mumbai, India", "Delhi, India", "Dubai, UAE", "Tel Aviv, Israel",
    "Istanbul, Turkey", "Cairo, Egypt", "Cape Town, South Africa",
    "Buenos Aires, Argentina", "Rio de Janeiro, Brazil", "São Paulo, Brazil",
    "Mexico City, Mexico", "Lima, Peru", "Santiago, Chile"
]

LANGUAGE_FLAGS = {
    "en": "🇺🇸",
    "it": "🇮🇹",
    "fr": "🇫🇷",
    "es": "🇪🇸"
}

TRANSLATIONS = {
    "en": {
        "app_title": "Zen-IT Story 🔭",
        "subtitle": "✨ Your Personalized Astronomical Bedtime Story ✨",
        "subsubtitle": "Every night, a new star. Every star, a new story.",
        "location_label": "😊 Discover which star is above you tonight!",
        "location_placeholder": "e.g. Paris, France",
        "location_info": "e.g. Paris",
        "location_hint": "🌎 Type or select a city 📍",
        "generate_btn": "✨ Generate Tonight's Story",
        "quick_actions": "⚡ Quick Actions",
        "save_btn": "💖 Save to Favorites",
        "postcard_btn": "🎨 Create Dream Canvas",
        "waiting_title": "🌙 Click \"Generate Story\" to begin",
        "waiting_subtitle": "Every night, a new adventure among the stars awaits...",
        "tab_generate": "🏠 Generate Story",
        "tab_saved": "📚 Saved Stories",
        "tab_postcards": "🎨 Dream Canvas",
        "tab_dict": "📖 Astronomy Dictionary",
        "tab_about": "ℹ️ About",
        "footer_love": "Made with 🫶 to make sweet dreams",
        "footer_powered": "Stories by Gemini AI · Built with Claude · Hosted on Gradio & Hugging Face · Real astronomical data",
        "dict_title": "📚 Astronomy Dictionary for Little Explorers",
        "dict_intro": "✨ Learn a new word every night and become a little astronomer!",
        "saved_title": "📚 Your Saved Stories",
        "saved_intro": "✨ Your collection of cosmic bedtime tales",
        "canvas_title": "🎨 Your Dream Canvas Collection",
        "canvas_intro": "✨ Download and draw what you dreamed tonight!",
        "saved_empty": "No saved stories yet. Generate and save your first cosmic tale!",
        "postcards_empty": "No Dream Canvas created yet. Generate a story and create your printable canvas!",
        "delete_all_stories": "🗑️ Delete All Stories",
        "delete_all_canvas": "🗑️ Delete All Dream Canvas",
        "story_accordion": "📖 Your Cosmic Story",
        "generating_story": "Generating your cosmic story...",
        "tonight_sky_from": "Tonight's sky from",
        "info_location": "Location",
        "info_language": "Language",
        "info_generated": "Generated",
    },
    "it": {
        "app_title": "Zen-IT Story 🔭",
        "subtitle": "✨ La Tua Favola Astronomica Personalizzata ✨",
        "subsubtitle": "Ogni notte, una nuova stella. Ogni stella, una nuova storia.",
        "location_label": "😊 Scopri quale stella è sopra la tua testa stasera!",
        "location_placeholder": "es. Roma, Italia",
        "location_info": "es. Roma",
        "location_hint": "🌎 Scrivi o seleziona una città 📍",
        "generate_btn": "✨ Genera la Storia di Stasera",
        "quick_actions": "⚡ Azioni Rapide",
        "save_btn": "💖 Salva nei Preferiti",
        "postcard_btn": "🎨 Crea Tela dei Sogni",
        "waiting_title": "🌙 Clicca \"Genera Storia\" per iniziare",
        "waiting_subtitle": "Ogni notte, una nuova avventura tra le stelle ti aspetta...",
        "tab_generate": "🏠 Genera Storia",
        "tab_saved": "📚 Storie Salvate",
        "tab_postcards": "🎨 Tela dei Sogni",
        "tab_dict": "📖 Dizionario Astronomico",
        "tab_about": "ℹ️ Info",
        "footer_love": "Fatto con 🫶 per sogni dolci",
        "footer_powered": "Storie di Gemini AI · Costruito con Claude · Ospitato su Gradio & Hugging Face · Dati astronomici reali",
        "dict_title": "📚 Dizionario Astronomico per Piccoli Esploratori",
        "dict_intro": "✨ Impara una nuova parola ogni notte e diventa un piccolo astronomo!",
        "saved_title": "📚 Le Tue Storie Salvate",
        "saved_intro": "✨ La tua collezione di racconti cosmici della buonanotte",
        "canvas_title": "🎨 La Tua Collezione di Tele dei Sogni",
        "canvas_intro": "✨ Scarica e disegna quello che hai sognato stanotte!",
        "saved_empty": "Nessuna storia salvata. Genera e salva il tuo primo racconto cosmico!",
        "postcards_empty": "Nessuna Tela dei Sogni creata. Genera una storia e crea la tua tela stampabile!",
        "delete_all_stories": "🗑️ Cancella Tutte le Storie",
        "delete_all_canvas": "🗑️ Cancella Tutte le Tele",
        "story_accordion": "📖 La Tua Storia Cosmica",
        "generating_story": "Generando la tua storia cosmica...",
        "tonight_sky_from": "Il cielo di stasera da",
        "info_location": "Posizione",
        "info_language": "Lingua",
        "info_generated": "Generato",
    },
    "fr": {
        "app_title": "Zen-IT Story 🔭",
        "subtitle": "✨ Votre Conte Astronomique Personnalisé ✨",
        "subsubtitle": "Chaque nuit, une nouvelle étoile. Chaque étoile, une nouvelle histoire.",
        "location_label": "😊 Découvrez quelle étoile est au-dessus de vous ce soir!",
        "location_placeholder": "ex. Paris, France",
        "location_info": "ex. Paris",
        "location_hint": "🌎 Tapez ou sélectionnez une ville 📍",
        "generate_btn": "✨ Générer l'Histoire de Ce Soir",
        "quick_actions": "⚡ Actions Rapides",
        "save_btn": "💖 Sauvegarder",
        "postcard_btn": "🎨 Créer Toile de Rêves",
        "waiting_title": "🌙 Cliquez sur \"Générer Histoire\" pour commencer",
        "waiting_subtitle": "Chaque nuit, une nouvelle aventure parmi les étoiles vous attend...",
        "tab_generate": "🏠 Générer Histoire",
        "tab_saved": "📚 Histoires Sauvées",
        "tab_postcards": "🎨 Toile de Rêves",
        "tab_dict": "📖 Dictionnaire Astro",
        "tab_about": "ℹ️ À Propos",
        "footer_love": "Fait avec 🫶 pour de doux rêves",
        "footer_powered": "Histoires par Gemini AI · Construit avec Claude · Hébergé sur Gradio & Hugging Face · Données astronomiques réelles",
        "dict_title": "📚 Dictionnaire Astronomique pour Petits Explorateurs",
        "dict_intro": "✨ Apprenez un nouveau mot chaque soir et devenez un petit astronome!",
        "saved_title": "📚 Vos Histoires Sauvegardées",
        "saved_intro": "✨ Votre collection de contes cosmiques du coucher",
        "canvas_title": "🎨 Votre Collection de Toiles de Rêves",
        "canvas_intro": "✨ Téléchargez et dessinez ce dont vous avez rêvé ce soir!",
        "saved_empty": "Aucune histoire sauvegardée. Générez et sauvegardez votre premier conte cosmique!",
        "postcards_empty": "Aucune Toile de Rêves créée. Générez une histoire et créez votre toile imprimable!",
        "delete_all_stories": "🗑️ Supprimer Toutes les Histoires",
        "delete_all_canvas": "🗑️ Supprimer Toutes les Toiles",
        "story_accordion": "📖 Votre Histoire Cosmique",
        "generating_story": "Génération de votre histoire cosmique...",
        "tonight_sky_from": "Le ciel de ce soir depuis",
        "info_location": "Localisation",
        "info_language": "Langue",
        "info_generated": "Généré",
    },
    "es": {
        "app_title": "Zen-IT Story 🔭",
        "subtitle": "✨ Tu Cuento Astronómico Personalizado ✨",
        "subsubtitle": "Cada noche, una nueva estrella. Cada estrella, una nueva historia.",
        "location_label": "😊 ¡Descubre qué estrella está sobre ti esta noche!",
        "location_placeholder": "ej. Madrid, España",
        "location_info": "ej. Madrid",
        "location_hint": "🌎 Escribe o selecciona una ciudad 📍",
        "generate_btn": "✨ Generar Historia de Esta Noche",
        "quick_actions": "⚡ Acciones Rápidas",
        "save_btn": "💖 Guardar",
        "postcard_btn": "🎨 Crear Lienzo de Sueños",
        "waiting_title": "🌙 Haz clic en \"Generar Historia\" para comenzar",
        "waiting_subtitle": "Cada noche, una nueva aventura entre las estrellas te espera...",
        "tab_generate": "🏠 Generar Historia",
        "tab_saved": "📚 Historias Guardadas",
        "tab_postcards": "🎨 Lienzo de Sueños",
        "tab_dict": "📖 Diccionario Astro",
        "tab_about": "ℹ️ Acerca de",
        "footer_love": "Hecho con 🫶 para dulces sueños",
        "footer_powered": "Historias por Gemini AI · Construido con Claude · Alojado en Gradio & Hugging Face · Datos astronómicos reales",
        "dict_title": "📚 Diccionario Astronómico para Pequeños Exploradores",
        "dict_intro": "✨ ¡Aprende una nueva palabra cada noche y conviértete en un pequeño astrónomo!",
        "saved_title": "📚 Tus Historias Guardadas",
        "saved_intro": "✨ Tu colección de cuentos cósmicos antes de dormir",
        "canvas_title": "🎨 Tu Colección de Lienzos de Sueños",
        "canvas_intro": "✨ ¡Descarga y dibuja lo que soñaste esta noche!",
        "saved_empty": "No hay historias guardadas. ¡Genera y guarda tu primer cuento cósmico!",
        "postcards_empty": "No hay Lienzo de Sueños creado. ¡Genera una historia y crea tu lienzo imprimible!",
        "delete_all_stories": "🗑️ Eliminar Todas las Historias",
        "delete_all_canvas": "🗑️ Eliminar Todos los Lienzos",
        "story_accordion": "📖 Tu Historia Cósmica",
        "generating_story": "Generando tu historia cósmica...",
        "tonight_sky_from": "El cielo de esta noche desde",
        "info_location": "Ubicación",
        "info_language": "Idioma",
        "info_generated": "Generado",
    }
}

DICTIONARY_TERMS = {
    "en": [
        {"emoji": "⭐", "title": "Star", "description": "A giant ball of hot gas that shines with its own light, just like our Sun!", "color": "yellow-400"},
        {"emoji": "🪐", "title": "Planet", "description": "A large round object in space that orbits around a star, like Earth orbits the Sun.", "color": "pink-400"},
        {"emoji": "🌌", "title": "Galaxy", "description": "A huge collection of billions of stars, planets, and space dust held together by gravity.", "color": "purple-400"},
        {"emoji": "🌙", "title": "Moon", "description": "A natural satellite that orbits a planet, like our Moon that lights up the night sky.", "color": "blue-400"},
        {"emoji": "☄️", "title": "Comet", "description": "A ball of ice and space dust that creates a beautiful tail when it gets close to the Sun.", "color": "green-400"},
        {"emoji": "🌟", "title": "Constellation", "description": "A group of stars that form a recognizable pattern in the sky, like a cosmic connect-the-dots!", "color": "indigo-400"},
        {"emoji": "💫", "title": "Light Year", "description": "The distance light travels in one year: about 9.46 trillion kilometers!", "color": "red-400"},
        {"emoji": "🔭", "title": "Telescope", "description": "An instrument that allows us to see objects very far away in space, like stars and galaxies.", "color": "orange-400"},
        {"emoji": "🌠", "title": "Shooting Star", "description": "Not actually a star! It's a small piece of space rock burning up in Earth's atmosphere.", "color": "cyan-400"},
        {"emoji": "🌑", "title": "Eclipse", "description": "When one celestial body passes in front of another and covers it, like when the Moon covers the Sun.", "color": "gray-400"},
        {"emoji": "🪨", "title": "Asteroid", "description": "A rocky object that orbits the Sun, smaller than a planet but bigger than a pebble!", "color": "amber-400"},
        {"emoji": "💥", "title": "Supernova", "description": "The giant explosion of a star at the end of its life, an incredible cosmic spectacle!", "color": "rose-400"},
        {"emoji": "🌌", "title": "Milky Way", "description": "Our galaxy! It contains our Solar System and about 200 billion stars.", "color": "violet-400"},
        {"emoji": "☀️", "title": "Solar System", "description": "The Sun and everything that orbits around it: planets, moons, asteroids, and comets.", "color": "yellow-500"},
        {"emoji": "🛰️", "title": "Satellite", "description": "An object that orbits a planet. Can be natural (like the Moon) or human-made!", "color": "sky-400"},
        {"emoji": "🌫️", "title": "Nebula", "description": "A colorful cloud of gas and dust in space where new stars are born.", "color": "fuchsia-400"},
        {"emoji": "⚫", "title": "Black Hole", "description": "A point in space with gravity so strong that not even light can escape!", "color": "slate-400"},
        {"emoji": "🔄", "title": "Orbit", "description": "The path an object takes while moving around another in space, like the Moon around Earth.", "color": "teal-400"}
    ],
    "it": [
        {"emoji": "⭐", "title": "Stella", "description": "Una gigantesca palla di gas caldo che brilla di luce propria, proprio come il nostro Sole!", "color": "yellow-400"},
        {"emoji": "🪐", "title": "Pianeta", "description": "Un grande oggetto rotondo nello spazio che orbita attorno a una stella, come la Terra orbita il Sole.", "color": "pink-400"},
        {"emoji": "🌌", "title": "Galassia", "description": "Un'enorme collezione di miliardi di stelle, pianeti e polvere spaziale tenuti insieme dalla gravità.", "color": "purple-400"},
        {"emoji": "🌙", "title": "Luna", "description": "Un satellite naturale che orbita un pianeta, come la nostra Luna che illumina il cielo notturno.", "color": "blue-400"},
        {"emoji": "☄️", "title": "Cometa", "description": "Una palla di ghiaccio e polvere spaziale che crea una bellissima coda quando si avvicina al Sole.", "color": "green-400"},
        {"emoji": "🌟", "title": "Costellazione", "description": "Un gruppo di stelle che formano un disegno riconoscibile nel cielo, come un unisci-i-puntini cosmico!", "color": "indigo-400"},
        {"emoji": "💫", "title": "Anno Luce", "description": "La distanza che la luce percorre in un anno: circa 9,46 trilioni di chilometri!", "color": "red-400"},
        {"emoji": "🔭", "title": "Telescopio", "description": "Uno strumento che ci permette di vedere oggetti molto lontani nello spazio, come stelle e galassie.", "color": "orange-400"},
        {"emoji": "🌠", "title": "Stella Cadente", "description": "Non è veramente una stella! È un piccolo pezzo di roccia spaziale che brucia nell'atmosfera terrestre.", "color": "cyan-400"},
        {"emoji": "🌑", "title": "Eclissi", "description": "Quando un corpo celeste passa davanti a un altro e lo copre, come quando la Luna copre il Sole.", "color": "gray-400"},
        {"emoji": "🪨", "title": "Asteroide", "description": "Un oggetto roccioso che orbita il Sole, più piccolo di un pianeta ma più grande di un sassolino!", "color": "amber-400"},
        {"emoji": "💥", "title": "Supernova", "description": "L'esplosione gigantesca di una stella alla fine della sua vita, uno spettacolo cosmico incredibile!", "color": "rose-400"},
        {"emoji": "🌌", "title": "Via Lattea", "description": "La nostra galassia! Contiene il nostro Sistema Solare e circa 200 miliardi di stelle.", "color": "violet-400"},
        {"emoji": "☀️", "title": "Sistema Solare", "description": "Il Sole e tutto ciò che gli orbita attorno: pianeti, lune, asteroidi e comete.", "color": "yellow-500"},
        {"emoji": "🛰️", "title": "Satellite", "description": "Un oggetto che orbita attorno a un pianeta. Può essere naturale (come la Luna) o artificiale!", "color": "sky-400"},
        {"emoji": "🌫️", "title": "Nebulosa", "description": "Una nuvola colorata di gas e polvere nello spazio dove nascono nuove stelle.", "color": "fuchsia-400"},
        {"emoji": "⚫", "title": "Buco Nero", "description": "Un punto nello spazio con gravità così forte che nemmeno la luce può sfuggire!", "color": "slate-400"},
        {"emoji": "🔄", "title": "Orbita", "description": "Il percorso che un oggetto compie mentre gira attorno a un altro nello spazio, come la Luna intorno alla Terra.", "color": "teal-400"}
    ],
    "fr": [
        {"emoji": "⭐", "title": "Étoile", "description": "Une boule géante de gaz chaud qui brille de sa propre lumière, comme notre Soleil!", "color": "yellow-400"},
        {"emoji": "🪐", "title": "Planète", "description": "Un grand objet rond dans l'espace qui orbite autour d'une étoile, comme la Terre orbite le Soleil.", "color": "pink-400"},
        {"emoji": "🌌", "title": "Galaxie", "description": "Une énorme collection de milliards d'étoiles, de planètes et de poussière spatiale maintenues ensemble par la gravité.", "color": "purple-400"},
        {"emoji": "🌙", "title": "Lune", "description": "Un satellite naturel qui orbite une planète, comme notre Lune qui éclaire le ciel nocturne.", "color": "blue-400"},
        {"emoji": "☄️", "title": "Comète", "description": "Une boule de glace et de poussière spatiale qui crée une belle queue quand elle s'approche du Soleil.", "color": "green-400"},
        {"emoji": "🌟", "title": "Constellation", "description": "Un groupe d'étoiles qui forment un motif reconnaissable dans le ciel, comme un jeu de points à relier cosmique!", "color": "indigo-400"},
        {"emoji": "💫", "title": "Année-Lumière", "description": "La distance que la lumière parcourt en un an: environ 9,46 billions de kilomètres!", "color": "red-400"},
        {"emoji": "🔭", "title": "Télescope", "description": "Un instrument qui nous permet de voir des objets très éloignés dans l'espace, comme les étoiles et les galaxies.", "color": "orange-400"},
        {"emoji": "🌠", "title": "Étoile Filante", "description": "Ce n'est pas vraiment une étoile! C'est un petit morceau de roche spatiale qui brûle dans l'atmosphère terrestre.", "color": "cyan-400"},
        {"emoji": "🌑", "title": "Éclipse", "description": "Quand un corps céleste passe devant un autre et le couvre, comme quand la Lune couvre le Soleil.", "color": "gray-400"},
        {"emoji": "🪨", "title": "Astéroïde", "description": "Un objet rocheux qui orbite le Soleil, plus petit qu'une planète mais plus grand qu'un caillou!", "color": "amber-400"},
        {"emoji": "💥", "title": "Supernova", "description": "L'explosion géante d'une étoile à la fin de sa vie, un spectacle cosmique incroyable!", "color": "rose-400"},
        {"emoji": "🌌", "title": "Voie Lactée", "description": "Notre galaxie! Elle contient notre Système Solaire et environ 200 milliards d'étoiles.", "color": "violet-400"},
        {"emoji": "☀️", "title": "Système Solaire", "description": "Le Soleil et tout ce qui orbite autour de lui: planètes, lunes, astéroïdes et comètes.", "color": "yellow-500"},
        {"emoji": "🛰️", "title": "Satellite", "description": "Un objet qui orbite une planète. Peut être naturel (comme la Lune) ou artificiel!", "color": "sky-400"},
        {"emoji": "🌫️", "title": "Nébuleuse", "description": "Un nuage coloré de gaz et de poussière dans l'espace où naissent de nouvelles étoiles.", "color": "fuchsia-400"},
        {"emoji": "⚫", "title": "Trou Noir", "description": "Un point dans l'espace avec une gravité si forte que même la lumière ne peut pas s'échapper!", "color": "slate-400"},
        {"emoji": "🔄", "title": "Orbite", "description": "Le chemin qu'un objet prend en se déplaçant autour d'un autre dans l'espace, comme la Lune autour de la Terre.", "color": "teal-400"}
    ],
    "es": [
        {"emoji": "⭐", "title": "Estrella", "description": "¡Una bola gigante de gas caliente que brilla con su propia luz, como nuestro Sol!", "color": "yellow-400"},
        {"emoji": "🪐", "title": "Planeta", "description": "Un gran objeto redondo en el espacio que orbita alrededor de una estrella, como la Tierra orbita el Sol.", "color": "pink-400"},
        {"emoji": "🌌", "title": "Galaxia", "description": "Una enorme colección de miles de millones de estrellas, planetas y polvo espacial unidos por la gravedad.", "color": "purple-400"},
        {"emoji": "🌙", "title": "Luna", "description": "Un satélite natural que orbita un planeta, como nuestra Luna que ilumina el cielo nocturno.", "color": "blue-400"},
        {"emoji": "☄️", "title": "Cometa", "description": "Una bola de hielo y polvo espacial que crea una hermosa cola cuando se acerca al Sol.", "color": "green-400"},
        {"emoji": "🌟", "title": "Constelación", "description": "¡Un grupo de estrellas que forman un patrón reconocible en el cielo, como un juego cósmico de conectar los puntos!", "color": "indigo-400"},
        {"emoji": "💫", "title": "Año Luz", "description": "¡La distancia que la luz viaja en un año: aproximadamente 9.46 billones de kilómetros!", "color": "red-400"},
        {"emoji": "🔭", "title": "Telescopio", "description": "Un instrumento que nos permite ver objetos muy lejanos en el espacio, como estrellas y galaxias.", "color": "orange-400"},
        {"emoji": "🌠", "title": "Estrella Fugaz", "description": "¡No es realmente una estrella! Es un pequeño trozo de roca espacial que se quema en la atmósfera terrestre.", "color": "cyan-400"},
        {"emoji": "🌑", "title": "Eclipse", "description": "Cuando un cuerpo celeste pasa frente a otro y lo cubre, como cuando la Luna cubre el Sol.", "color": "gray-400"},
        {"emoji": "🪨", "title": "Asteroide", "description": "¡Un objeto rocoso que orbita el Sol, más pequeño que un planeta pero más grande que una piedra!", "color": "amber-400"},
        {"emoji": "💥", "title": "Supernova", "description": "¡La explosión gigante de una estrella al final de su vida, un espectáculo cósmico increíble!", "color": "rose-400"},
        {"emoji": "🌌", "title": "Vía Láctea", "description": "¡Nuestra galaxia! Contiene nuestro Sistema Solar y unos 200 mil millones de estrellas.", "color": "violet-400"},
        {"emoji": "☀️", "title": "Sistema Solar", "description": "El Sol y todo lo que orbita a su alrededor: planetas, lunas, asteroides y cometas.", "color": "yellow-500"},
        {"emoji": "🛰️", "title": "Satélite", "description": "Un objeto que orbita un planeta. ¡Puede ser natural (como la Luna) o hecho por humanos!", "color": "sky-400"},
        {"emoji": "🌫️", "title": "Nebulosa", "description": "Una nube colorida de gas y polvo en el espacio donde nacen nuevas estrellas.", "color": "fuchsia-400"},
        {"emoji": "⚫", "title": "Agujero Negro", "description": "¡Un punto en el espacio con gravedad tan fuerte que ni siquiera la luz puede escapar!", "color": "slate-400"},
        {"emoji": "🔄", "title": "Órbita", "description": "El camino que toma un objeto mientras se mueve alrededor de otro en el espacio, como la Luna alrededor de la Tierra.", "color": "teal-400"}
    ]
}

ABOUT_CONTENT = {
    "en": {
        "mission_title": "🌟 Our Mission",
        "mission_text": "Zen-IT Story transforms the night sky into magical bedtime stories. We believe every child deserves to fall asleep with wonder in their hearts.",
        "how_title": "🔮 How It Works",
        "how_steps": [
            "📍 Enter your city to find what's in YOUR sky tonight",
            "⭐ We identify the brightest star or planet visible above you",
            "✨ AI creates a personalized bedtime tale about that celestial friend",
        ],
        "features_title": "✨ Features",
        "features": [
            "🌍 Location-based astronomy",
            "🤖 AI-generated stories by Google Gemini",
            "🌟 Authentic astronomical data",
        ],
        "perfect_title": "🎯 Perfect for",
        "perfect_for": [
            "🛏️ Bedtime routines with children",
            "🔭 Astronomy education made magical",
            "👨‍👩‍👧 Family bonding moments",
        ]
    },
    "it": {
        "mission_title": "🌟 La Nostra Missione",
        "mission_text": "Zen-IT Story trasforma il cielo notturno in magiche storie della buonanotte.",
        "how_title": "🔮 Come Funziona",
        "how_steps": [
            "📍 Inserisci la tua città per scoprire cosa c'è nel TUO cielo stasera",
            "⭐ Identifichiamo la stella o il pianeta più luminoso sopra di te",
            "✨ L'IA crea un racconto personalizzato su quell'amico celeste",
        ],
        "features_title": "✨ Funzionalità",
        "features": [
            "🌍 Astronomia basata sulla posizione",
            "🤖 Storie generate dall'IA con Google Gemini",
            "🌟 Dati astronomici autentici",
        ],
        "perfect_title": "🎯 Perfetto per",
        "perfect_for": [
            "🛏️ Routine della buonanotte con i bambini",
            "🔭 Educazione astronomica resa magica",
            "👨‍👩‍👧 Momenti di legame familiare",
        ]
    },
    "fr": {
        "mission_title": "🌟 Notre Mission",
        "mission_text": "Zen-IT Story transforme le ciel nocturne en histoires magiques du coucher.",
        "how_title": "🔮 Comment Ça Marche",
        "how_steps": [
            "📍 Entrez votre ville pour découvrir ce qu'il y a dans VOTRE ciel ce soir",
            "⭐ Nous identifions l'étoile ou la planète la plus brillante au-dessus de vous",
            "✨ L'IA crée un conte personnalisé sur cet ami céleste",
        ],
        "features_title": "✨ Fonctionnalités",
        "features": [
            "🌍 Astronomie basée sur la localisation",
            "🤖 Histoires générées par l'IA avec Google Gemini",
            "🌟 Données astronomiques authentiques",
        ],
        "perfect_title": "🎯 Parfait pour",
        "perfect_for": [
            "🛏️ Routines du coucher avec les enfants",
            "🔭 Éducation astronomique rendue magique",
            "👨‍👩‍👧 Moments de liens familiaux",
        ]
    },
    "es": {
        "mission_title": "🌟 Nuestra Misión",
        "mission_text": "Zen-IT Story transforma el cielo nocturno en mágicas historias para dormir.",
        "how_title": "🔮 Cómo Funciona",
        "how_steps": [
            "📍 Ingresa tu ciudad para descubrir qué hay en TU cielo esta noche",
            "⭐ Identificamos la estrella o planeta más brillante sobre ti",
            "✨ La IA crea un cuento personalizado sobre ese amigo celestial",
        ],
        "features_title": "✨ Características",
        "features": [
            "🌍 Astronomía basada en ubicación",
            "🤖 Historias generadas por IA con Google Gemini",
            "🌟 Datos astronómicos auténticos",
        ],
        "perfect_title": "🎯 Perfecto para",
        "perfect_for": [
            "🛏️ Rutinas de dormir con niños",
            "🔭 Educación astronómica hecha mágica",
            "👨‍👩‍👧 Momentos de unión familiar",
        ]
    }
}

CUSTOM_CSS = """
/* ============================================================================
   ZEN-IT STORY - CUSTOM CSS COMPLETO
   Font Fredoka + Sfondo Stellato + Breathe Aurora + Tutte le modifiche
   ============================================================================ */

/* === FONT IMPORT === */
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');

/* === CSS VARIABLES === */
:root {
    --arctic: #0b0b14;
    --polar: #162447;
    --aurora-green: #3dffa2;
    --aurora-teal: #2dd4bf;
    --aurora-purple: #a78bfa;
    --aurora-pink: #f472b6;
    --snow: #f1f5f9;
    --ice: #94a3b8;
    --gold: #fbbf24;
}

/* === SFONDO STELLATO ANIMATO === */
.gradio-container {
    position: relative;
    background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%) !important;
    font-family: 'Fredoka', sans-serif !important;
    color: var(--snow) !important;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Stelle fisse e lampeggianti */
.gradio-container::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
        radial-gradient(2px 2px at 20px 30px, white, transparent),
        radial-gradient(2px 2px at 60px 70px, white, transparent),
        radial-gradient(1px 1px at 50px 50px, white, transparent),
        radial-gradient(1px 1px at 130px 80px, white, transparent),
        radial-gradient(2px 2px at 90px 10px, white, transparent),
        radial-gradient(1px 1px at 200px 150px, white, transparent),
        radial-gradient(1px 1px at 300px 50px, white, transparent),
        radial-gradient(2px 2px at 250px 200px, white, transparent),
        radial-gradient(1px 1px at 400px 30px, white, transparent),
        radial-gradient(1px 1px at 180px 180px, white, transparent);
    background-size: 450px 300px;
    background-repeat: repeat;
    opacity: 0.5;
    animation: twinkle-stars 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes twinkle-stars {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.8; }
}

/* Rotazione lenta del cielo */
.gradio-container::after {
    content: "";
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, transparent 20%, #0b0b14 80%);
    animation: rotate-sky 300s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes rotate-sky {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Ensure content is above stars */
.gradio-container > * {
    position: relative;
    z-index: 1;
}

/* === TITOLO BREATHE AURORA === */
.app-title {
    font-family: 'Fredoka', sans-serif !important;
    font-size: 5.5rem !important;  /* Ingrandito 1.5x */
    font-weight: 700 !important;
    text-align: center !important;
    letter-spacing: -0.5px;
    margin: 40px 0 20px 0 !important;

    /* Aurora Gradient Sobrio */
    background: linear-gradient(
        120deg,
        #94a3b8,
        #3dffa2,
        #2dd4bf,
        #a78bfa,
        #94a3b8
    );
    background-size: 200% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;

    /* Animazioni */
    animation:
        aurora-breathe 5s ease-in-out infinite,
        gentle-opacity 8s ease-in-out infinite;
}

/* Emoji nel titolo */
.app-title .emoji {
    -webkit-text-fill-color: #94a3b8 !important;
    background: none !important;
    opacity: 0.7;
    font-size: 0.9em;
    margin-left: 0.2em;
}

/* Aurora Gradient lento e fluido */
@keyframes aurora-breathe {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Breathe - opacità che respira */
@keyframes gentle-opacity {
    0%, 100% { opacity: 0.85; }
    50% { opacity: 1; }
}

/* === SOTTOTITOLI === */
.subtitle {
    text-align: center !important;
    color: var(--gold) !important;
    font-size: 1.95rem !important;  /* 1.3rem * 1.5 */
    font-weight: 600 !important;
    margin-bottom: 10px !important;
}

.subsubtitle {
    text-align: center !important;
    color: var(--ice) !important;
    font-size: 1.65rem !important;  /* 1.1rem * 1.5 */
    font-style: italic !important;
    margin-bottom: 30px !important;
}

/* === BANDIERE LINGUE === */
.lang-flags {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 30px;
}

.lang-flags button {
    font-size: 2.5rem !important;  /* Ingrandito */
    background: transparent !important;
    border: 2px solid transparent !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

.lang-flags button:hover {
    background: rgba(61, 255, 162, 0.1) !important;
    border-color: var(--aurora-green) !important;
    transform: scale(1.1);
}

/* === MENU TABS INGRANDITO === */
.tabs button {
    font-size: 1.5rem !important;  /* Reduced to fit all tabs */
    padding: 16px 28px !important;  /* Reduced padding */
    font-weight: 600 !important;
    border-radius: 12px 12px 0 0 !important;
    transition: all 0.3s ease !important;
}

.tabs button[aria-selected="true"] {
    background: rgba(61, 255, 162, 0.2) !important;
    border-bottom: 3px solid var(--aurora-green) !important;
}

/* === INPUT PANEL === */
.input-panel {
    background: rgba(22, 36, 71, 0.7) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    border: 1px solid rgba(61, 255, 162, 0.3) !important;
    backdrop-filter: blur(15px) !important;
    box-shadow: 0 10px 40px rgba(61, 255, 162, 0.15) !important;
}

.location-label {
    font-size: 1.95rem !important;  /* 1.3rem * 1.5 */
    font-weight: 700 !important;
    color: var(--snow) !important;
    text-align: center !important;
    margin-bottom: 15px !important;
}

/* === FIX DROPDOWN CITTÀ (POSITIONING STABLE) === */
.location-input {
    position: relative !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

/* Dropdown container wrapper */
.location-input > div {
    position: relative !important;
}

/* Dropdown label */
.location-input label {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin-bottom: 8px !important;
    display: block !important;
}

/* Dropdown info text */
.location-input .info {
    font-size: 1.5rem !important;
    margin-top: 4px !important;
    margin-left: 8px !important;
    display: block !important;
}

/* UNIFIED AUTOCOMPLETE FIELD - Single dropdown that acts as textbox + autocomplete */
.location-input-unified {
    position: relative !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

.location-input-unified input {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 2px solid rgba(255, 215, 0, 0.5) !important;
    border-radius: 15px !important;
    color: #F8F9FA !important;
    font-size: 1.15em !important;
    padding: 18px !important;
    transition: all 0.3s ease;
    width: 100% !important;
    box-sizing: border-box !important;
}

.location-input-unified input:focus {
    border-color: #FFD700 !important;
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.4) !important;
    background: rgba(255, 255, 255, 0.12) !important;
    outline: none !important;
}

/* Info text below dropdown */
.location-input-unified .info {
    color: rgba(255, 215, 0, 0.7) !important;
    font-size: 0.85em !important;
    margin-top: 8px !important;
    font-style: italic !important;
}

/* Dropdown options container */
.svelte-1gfkn6j, .svelte-1gfkn6j ul {
    max-height: 300px !important;
    overflow-y: auto !important;
    font-size: 1.1em !important;
    position: absolute !important;
    width: 100% !important;
    z-index: 1000 !important;
    background: rgba(26, 31, 58, 0.98) !important;
    border: 2px solid rgba(255, 215, 0, 0.5) !important;
    border-radius: 15px !important;
    margin-top: 4px !important;
}

/* === FIX DROPDOWN GRADIO 6.0 - OVERFLOW & Z-INDEX === */
.gradio-container,
.input-panel,
.block,
.form,
.contain {
    overflow: visible !important;
}

.location-input ul[role="listbox"],
.location-input [data-testid="dropdown-options"] {
    z-index: 99999 !important;
    position: absolute !important;
}

.input-panel {
    contain: none !important;
}

/* === BOTTONI === */
.generate-btn {
    background: linear-gradient(135deg, var(--aurora-green) 0%, var(--aurora-teal) 100%) !important;
    border: none !important;
    border-radius: 15px !important;
    padding: 22px 50px !important;  /* Ingrandito */
    font-size: 1.95rem !important;  /* 1.3rem * 1.5 */
    font-weight: 800 !important;
    color: var(--arctic) !important;
    width: 100% !important;
    margin-top: 20px !important;
    box-shadow: 0 8px 25px rgba(61, 255, 162, 0.4) !important;
    transition: all 0.3s ease !important;
}

.generate-btn:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 35px rgba(61, 255, 162, 0.5) !important;
}

.save-btn {
    background: linear-gradient(135deg, var(--aurora-pink) 0%, var(--aurora-purple) 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 15px 30px !important;
    font-size: 1.5rem !important;  /* 1rem * 1.5 */
    width: 100% !important;
    margin: 8px 0 !important;
    transition: all 0.3s ease !important;
}

.save-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(244, 114, 182, 0.4) !important;
}

.postcard-btn {
    background: linear-gradient(135deg, var(--aurora-purple) 0%, #6366f1 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 15px 30px !important;
    font-size: 1.5rem !important;  /* 1rem * 1.5 */
    width: 100% !important;
    margin: 8px 0 !important;
    transition: all 0.3s ease !important;
}

.postcard-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(167, 139, 250, 0.4) !important;
}

/* === WAITING CONTAINER === */
.waiting-container {
    text-align: center;
    padding: 80px 50px;  /* Ingrandito */
    background: rgba(22, 36, 71, 0.5);
    border-radius: 20px;
    border: 1px dashed rgba(61, 255, 162, 0.3);
    backdrop-filter: blur(10px);
}

.waiting-icon {
    font-size: 6rem !important;  /* 4rem * 1.5 */
    margin-bottom: 30px;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-15px); }
}

.waiting-title {
    font-size: 2.4rem !important;  /* 1.6rem * 1.5 */
    color: var(--gold);
    font-weight: 700;
    margin-bottom: 15px;
}

.waiting-subtitle {
    font-size: 1.65rem !important;  /* 1.1rem * 1.5 */
    color: var(--ice);
    font-style: italic;
}

/* === STORY CONTENT === */
.story-content {
    background: rgba(22, 36, 71, 0.6) !important;
    border-radius: 20px !important;
    padding: 40px !important;
    border: 1px solid rgba(61, 255, 162, 0.2) !important;
    backdrop-filter: blur(15px) !important;
    font-size: 1.5rem !important;  /* 1rem * 1.5 */
    line-height: 1.8 !important;
}

.story-content h1 {
    font-size: 3.75rem !important;  /* 2.5rem * 1.5 */
}

.story-content h2 {
    font-size: 2.85rem !important;  /* 1.9rem * 1.5 */
}

.story-content h3 {
    font-size: 2.25rem !important;  /* 1.5rem * 1.5 */
}

.story-content p {
    font-size: 1.65rem !important;  /* 1.1rem * 1.5 */
    line-height: 2rem !important;
    margin-bottom: 20px !important;
}

/* === DIZIONARIO CON BOX COLORATE === */
.dictionary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
}

.dictionary-term {
    background: linear-gradient(135deg, rgba(22, 36, 71, 0.8) 0%, rgba(30, 27, 75, 0.8) 100%);
    border-radius: 16px;
    padding: 24px;
    border: 2px solid;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.dictionary-term:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.dictionary-term .emoji {
    font-size: 3rem;
    display: block;
    margin-bottom: 12px;
}

.dictionary-term .title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.dictionary-term .description {
    font-size: 1.3rem;
    line-height: 1.6;
    color: #e2e8f0;
}

/* Colori bordo per ogni termine */
.term-yellow-400 { border-color: #fbbf24; }
.term-pink-400 { border-color: #f472b6; }
.term-purple-400 { border-color: #c084fc; }
.term-blue-400 { border-color: #60a5fa; }
.term-green-400 { border-color: #4ade80; }
.term-indigo-400 { border-color: #818cf8; }
.term-red-400 { border-color: #f87171; }
.term-orange-400 { border-color: #fb923c; }
.term-cyan-400 { border-color: #22d3ee; }
.term-gray-400 { border-color: #9ca3af; }
.term-amber-400 { border-color: #fbbf24; }
.term-rose-400 { border-color: #fb7185; }
.term-violet-400 { border-color: #a78bfa; }
.term-yellow-500 { border-color: #eab308; }
.term-sky-400 { border-color: #38bdf8; }
.term-fuchsia-400 { border-color: #e879f9; }
.term-slate-400 { border-color: #94a3b8; }
.term-teal-400 { border-color: #2dd4bf; }

/* === FOOTER === */
.footer {
    text-align: center;
    padding: 50px 30px;
    margin-top: 60px;
    border-top: 1px solid rgba(61, 255, 162, 0.2);
}

.footer-love {
    font-size: 2.25rem !important;  /* 1.5rem * 1.5 */
    font-weight: 700;
    color: var(--gold);
    margin-bottom: 20px;
    animation: sparkle 3s ease-in-out infinite;
}

@keyframes sparkle {
    0%, 100% { text-shadow: 0 0 10px rgba(251, 191, 36, 0.5); }
    50% { text-shadow: 0 0 20px rgba(251, 191, 36, 0.8), 0 0 30px rgba(251, 191, 36, 0.4); }
}

.footer-powered {
    font-size: 1.35rem !important;  /* 0.9rem * 1.5 */
    color: var(--ice);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
    .app-title { font-size: 3.5rem !important; }
    .subtitle { font-size: 1.5rem !important; }
    .subsubtitle { font-size: 1.3rem !important; }
    .tabs button { font-size: 1.4rem !important; padding: 15px 25px !important; }
    .dictionary-grid { grid-template-columns: 1fr; }
}
"""


def generate_story_flow_with_logs(location: str, language: str):
    """
    Main story generation workflow with streaming MCP activity logs.
    Yields progress updates for UI display.
    """
    from datetime import datetime as dt

    def make_log(icon: str, message: str) -> str:
        timestamp = dt.now().strftime("%H:%M:%S")
        return f"{timestamp} {icon} {message}"

    logs = []

    try:
        # Step 1: Parse location
        logs.append(make_log("🔍", f"Parsing location input: '{location}'"))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        lat, lon, city_name = astronomy_api.parse_location_input(location)

        if lat is None or lon is None:
            logs.append(make_log("⚠️", "Location parsing failed, trying auto-geolocation..."))
            yield {"logs": "\n".join(logs), "complete": False, "result": None}

            geo_data = astronomy_api.get_user_location_from_ip()

            if geo_data["error"]:
                logs.append(make_log("❌", f"Geolocation failed: {geo_data['error']}"))
                yield {"logs": "\n".join(logs), "complete": False, "result": None, "error": True}
                return

            lat = geo_data["latitude"]
            lon = geo_data["longitude"]
            city_name = f"{geo_data['city']}, {geo_data['country']}"
            logs.append(make_log("✅", f"Auto-located: {city_name}"))
            yield {"logs": "\n".join(logs), "complete": False, "result": None}

        logs.append(make_log("🌍", f"Coordinates: {lat:.1f}°N, {lon:.1f}°E"))
        logs.append(make_log("📍", f"Location: {city_name}"))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        # Step 2: MCP Tool - select_celestial
        today = datetime.now().strftime("%Y-%m-%d")
        logs.append(make_log("🔧", f"MCP Tool: select_celestial(lat={lat:.1f}, lon={lon:.1f}, date={today})"))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        celestial_object = select_celestial(lat, lon, today)

        object_name = celestial_object["object_name"]
        object_type = celestial_object["type"]
        magnitude = celestial_object.get("magnitude", "N/A")
        logs.append(make_log("⭐", f"MCP Response: {object_name} ({object_type}, magnitude {magnitude})"))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        # Step 3: Generate story with Gemini
        scientific_facts = celestial_object.get("description", "A beautiful celestial object")
        logs.append(make_log("🤖", f"Calling Gemini 2.5 Flash API (language: {language})..."))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        story_result = story_generator.generate_story(
            object_name=object_name,
            object_type=object_type,
            location=city_name,
            scientific_facts=scientific_facts,
            language=language
        )

        if not story_result["success"]:
            logs.append(make_log("❌", f"Story generation failed: {story_result.get('error')}"))
            yield {"logs": "\n".join(logs), "complete": False, "result": None, "error": True}
            return

        story_len = len(story_result.get("story", ""))
        logs.append(make_log("📖", f"Story generated successfully ({story_len} characters)"))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        # Step 4: Fetch image
        logs.append(make_log("🖼️", f"Fetching image for {object_name}..."))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        image_result = image_fetcher.get_image_for_object(object_name, celestial_object)
        image_url = image_result["url"]
        image_source = image_result['source']

        if image_source == "fallback":
            logs.append(make_log("⚠️", "Using fallback image (APIs unavailable)"))
        else:
            logs.append(make_log("✅", f"Image fetched from {image_source}"))
        yield {"logs": "\n".join(logs), "complete": False, "result": None}

        # Step 5: Format output with enhanced styling (HTML)
        from datetime import datetime as dt
        story_html = story_generator.format_story_for_display(story_result, language)

        # Get translations for current language
        trans = TRANSLATIONS.get(language, TRANSLATIONS["en"])

        # Location display as HTML
        location_html = f"""
<div style='background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); padding: 16px 24px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #fbbf24;'>
    <p style='margin: 0; color: #fbbf24; font-size: 1.1em;'>📍 {trans['tonight_sky_from']} <strong>{city_name}</strong> <span style='color: #a0aec0;'>({lat:.1f} N, {lon:.1f} W)</span></p>
</div>
"""

        # Generate fun facts section as HTML
        fun_facts = story_generator.generate_fun_facts(object_name, object_type, language)
        did_you_know_title = {
            "en": "💡 Did You Know?",
            "it": "💡 Lo Sapevi?",
            "fr": "💡 Le Saviez-Vous?",
            "es": "💡 ¿Sabías?"
        }.get(language, "💡 Did You Know?")

        fun_facts_html = f"""
<hr style='margin: 30px 0; border: none; border-top: 1px solid #4a5568;'>
<h3 style='color: #fbbf24; font-size: 1.5em; margin-bottom: 16px;'>{did_you_know_title}</h3>
"""
        for fact in fun_facts:
            fun_facts_html += f"<p style='font-size: 1em; line-height: 1.6; margin-bottom: 12px; color: #e2e8f0;'>✨ {fact}</p>\n"

        # Create info bar as HTML
        timestamp = dt.now().strftime("%m/%d/%Y, %I:%M:%S %p")
        lang_name = {"en": "English", "it": "Italiano", "fr": "Français", "es": "Español"}.get(language, language)
        info_bar = f"""
<hr style='margin: 30px 0; border: none; border-top: 1px solid #4a5568;'>
<div style='background: linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%); padding: 12px 20px; border-radius: 8px; margin-top: 20px; font-size: 0.9em; color: #a0aec0;'>
📍 <strong>{trans['info_location']}:</strong> {city_name} | 🌐 <strong>{trans['info_language']}:</strong> {lang_name} | 📅 <strong>{trans['info_generated']}:</strong> {timestamp}
</div>
"""

        # Combine all HTML sections
        story_html = f"{location_html}\n{story_html}\n{fun_facts_html}\n{info_bar}"

        share_text = story_generator.format_story_for_sharing(story_result, object_name, city_name)

        logs.append(make_log("✅", "Story generation complete!"))
        yield {
            "logs": "\n".join(logs),
            "complete": True,
            "result": (story_html, image_url, share_text),
            "error": False
        }

    except Exception as e:
        logger.error(f"Error in story generation: {e}", exc_info=True)
        logs.append(make_log("❌", f"Error: {str(e)}"))
        yield {
            "logs": "\n".join(logs),
            "complete": False,
            "result": None,
            "error": True
        }


def generate_story_flow(location: str, language: str) -> Tuple[str, Optional[str], str]:
    """Legacy non-streaming version for compatibility"""
    for update in generate_story_flow_with_logs(location, language):
        if update["complete"]:
            return update["result"]
        elif update.get("error"):
            return (format_error_message("An error occurred.", language), None, "")
    return (format_error_message("An error occurred.", language), None, "")


def format_error_message(message: str, language: str, error_type: str = "generic_error") -> str:
    poetic_messages = config.POETIC_ERROR_MESSAGES.get(language, config.POETIC_ERROR_MESSAGES["en"])
    poetic_msg = poetic_messages.get(error_type, poetic_messages.get("generic_error"))
    lang_wrapper = {
        "en": (f"✨ **Oh my!** {poetic_msg}", "Please try again!"),
        "it": (f"✨ **Oh no!** {poetic_msg}", "Riprova!"),
        "fr": (f"✨ **Oh là là!** {poetic_msg}", "Réessayez!"),
        "es": (f"✨ **¡Ay, no!** {poetic_msg}", "¡Intenta de nuevo!"),
    }
    msg, try_again = lang_wrapper.get(language, lang_wrapper["en"])
    return f"{msg}\n\n{try_again}"


def format_astronomy_dictionary(language: str) -> str:
    """Format astronomy dictionary with colorful HTML boxes"""
    dictionary = DICTIONARY_TERMS.get(language, DICTIONARY_TERMS["en"])
    trans = TRANSLATIONS.get(language, TRANSLATIONS["en"])

    # Title and intro
    html = f"""
    <div style='text-align: center; margin-bottom: 40px;'>
        <h1 style='color: #fbbf24; font-size: 2.5rem; margin-bottom: 15px;'>{trans['dict_title']}</h1>
        <p style='color: #94a3b8; font-size: 1.4rem; font-style: italic;'>{trans['dict_intro']}</p>
    </div>

    <div class='dictionary-grid'>
    """

    # Add each term as a colorful box
    for term in dictionary:
        emoji = term['emoji']
        title = term['title']
        description = term['description']
        color = term['color']

        html += f"""
        <div class='dictionary-term term-{color}'>
            <div class='emoji'>{emoji}</div>
            <div class='title'>{title}</div>
            <div class='description'>{description}</div>
        </div>
        """

    html += "</div>"
    return html


def format_about_section(language: str) -> str:
    """Format About section as HTML with enlarged fonts (1.5x)"""
    content = ABOUT_CONTENT.get(language, ABOUT_CONTENT["en"])

    html = f"""
    <div style='padding: 20px; color: #e2e8f0;'>
        <h1 style='color: #fbbf24; font-size: 3.75rem; margin-bottom: 24px;'>{content['mission_title']}</h1>
        <p style='font-size: 1.65rem; line-height: 2.4rem; margin-bottom: 32px;'>{content['mission_text']}</p>

        <hr style='border: none; border-top: 1px solid #4a5568; margin: 40px 0;'>

        <h2 style='color: #3dffa2; font-size: 2.85rem; margin-bottom: 24px;'>{content['how_title']}</h2>
    """

    for step in content['how_steps']:
        html += f"<p style='font-size: 1.65rem; line-height: 2.4rem; margin-bottom: 20px;'>{step}</p>\n"

    html += f"""
        <hr style='border: none; border-top: 1px solid #4a5568; margin: 40px 0;'>

        <h2 style='color: #2dd4bf; font-size: 2.85rem; margin-bottom: 24px;'>{content['features_title']}</h2>
    """

    for feature in content['features']:
        html += f"<p style='font-size: 1.65rem; line-height: 2.4rem; margin-bottom: 20px;'>{feature}</p>\n"

    html += "</div>"
    return html


def save_story(story_markdown: str, image_url: Optional[str], share_text: str,
               location: str, language: str, saved_stories: List[Dict]) -> Tuple[List[Dict], str]:
    if not story_markdown or "Click" in story_markdown:
        return saved_stories, "⚠️ No story to save. Generate a story first!"

    import re

    # Extract title from HTML
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', story_markdown, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else f"Story from {location}"

    story_entry = {
        "id": datetime.now().isoformat(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "location": location,
        "language": language,
        "story": story_markdown,
        "image_url": image_url,
        "share_text": share_text,
        "html_path": None  # Will be generated next
    }

    updated_stories = [story_entry] + saved_stories
    updated_stories = updated_stories[:50]

    # Generate HTML IMMEDIATELY for instant download
    html_path = generate_saved_story_html(1, updated_stories, language)
    if html_path:
        updated_stories[0]["html_path"] = html_path
        logger.info(f"✓ HTML generated immediately: {html_path}")

    message = f"💖 Story saved! You now have {len(updated_stories)} saved stories."
    logger.info(message)
    return updated_stories, message


def delete_story_by_index(index: int, saved_stories: List[Dict], language: str) -> Tuple[List[Dict], str]:
    """Delete a story by its index (1-based)"""
    trans = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    if index < 1 or index > len(saved_stories):
        return saved_stories, f"⚠️ Invalid story number. Please enter a number between 1 and {len(saved_stories)}."

    updated_stories = saved_stories.copy()
    deleted = updated_stories.pop(index - 1)
    message = f"✓ Story from {deleted['location']} deleted successfully!"
    logger.info(message)
    return updated_stories, message


def delete_all_stories(saved_stories: List[Dict], language: str) -> Tuple[List[Dict], str]:
    """Delete all saved stories"""
    count = len(saved_stories)
    if count == 0:
        return saved_stories, "ℹ️ No stories to delete."
    message = f"✓ All {count} stories deleted successfully!"
    logger.info(message)
    return [], message


def generate_saved_story_html(story_index: int, saved_stories: List[Dict], language: str = "en") -> Optional[str]:
    """
    Generate downloadable HTML for a saved story.

    Returns: HTML file path for download
    """
    if story_index < 1 or story_index > len(saved_stories):
        logger.error(f"Invalid story index: {story_index}")
        return None

    try:
        import tempfile

        story = saved_stories[story_index - 1]
        story_html = story.get("story", "")
        location = story.get("location", "Unknown")
        lang = story.get("language", "en")
        title = story.get("title", "Zen-IT Story")
        timestamp = story.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        image_url = story.get("image_url", "")

        # Prepare image tag (avoid backslash in f-string)
        img_tag = f'<img src="{image_url}" alt="{title}" class="story-image" onerror="this.style.display=\'none\'">' if image_url else ''

        # Generate printable HTML
        html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            padding: 40px 20px;
            line-height: 1.8;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #1e293b;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border: 2px solid #fbbf24;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #fbbf24;
        }}

        .header h1 {{
            font-size: 2.5rem;
            color: #fbbf24;
            margin-bottom: 15px;
        }}

        .meta {{
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 10px;
        }}

        .story-image {{
            width: 100%;
            max-width: 600px;
            height: auto;
            border-radius: 12px;
            margin: 30px auto;
            display: block;
            border: 3px solid #fbbf24;
        }}

        .story-content {{
            font-size: 1.3rem;
            line-height: 2.2rem;
            color: #e2e8f0;
        }}

        .story-content h1,
        .story-content h2,
        .story-content h3 {{
            color: #fbbf24;
            margin: 25px 0 15px 0;
        }}

        .story-content p {{
            margin-bottom: 20px;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #4a5568;
            color: #94a3b8;
            font-size: 1rem;
        }}

        @media print {{
            body {{
                background: white;
                color: black;
                padding: 0;
            }}

            .container {{
                background: white;
                border: none;
                box-shadow: none;
                padding: 20px;
            }}

            .header h1 {{
                color: #d97706;
            }}

            .story-content h1,
            .story-content h2,
            .story-content h3 {{
                color: #d97706;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 {title} 🔭</h1>
            <p class="meta">📅 {timestamp}</p>
            <p class="meta">📍 {location}</p>
        </div>

        {img_tag}

        <div class="story-content">
            {story_html}
        </div>

        <div class="footer">
            ⭐ Generated with Zen-IT Story ⭐
        </div>
    </div>
</body>
</html>"""

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            html_path = f.name

        logger.info(f"✓ Saved Story HTML generated: {html_path}")
        return html_path

    except Exception as e:
        logger.error(f"Error generating story HTML: {e}")
        return None


def generate_story_card_html(story: Dict, index: int, language: str) -> str:
    """Generate HTML for a single story card"""
    import re

    timestamp = story.get("timestamp", "Unknown")
    location = story.get("location", "Unknown")
    lang = story.get("language", "en")
    lang_flag = LANGUAGE_FLAGS.get(lang, lang)
    story_html = story.get("story", "No content")
    title = story.get("title", "Untitled Story")

    # Create expandable card with space for delete button
    html = f"""
<details style='background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
                padding: 24px 24px 24px 24px;
                border-radius: 12px;
                border-left: 6px solid #fbbf24;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                margin-bottom: 15px;'>
    <summary style='font-size: 1.8rem;
                    font-weight: bold;
                    color: #fbbf24;
                    cursor: pointer;
                    list-style: none;'>
        <span style='color: #a0aec0; font-size: 1.35rem;'>Story #{index}</span> · {title}
    </summary>
    <div style='margin-top: 24px; padding-top: 24px; border-top: 1px solid #4a5568;'>
        <p style='color: #a0aec0; font-size: 1.35rem; margin-bottom: 18px;'>
            📅 {timestamp} | 📍 {location} | {lang_flag}
        </p>
        <div style='color: #e2e8f0; font-size: 1.5rem; line-height: 2rem;'>
            {story_html}
        </div>
    </div>
</details>
"""
    return html


def generate_saved_stories_display(saved_stories: List[Dict], language: str) -> str:
    """DEPRECATED - kept for compatibility. Use generate_story_card_html for individual cards."""
    trans = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    if not saved_stories:
        return f"<h2 style='color: #fbbf24; font-size: 3rem;'>{trans['tab_saved']}</h2><p style='color: #a0aec0; font-style: italic; font-size: 1.5rem;'>{trans['saved_empty']}</p>"

    html = f"<h2 style='color: #fbbf24; margin-bottom: 20px; font-size: 3rem;'>{trans['tab_saved']}</h2>\n"
    for i, story in enumerate(saved_stories[:10], 1):
        html += generate_story_card_html(story, i, language)
    return html


def create_postcard(story_html: str, image_url: Optional[str], location: str,
                   language: str, postcards: List[Dict]) -> Tuple[List[Dict], Optional[str], str]:
    """
    Create Dream Canvas with PDF generated immediately for instant download.

    FASE 2B: Generate PDF instantly
    - Saves Dream Canvas data with PDF ready
    - PDF generated NOW (not on-demand)
    - User can download immediately from gallery
    """
    if not story_html or "Click" in story_html:
        return postcards, None, "⚠️ No story to create Dream Canvas. Generate a story first!"

    try:
        import re

        # Extract title for preview
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', story_html, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else "Zen-IT Story"

        # Save postcard to state
        postcard_entry = {
            "id": datetime.now().isoformat(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": location,
            "language": language,
            "story_html": story_html,
            "image_url": image_url,
            "title": title,
            "pdf_path": None  # Will be generated next
        }

        updated_postcards = [postcard_entry] + postcards
        updated_postcards = updated_postcards[:20]  # Keep max 20 postcards

        # Generate HTML IMMEDIATELY for instant download
        html_path = generate_dream_canvas_html(1, updated_postcards, language)
        if html_path:
            updated_postcards[0]["pdf_path"] = html_path  # Store as pdf_path for compatibility
            logger.info(f"✓ HTML generated immediately: {html_path}")

        # Create HTML preview (instant, no blocking) - TRADOTTO
        lang_flags = {"en": "🇺🇸", "it": "🇮🇹", "fr": "🇫🇷", "es": "🇪🇸"}
        lang_flag = lang_flags.get(language, language)
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Traduzioni per preview
        preview_texts = {
            "en": {
                "created": "🎨 Dream Canvas Created! 💭",
                "view_tab": "→ Go to Dream Canvas tab to download! 📥"
            },
            "it": {
                "created": "🎨 Tela dei Sogni Creata! 💭",
                "view_tab": "→ Vai al tab Tela dei Sogni per scaricare! 📥"
            },
            "fr": {
                "created": "🎨 Toile de Rêves Créée! 💭",
                "view_tab": "→ Aller à l'onglet Toile de Rêves pour télécharger! 📥"
            },
            "es": {
                "created": "🎨 Lienzo de Sueños Creado! 💭",
                "view_tab": "→ Ir a pestaña Lienzo de Sueños para descargar! 📥"
            }
        }

        preview_trans = preview_texts.get(language, preview_texts["en"])

        preview_html = f"""
        <div style='background: linear-gradient(135deg, #0b0b14 0%, #1a1a24 100%);
                    border: 3px solid #fbbf24;
                    border-radius: 12px;
                    padding: 30px;
                    text-align: center;
                    max-width: 400px;
                    margin: 0 auto;'>
            <h2 style='color: #fbbf24; font-size: 2em; margin-bottom: 15px;'>{preview_trans["created"]}</h2>
            <h3 style='color: #3dffa2; font-size: 1.5em; margin-bottom: 20px;'>{title[:50]}...</h3>
            <p style='color: #94a3b8; font-size: 1.2em; margin: 10px 0;'>📍 {location}</p>
            <p style='color: #94a3b8; font-size: 1.1em;'>{date_str} • {lang_flag}</p>
            <p style='color: #3dffa2; font-size: 1.4em; font-weight: bold; margin-top: 20px;'>{preview_trans["view_tab"]}</p>
        </div>
        """

        message = f"✓ Dream Canvas created! You now have {len(updated_postcards)} Dream Canvas ready to download."
        logger.info(message)

        return updated_postcards, preview_html, message

    except Exception as e:
        logger.error(f"Error creating postcard: {e}")
        return postcards, None, f"❌ Error creating postcard: {str(e)}"


def delete_postcard_by_index(index: int, postcards: List[Dict], language: str) -> Tuple[List[Dict], str]:
    """Delete a postcard by its index (1-based)"""
    if index < 1 or index > len(postcards):
        return postcards, f"⚠️ Invalid postcard number. Please enter a number between 1 and {len(postcards)}."

    updated_postcards = postcards.copy()
    deleted = updated_postcards.pop(index - 1)
    message = f"✓ Postcard from {deleted['location']} deleted successfully!"
    logger.info(message)
    return updated_postcards, message


def delete_all_postcards(postcards: List[Dict], language: str) -> Tuple[List[Dict], str]:
    """Delete all postcards"""
    count = len(postcards)
    if count == 0:
        return postcards, "ℹ️ No postcards to delete."
    message = f"✓ All {count} postcards deleted successfully!"
    logger.info(message)
    return [], message


def generate_dream_canvas_html(postcard_index: int, postcards: List[Dict], language: str = "en") -> Optional[str]:
    """
    Generate printable Dream Canvas HTML for children to draw their dreams.

    FASE 2A REVISED - Dream Canvas HTML: User prints to PDF from browser
    - WHITE background (#FFFFFF) - sobrio, printable
    - CSS with HUGE fonts (5rem, 4rem, 3rem)
    - Golden frame (elegant)
    - Large blank drawing area
    - Haiku box as story reminder
    - Minimal emoji decorations (⭐✨💭🌸)
    - Multi-language support (en/it/fr/es)
    - @media print for optimal printing
    - Returns: HTML file path for download
    """
    if postcard_index < 1 or postcard_index > len(postcards):
        logger.error(f"Invalid postcard index: {postcard_index}")
        return None

    try:
        import re
        import tempfile

        postcard = postcards[postcard_index - 1]
        story_html = postcard.get("story_html", "")
        location = postcard.get("location", "Unknown")
        lang = postcard.get("language", "en")
        title = postcard.get("title", "Zen-IT Story")
        timestamp = postcard.get("timestamp", datetime.now().strftime("%Y-%m-%d"))

        # Multi-language translations for Dream Canvas
        canvas_texts = {
            "en": {
                "header": "Zen-IT Story Dream Canvas",
                "draw_prompt_1": "Draw what you dreamed about",
                "draw_prompt_2": "tonight!",
                "haiku_label": "Tonight's Haiku:",
                "footer": "Generated with Zen-IT Story"
            },
            "it": {
                "header": "Tela dei Sogni Zen-IT Story",
                "draw_prompt_1": "Disegna quello che hai sognato",
                "draw_prompt_2": "stanotte!",
                "haiku_label": "Haiku di Stasera:",
                "footer": "Generato con Zen-IT Story"
            },
            "fr": {
                "header": "Toile de Rêves Zen-IT Story",
                "draw_prompt_1": "Dessine ce dont tu as rêvé",
                "draw_prompt_2": "ce soir!",
                "haiku_label": "Haiku de Ce Soir:",
                "footer": "Généré avec Zen-IT Story"
            },
            "es": {
                "header": "Lienzo de Sueños Zen-IT Story",
                "draw_prompt_1": "Dibuja lo que soñaste",
                "draw_prompt_2": "esta noche!",
                "haiku_label": "Haiku de Esta Noche:",
                "footer": "Generado con Zen-IT Story"
            }
        }

        texts = canvas_texts.get(lang, canvas_texts["en"])

        # Extract haiku from story HTML (format: <h3>🌸 Haiku title</h3><div>...</div>)
        haiku_html_lines = ""

        # Look for haiku section with 🌸 emoji in h3
        haiku_section_match = re.search(r'<h3[^>]*>🌸[^<]*</h3>\s*<div[^>]*>(.*?)</div>', story_html, re.DOTALL)

        if haiku_section_match:
            haiku_content = haiku_section_match.group(1)
            # Extract text from <p> tags
            haiku_lines = re.findall(r'<p[^>]*>(.*?)</p>', haiku_content)
            haiku_html_lines = '<br>'.join([line.strip() for line in haiku_lines if line.strip()])
            logger.info(f"✓ Haiku extracted: {len(haiku_lines)} lines")
        else:
            logger.warning("✗ Haiku not found in story HTML")

        # Generate printable HTML (user prints to PDF from browser)
        html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dream Canvas - {title}</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: system-ui, -apple-system, 'Segoe UI', Arial, sans-serif;
            background: white;
            width: 210mm;
            min-height: 297mm;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            display: flex;
            flex-direction: column;
        }}

        .corner-emoji {{
            position: absolute;
            font-size: 3rem;
            line-height: 1;
        }}

        .corner-tl {{ top: 5px; left: 5px; }}
        .corner-tr {{ top: 5px; right: 5px; }}
        .corner-bl {{ bottom: 5px; left: 5px; }}
        .corner-br {{ bottom: 5px; right: 5px; }}

        .header {{
            text-align: center;
            color: #fbbf24;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 40px 0 20px 0;
            white-space: nowrap;
        }}

        .title {{
            text-align: center;
            color: #1a202c;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 30px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .drawing-area {{
            border: 8px solid #fbbf24;
            min-height: 650px;
            flex-grow: 1;
            margin: 20px 40px;
            background: white;
            page-break-inside: avoid;
        }}

        .haiku-section {{
            text-align: center;
            margin: 30px 40px;
        }}

        .haiku-text {{
            font-size: 1.8rem;
            color: #4a5568;
            font-style: italic;
            line-height: 1.6;
        }}

        .footer {{
            text-align: center;
            color: #94a3b8;
            font-size: 1rem;
            margin-top: auto;
            padding-bottom: 10px;
        }}

        @media print {{
            body {{
                width: 210mm;
                height: 297mm;
                margin: 0;
                padding: 20px;
            }}

            .drawing-area {{
                min-height: 700px;
            }}
        }}
    </style>
</head>
<body>
    <div class="corner-emoji corner-tl">⭐</div>
    <div class="corner-emoji corner-tr">✨</div>
    <div class="corner-emoji corner-bl">✨</div>
    <div class="corner-emoji corner-br">⭐</div>

    <div class="header">🌌 {texts["header"]} 🔭</div>

    <div class="title">{title}</div>

    <div class="drawing-area"></div>

    <div class="haiku-section">
        <div class="haiku-text">{haiku_html_lines if haiku_html_lines else ''}</div>
    </div>

    <div class="footer">
        📍 {location} • {timestamp}
    </div>
</body>
</html>"""

        # Save as HTML file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8')
        temp_file.write(html_content)
        temp_file.close()

        logger.info(f"✓ Dream Canvas HTML generated: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        logger.error(f"✗ Error generating Dream Canvas PDF: {e}")
        return None


def generate_canvas_card_html(canvas: Dict, index: int, language: str) -> str:
    """Generate HTML for a single Dream Canvas card"""
    timestamp = canvas.get("timestamp", "Unknown")
    location = canvas.get("location", "Unknown")
    lang = canvas.get("language", "en")
    lang_flag = LANGUAGE_FLAGS.get(lang, lang)
    title = canvas.get("title", "Untitled")

    # Compact canvas card
    html = f"""
<div style='background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
            padding: 25px;
            border-radius: 12px;
            border: 3px solid #fbbf24;
            box-shadow: 0 4px 6px rgba(251, 191, 36, 0.2);'>
    <h3 style='color: #fbbf24; font-size: 2rem; margin: 0 0 15px 0;'>🎨 Dream Canvas #{index}</h3>
    <p style='color: #3dffa2; font-size: 1.5rem; font-weight: bold; margin: 10px 0;'>{title[:50]}{("..." if len(title) > 50 else "")}</p>
    <div style='border-top: 1px solid #fbbf24; margin: 15px 0; padding-top: 15px;'>
        <p style='color: #a0aec0; font-size: 1.3rem; margin: 8px 0;'>📍 {location}</p>
        <p style='color: #94a3b8; font-size: 1.2rem; margin: 8px 0;'>📅 {timestamp}</p>
        <p style='color: #94a3b8; font-size: 1.2rem; margin: 8px 0;'>🌐 {lang_flag}</p>
    </div>
</div>
"""
    return html


def generate_postcards_gallery(postcards: List[Dict], language: str) -> str:
    """DEPRECATED - kept for compatibility. Use generate_canvas_card_html for individual cards."""
    trans = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    if not postcards:
        return f"<h2 style='color: #fbbf24; font-size: 3rem;'>{trans['tab_postcards']}</h2><p style='color: #a0aec0; font-style: italic; font-size: 1.5rem;'>{trans['postcards_empty']}</p>"

    # Traduzioni per messaggio gallery
    gallery_msg = {
        "en": "💭 Download your Dream Canvas and draw what you dreamed tonight!",
        "it": "💭 Scarica la tua Tela dei Sogni e disegna quello che hai sognato stanotte!",
        "fr": "💭 Téléchargez votre Toile de Rêves et dessinez ce dont vous avez rêvé ce soir!",
        "es": "💭 ¡Descarga tu Lienzo de Sueños y dibuja lo que soñaste esta noche!"
    }

    html = f"<h2 style='color: #fbbf24; font-size: 3rem; margin-bottom: 20px;'>{trans['tab_postcards']}</h2>\n"
    html += f"<p style='color: #94a3b8; font-size: 1.3rem; margin-bottom: 20px;'>{gallery_msg.get(language, gallery_msg['en'])}</p>\n"
    html += "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;'>\n"

    for i, postcard in enumerate(postcards[:20], 1):
        html += generate_canvas_card_html(postcard, i, language)

    html += "</div>"
    return html


def create_share_link(share_text: str, platform: str = "whatsapp") -> str:
    encoded_text = urllib.parse.quote(share_text)
    if platform == "whatsapp":
        return f"https://wa.me/?text={encoded_text}"
    elif platform == "email":
        subject = urllib.parse.quote("🌌 My Zen-IT Story")
        return f"mailto:?subject={subject}&body={encoded_text}"
    elif platform == "twitter":
        snippet = share_text[:240] if len(share_text) > 240 else share_text
        return f"https://twitter.com/intent/tweet?text={urllib.parse.quote(snippet)}"
    elif platform == "telegram":
        return f"https://t.me/share/url?text={encoded_text}"
    return ""


def build_ui():
    """Build the Gradio interface - GRADIO 6.0 COMPATIBLE"""

    with gr.Blocks(title="🌌 Zen-IT Story 🔭") as app:
        
        current_language = gr.State("en")
        current_story = gr.State("")
        current_image = gr.State(None)
        current_location = gr.State("")
        saved_stories_state = gr.State([])
        postcards_state = gr.State([])

        gr.HTML("""
            <h1 class="app-title">Zen-IT Story<span class="emoji">🔭</span></h1>
        """)
        subtitle_display = gr.HTML(f"""<p class="subtitle">{TRANSLATIONS['en']['subtitle']}</p>""")
        subsubtitle_display = gr.HTML(f"""<p class="subsubtitle">{TRANSLATIONS['en']['subsubtitle']}</p>""")

        with gr.Row(elem_classes="lang-flags"):
            lang_en = gr.Button("🇺🇸", elem_id="lang-en", size="sm")
            lang_it = gr.Button("🇮🇹", elem_id="lang-it", size="sm")
            lang_fr = gr.Button("🇫🇷", elem_id="lang-fr", size="sm")
            lang_es = gr.Button("🇪🇸", elem_id="lang-es", size="sm")
        
        with gr.Tabs() as tabs:
            with gr.Tab(TRANSLATIONS["en"]["tab_generate"], id="tab-generate"):
                with gr.Row():
                    with gr.Column(scale=4):
                        with gr.Group(elem_classes="input-panel"):
                            location_label_md = gr.Markdown(f"<div class='location-label'>{TRANSLATIONS['en']['location_label']}</div>")

                            # UNIFIED AUTOCOMPLETE: Single Dropdown that acts as textbox + autocomplete
                            location_input = gr.Dropdown(
                                choices=POPULAR_CITIES,
                                allow_custom_value=True,
                                filterable=True,
                                value=None,
                                show_label=False,
                                container=False,
                                elem_classes="location-input-unified",
                                info="💡 Type to filter cities or enter your own"
                            )

                        generate_btn = gr.Button(
                            TRANSLATIONS["en"]["generate_btn"],
                            variant="primary",
                            size="lg",
                            elem_classes="generate-btn"
                        )
                        
                        gr.Markdown(f"### {TRANSLATIONS['en']['quick_actions']}")

                        save_btn = gr.Button(TRANSLATIONS["en"]["save_btn"], elem_classes="save-btn")
                        postcard_btn = gr.Button(TRANSLATIONS["en"]["postcard_btn"], elem_classes="postcard-btn")
                        status_msg = gr.HTML("", visible=False, elem_classes="status-message")

                        # Postcard preview
                        postcard_preview = gr.HTML(
                            value="",
                            visible=True,
                            elem_classes="postcard-preview"
                        )
                    
                    with gr.Column(scale=6):
                        # MCP Agent Activity Log
                        with gr.Accordion("📊 MCP Agent Activity Log", open=True, elem_classes="activity-log-container"):
                            activity_log = gr.Code(
                                value="Waiting for generation request...",
                                language=None,
                                label=None,
                                interactive=False,
                                elem_classes="activity-log"
                            )

                        preview_md = gr.HTML(f"""
                            <div class='waiting-container'>
                                <div class='waiting-icon'>🌙✨</div>
                                <div class='waiting-title'>{TRANSLATIONS['en']['waiting_title']}</div>
                                <div class='waiting-subtitle'>{TRANSLATIONS['en']['waiting_subtitle']}</div>
                            </div>
                        """)

                        with gr.Accordion(TRANSLATIONS["en"]["story_accordion"], open=True, visible=False) as story_accordion:
                            story_image = gr.Image(show_label=False, elem_classes="story-image")
                            story_display = gr.HTML(elem_classes="story-content")
            
            with gr.Tab(TRANSLATIONS["en"]["tab_saved"], id="tab-saved"):
                # 1. Header styled like Astronomy Dictionary
                saved_header = gr.HTML(f"""
                <div style='text-align: center; margin-bottom: 40px;'>
                    <h1 style='color: #fbbf24; font-size: 2.5rem; margin-bottom: 15px;'>{TRANSLATIONS['en']['saved_title']}</h1>
                    <p style='color: #94a3b8; font-size: 1.4rem; font-style: italic;'>{TRANSLATIONS['en']['saved_intro']}</p>
                </div>
                """)

                # 2. Stories display with integrated delete buttons - Card slots immediately below
                story_rows = []
                story_displays = []
                story_delete_btns = []

                for i in range(10):
                    with gr.Row(visible=False, elem_classes="story-card-row") as story_row:
                        with gr.Column(scale=20):
                            story_html = gr.HTML()
                        with gr.Column(scale=1, min_width=50):
                            delete_btn = gr.Button("×", size="sm", variant="stop")

                    story_rows.append(story_row)
                    story_displays.append(story_html)
                    story_delete_btns.append(delete_btn)

                # 3. Delete All button
                with gr.Row():
                    delete_all_stories_btn = gr.Button(TRANSLATIONS["en"]["delete_all_stories"], variant="stop", size="lg")

                delete_stories_msg = gr.HTML("", visible=False, elem_classes="status-message")

                # 4. Download controls at the bottom
                gr.Markdown("### 📥 Download Story")
                with gr.Row():
                    download_story_num = gr.Number(
                        label="Story number",
                        value=1,
                        minimum=1,
                        precision=0
                    )
                    download_story_btn = gr.Button("📥 Download", variant="primary", size="lg")

                download_story_file = gr.File(label="Your Story (click to download)", visible=True)

            with gr.Tab(TRANSLATIONS["en"]["tab_postcards"], id="tab-postcards"):
                # 1. Header styled like Astronomy Dictionary
                canvas_header = gr.HTML(f"""
                <div style='text-align: center; margin-bottom: 40px;'>
                    <h1 style='color: #fbbf24; font-size: 2.5rem; margin-bottom: 15px;'>{TRANSLATIONS['en']['canvas_title']}</h1>
                    <p style='color: #94a3b8; font-size: 1.4rem; font-style: italic;'>{TRANSLATIONS['en']['canvas_intro']}</p>
                </div>
                """)

                # 2. Dream Canvas display with integrated delete buttons - Card slots immediately below
                canvas_rows = []
                canvas_displays = []
                canvas_delete_btns = []

                for i in range(10):
                    with gr.Row(visible=False, elem_classes="canvas-card-row") as canvas_row:
                        with gr.Column(scale=20):
                            canvas_html = gr.HTML()
                        with gr.Column(scale=1, min_width=50):
                            delete_btn = gr.Button("×", size="sm", variant="stop")

                    canvas_rows.append(canvas_row)
                    canvas_displays.append(canvas_html)
                    canvas_delete_btns.append(delete_btn)

                # 3. Delete All button
                with gr.Row():
                    delete_all_postcards_btn = gr.Button(TRANSLATIONS["en"]["delete_all_canvas"], variant="stop", size="lg")

                delete_postcards_msg = gr.HTML("", visible=False, elem_classes="status-message")

                # 4. Download controls at the bottom
                gr.Markdown("### 📥 Download Dream Canvas")
                with gr.Row():
                    download_canvas_num = gr.Number(
                        label="Canvas number",
                        value=1,
                        minimum=1,
                        precision=0
                    )
                    download_canvas_btn = gr.Button("📥 Download", variant="primary", size="lg")

                download_canvas_file = gr.File(label="Your Dream Canvas (click to download)", visible=True)
            
            with gr.Tab(TRANSLATIONS["en"]["tab_dict"], id="tab-dict"):
                dictionary_display = gr.HTML(format_astronomy_dictionary("en"))
            
            with gr.Tab(TRANSLATIONS["en"]["tab_about"], id="tab-about"):
                about_display = gr.HTML(format_about_section("en"))

        footer_display = gr.HTML(f"""
            <div class="footer">
                <div class="footer-love">{TRANSLATIONS['en']['footer_love']}</div>
                <div class="footer-powered">{TRANSLATIONS['en']['footer_powered']}</div>
            </div>
        """)
        
        def change_language(lang_code):
            trans = TRANSLATIONS[lang_code]
            waiting_html = f"""
                <div class='waiting-container'>
                    <div class='waiting-icon'>🌙✨</div>
                    <div class='waiting-title'>{trans['waiting_title']}</div>
                    <div class='waiting-subtitle'>{trans['waiting_subtitle']}</div>
                </div>
            """
            location_label_html = f"<div class='location-label'>{trans['location_label']}</div>"
            subtitle_html = f"""<p class="subtitle">{trans['subtitle']}</p>"""
            subsubtitle_html = f"""<p class="subsubtitle">{trans['subsubtitle']}</p>"""
            footer_html = f"""
            <div class="footer">
                <div class="footer-love">{trans['footer_love']}</div>
                <div class="footer-powered">{trans['footer_powered']}</div>
            </div>
            """
            # GRADIO 6.0 FIX: Use label instead of placeholder
            saved_header_html = f"""
            <div style='text-align: center; margin-bottom: 40px;'>
                <h1 style='color: #fbbf24; font-size: 2.5rem; margin-bottom: 15px;'>{trans['saved_title']}</h1>
                <p style='color: #94a3b8; font-size: 1.4rem; font-style: italic;'>{trans['saved_intro']}</p>
            </div>
            """
            canvas_header_html = f"""
            <div style='text-align: center; margin-bottom: 40px;'>
                <h1 style='color: #fbbf24; font-size: 2.5rem; margin-bottom: 15px;'>{trans['canvas_title']}</h1>
                <p style='color: #94a3b8; font-size: 1.4rem; font-style: italic;'>{trans['canvas_intro']}</p>
            </div>
            """
            return [
                lang_code,
                subtitle_html,
                subsubtitle_html,
                location_label_html,
                gr.update(info=f"💡 {trans['location_placeholder']}"),
                trans["generate_btn"],
                trans["save_btn"],
                trans["postcard_btn"],
                waiting_html,
                format_astronomy_dictionary(lang_code),
                format_about_section(lang_code),
                footer_html,
                saved_header_html,
                canvas_header_html,
                trans["delete_all_stories"],
                trans["delete_all_canvas"],
            ]
        
        def generate_and_display(location, lang):
            """Generator function that streams MCP activity logs and story generation"""
            trans = TRANSLATIONS[lang]

            # Validation
            if not location or not location.strip():
                waiting_html = f"""
                    <div class='waiting-container'>
                        <div class='waiting-icon'>🌙✨</div>
                        <div class='waiting-title'>{trans['waiting_title']}</div>
                        <div class='waiting-subtitle'>{trans['waiting_subtitle']}</div>
                    </div>
                """
                yield [
                    "⚠️ Please enter a location to generate a story.",
                    waiting_html,
                    gr.update(visible=False),
                    None,
                    "",
                    "",
                    None,
                    location
                ]
                return

            # Stream progress updates
            for update in generate_story_flow_with_logs(location, lang):
                logs_text = update["logs"]

                if update.get("error"):
                    # Error occurred
                    error_html = f"""
                        <div class='waiting-container'>
                            <div class='waiting-icon'>❌</div>
                            <div class='waiting-title'>Generation Failed</div>
                        </div>
                    """
                    yield [
                        logs_text,
                        error_html,
                        gr.update(visible=False),
                        None,
                        "",
                        "",
                        None,
                        location
                    ]
                    return

                elif update["complete"]:
                    # Generation complete - show story
                    story_md, image_url, share_text = update["result"]
                    yield [
                        logs_text,
                        "",  # Clear waiting message
                        gr.update(visible=True, open=True),
                        image_url,
                        story_md,
                        story_md,
                        image_url,
                        location
                    ]
                    return

                else:
                    # Still processing - update log only
                    waiting_html = f"""
                        <div class='waiting-container'>
                            <div class='waiting-icon'>⏳</div>
                            <div class='waiting-title'>{trans['generating_story']}</div>
                        </div>
                    """
                    yield [
                        logs_text,
                        waiting_html,
                        gr.update(visible=False),
                        None,
                        "",
                        "",
                        None,
                        location
                    ]
        
        def update_story_slots(stories, lang):
            """Update all 10 story slots with current data"""
            updates = []
            for i in range(10):
                if i < len(stories):
                    # Show row and populate HTML
                    updates.append(gr.update(visible=True))  # Row visibility
                    updates.append(generate_story_card_html(stories[i], i+1, lang))  # HTML content
                else:
                    # Hide row
                    updates.append(gr.update(visible=False))  # Row visibility
                    updates.append("")  # Empty HTML
            return updates

        def save_current_story(story_md, img_url, loc, lang, saved):
            updated, msg = save_story(story_md, img_url, "", loc, lang, saved)
            # Generate updates for all 10 slots
            slot_updates = update_story_slots(updated, lang)
            # Success banner
            msg_html = f"""
            <div style='background: rgba(16, 185, 129, 0.15);
                        padding: 12px 16px;
                        border-left: 4px solid #10b981;
                        border-radius: 6px;
                        text-align: left;
                        font-size: 1.35rem;
                        font-weight: 600;
                        color: #10b981;
                        margin: 12px 0;'>
                ✓ {msg}
            </div>
            """
            return [updated] + slot_updates + [gr.update(value=msg_html, visible=True)]

        def update_canvas_slots(canvases, lang):
            """Update all 10 canvas slots with current data"""
            updates = []
            for i in range(10):
                if i < len(canvases):
                    # Show row and populate HTML
                    updates.append(gr.update(visible=True))  # Row visibility
                    updates.append(generate_canvas_card_html(canvases[i], i+1, lang))  # HTML content
                else:
                    # Hide row
                    updates.append(gr.update(visible=False))  # Row visibility
                    updates.append("")  # Empty HTML
            return updates

        def create_postcard_handler(story_md, img_url, loc, lang, postcards):
            updated_postcards, postcard_img, msg = create_postcard(story_md, img_url, loc, lang, postcards)
            # Generate updates for all 10 canvas slots
            canvas_slot_updates = update_canvas_slots(updated_postcards, lang)

            msg_html = f"""
            <div style='background: rgba(167, 139, 250, 0.15);
                        padding: 12px 16px;
                        border-left: 4px solid #a78bfa;
                        border-radius: 6px;
                        text-align: left;
                        font-size: 1.35rem;
                        font-weight: 600;
                        color: #a78bfa;
                        margin: 12px 0;'>
                ✓ {msg}
            </div>
            """

            return [
                updated_postcards
            ] + canvas_slot_updates + [
                gr.update(value=postcard_img, visible=True if postcard_img else False),
                gr.update(value=msg_html, visible=True)
            ]

        def delete_story_handler(index, saved, lang):
            updated, msg = delete_story_by_index(int(index) if index else 0, saved, lang)
            slot_updates = update_story_slots(updated, lang)

            msg_html = f"""
            <div style='background: rgba(239, 68, 68, 0.15);
                        padding: 12px 16px;
                        border-left: 4px solid #ef4444;
                        border-radius: 6px;
                        text-align: left;
                        font-size: 1.35rem;
                        font-weight: 600;
                        color: #ef4444;
                        margin: 12px 0;'>
                {msg}
            </div>
            """

            return [updated] + slot_updates + [gr.update(value=msg_html, visible=True)]

        def delete_all_stories_handler(saved, lang):
            updated, msg = delete_all_stories(saved, lang)
            slot_updates = update_story_slots(updated, lang)

            msg_html = f"""
            <div style='background: rgba(239, 68, 68, 0.15);
                        padding: 12px 16px;
                        border-left: 4px solid #ef4444;
                        border-radius: 6px;
                        text-align: left;
                        font-size: 1.35rem;
                        font-weight: 600;
                        color: #ef4444;
                        margin: 12px 0;'>
                {msg}
            </div>
            """

            return [updated] + slot_updates + [gr.update(value=msg_html, visible=True)]

        def download_postcard_handler(index, postcards, language):
            """Generate and return Dream Canvas PDF file for download"""
            if not postcards:
                return None, "<div style='color: #ef4444;'>⚠️ No Dream Canvas available</div>"

            pdf_path = generate_dream_canvas_pdf(int(index) if index else 1, postcards, language)

            if pdf_path:
                return pdf_path, f"<div style='color: #3dffa2;'>✓ Dream Canvas #{int(index)} PDF ready for download!</div>"
            else:
                return None, f"<div style='color: #ef4444;'>❌ Failed to generate Dream Canvas PDF</div>"

        def delete_postcard_handler(index, postcards, lang):
            updated, msg = delete_postcard_by_index(int(index) if index else 0, postcards, lang)
            canvas_slot_updates = update_canvas_slots(updated, lang)

            msg_html = f"""
            <div style='background: rgba(239, 68, 68, 0.15);
                        padding: 12px 16px;
                        border-left: 4px solid #ef4444;
                        border-radius: 6px;
                        text-align: left;
                        font-size: 1.35rem;
                        font-weight: 600;
                        color: #ef4444;
                        margin: 12px 0;'>
                {msg}
            </div>
            """

            return [updated] + canvas_slot_updates + [gr.update(value=msg_html, visible=True)]

        def delete_all_postcards_handler(postcards, lang):
            updated, msg = delete_all_postcards(postcards, lang)
            canvas_slot_updates = update_canvas_slots(updated, lang)

            msg_html = f"""
            <div style='background: rgba(239, 68, 68, 0.15);
                        padding: 12px 16px;
                        border-left: 4px solid #ef4444;
                        border-radius: 6px;
                        text-align: left;
                        font-size: 1.35rem;
                        font-weight: 600;
                        color: #ef4444;
                        margin: 12px 0;'>
                {msg}
            </div>
            """

            return [updated] + canvas_slot_updates + [gr.update(value=msg_html, visible=True)]
        
        lang_outputs = [
            current_language, subtitle_display, subsubtitle_display, location_label_md, location_input,
            generate_btn, save_btn, postcard_btn, preview_md, dictionary_display, about_display,
            footer_display, saved_header, canvas_header, delete_all_stories_btn, delete_all_postcards_btn,
        ]
        
        lang_en.click(fn=lambda: change_language("en"), outputs=lang_outputs)
        lang_it.click(fn=lambda: change_language("it"), outputs=lang_outputs)
        lang_fr.click(fn=lambda: change_language("fr"), outputs=lang_outputs)
        lang_es.click(fn=lambda: change_language("es"), outputs=lang_outputs)

        generate_btn.click(
            fn=generate_and_display,
            inputs=[location_input, current_language],
            outputs=[activity_log, preview_md, story_accordion, story_image, story_display, current_story, current_image, current_location]
        )
        
        # Build outputs lists for story slots
        story_slot_outputs = []
        for i in range(10):
            story_slot_outputs.append(story_rows[i])
            story_slot_outputs.append(story_displays[i])

        save_btn.click(
            fn=save_current_story,
            inputs=[current_story, current_image, current_location, current_language, saved_stories_state],
            outputs=[saved_stories_state] + story_slot_outputs + [status_msg]
        )

        # Build outputs lists for canvas slots
        canvas_slot_outputs = []
        for i in range(10):
            canvas_slot_outputs.append(canvas_rows[i])
            canvas_slot_outputs.append(canvas_displays[i])

        postcard_btn.click(
            fn=create_postcard_handler,
            inputs=[current_story, current_image, current_location, current_language, postcards_state],
            outputs=[postcards_state] + canvas_slot_outputs + [postcard_preview, status_msg]
        )

        # Connect individual ❌ delete buttons for Saved Stories
        for i in range(10):
            story_delete_btns[i].click(
                fn=lambda saved, lang, idx=i+1: delete_story_handler(idx, saved, lang),
                inputs=[saved_stories_state, current_language],
                outputs=[saved_stories_state] + story_slot_outputs + [delete_stories_msg]
            )

        delete_all_stories_btn.click(
            fn=delete_all_stories_handler,
            inputs=[saved_stories_state, current_language],
            outputs=[saved_stories_state] + story_slot_outputs + [delete_stories_msg]
        )

        # Download handlers - return HTML/PDF path directly
        def download_story_handler(story_num, saved_stories):
            """Return HTML path for instant download"""
            if not saved_stories:
                return None

            idx = int(story_num) - 1
            if idx < 0 or idx >= len(saved_stories):
                return None

            html_path = saved_stories[idx].get("html_path")
            if html_path:
                logger.info(f"✓ Returning Story HTML for download: {html_path}")
                return html_path
            else:
                logger.warning(f"✗ No HTML found for story #{story_num}")
                return None

        def download_canvas_handler(canvas_num, postcards):
            """Return PDF path for instant download"""
            if not postcards:
                return None

            idx = int(canvas_num) - 1
            if idx < 0 or idx >= len(postcards):
                return None

            pdf_path = postcards[idx].get("pdf_path")
            if pdf_path:
                logger.info(f"✓ Returning PDF for download: {pdf_path}")
                return pdf_path
            else:
                logger.warning(f"✗ No PDF found for canvas #{canvas_num}")
                return None

        download_story_btn.click(
            fn=download_story_handler,
            inputs=[download_story_num, saved_stories_state],
            outputs=[download_story_file]
        )

        download_canvas_btn.click(
            fn=download_canvas_handler,
            inputs=[download_canvas_num, postcards_state],
            outputs=[download_canvas_file]
        )

        # Connect individual ❌ delete buttons for Dream Canvas
        for i in range(10):
            canvas_delete_btns[i].click(
                fn=lambda postcards, lang, idx=i+1: delete_postcard_handler(idx, postcards, lang),
                inputs=[postcards_state, current_language],
                outputs=[postcards_state] + canvas_slot_outputs + [delete_postcards_msg]
            )

        delete_all_postcards_btn.click(
            fn=delete_all_postcards_handler,
            inputs=[postcards_state, current_language],
            outputs=[postcards_state] + canvas_slot_outputs + [delete_postcards_msg]
        )

    return app


if __name__ == "__main__":
    config.validate_config()
    print("\n" + "="*60)
    print("🌌 ZEN-IT-STORY - GRADIO 6.0 COMPATIBLE")
    print("="*60)
    print("Access at: http://localhost:7860")
    print("="*60 + "\n")
    app = build_ui()
    app.queue(default_concurrency_limit=10)
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS,
        show_error=True,
        max_threads=40
    )
