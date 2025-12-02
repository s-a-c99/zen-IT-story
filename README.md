# 🌌 Zen-IT Story 🔭

**Transform the night sky into magical bedtime stories combining real astronomy, AI narratives, and haiku poetry**


[![MCP Hackathon](https://img.shields.io/badge/MCP_1st_Birthday-Hackathon_2025-blueviolet?style=for-the-badge&logo=huggingface)](https://huggingface.co/MCP-1st-Birthday)
[![Gradio 6.0](https://img.shields.io/badge/Gradio-6.0_MCP-orange?style=for-the-badge&logo=gradio)](https://gradio.app)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_2.5-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)
[![Skyfield](https://img.shields.io/badge/Skyfield-Astronomy-success?style=for-the-badge)](https://rhodesmill.org/skyfield/)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> Every night, a new star. Every star, a new story. Perfect for curious young minds aged 2-8 and their families! ✨

---

## 🎥 Demo Video

**Watch zen-IT story in action:**
- [🤗 Hugging Face](https://huggingface.co/spaces/MCP-1st-Birthday/zen-IT-story/blob/main/README.md)


---

## 📱 Social Media

**Follow the launch:**
- [𝕏 Announcement](https://x.com/s_a_c99/status/1995255819600867538?s=20)

---

## 🎯 What is Zen-IT Story?

An **educational-creative web application** that turns celestial objects visible in your night sky into personalized bedtime stories.

### ✨ Key Features

🌍 **Real-time Astronomy** → Uses your location to find visible planets and stars tonight  
🤖 **AI Storytelling** → Google Gemini generates unique, child-safe narratives  
🎨 **Beautiful Imagery** → Real photos from Hubble, SDSS, and NASA archives  
📖 **Haiku Poetry** → Each story ends with a contemplative haiku  
🌐 **Multi-language** → English, Italian, French, Spanish  
🎨 **Dream Canvas** → Printable activity template for kids to draw their dreams  
💾 **Save & Share** → Bookmark stories and share on social media


---

## 🏗️ System Architecture

### Data Flow Map

```
User Input (location, language)
    │
    ├──→ astronomy_api.parse_location_input() → (lat, lon, city)
    │         │
    │         ├──→ CITIES dict (300+ worldwide)
    │         │         ↓ fallback
    │         └──→ get_user_location_from_ip()
    │                   └──→ ipapi.co/json
    │
    └──→ mcp_server.select_celestial(lat, lon, date)
              │
              ├──→ LEVEL 1: Skyfield (PRIORITY)
              │         │
              │         ├──→ de421.bsp (NASA JPL ephemeris)
              │         ├──→ hip_main.dat (Hipparcos catalog)
              │         └──→ get_visible_stars_skyfield()
              │                   ├──→ Observer at lat/lon
              │                   ├──→ Filter: altitude > 30°
              │                   ├──→ Filter: magnitude ≤ 2.5
              │                   └──→ Return: top 10 brightest
              │
              │         ↓ fallback
              ├──→ LEVEL 2: Visible Planets API
              │         └──→ api.visibleplanets.dev/v3
              │
              │         ↓ fallback
              └──→ LEVEL 3: Hemisphere Defaults
                        ├──→ Northern: Polaris, Vega, Arcturus, Deneb
                        └──→ Southern: Sirius, Canopus, Alpha Centauri
                        │
                        ↓ scoring
              celestial_object{name, type, ra, dec, score}
                          │
    ┌─────────────────────┴─────────────────────┐
    ↓                                           ↓
story_generator.generate_story()       image_fetcher.fetch_image()
    │                                           │
    ├──→ Gemini 2.5 Flash                       ├──→ T1: Curated Mapping
    │         ├──→ STORY_PROMPT_TEMPLATE        │         └──→ HEAD check (auto-skip)
    │         ├──→ 4-act structure              │
    │         └──→ Multi-lang (en/it/fr/es)     ├──→ T2: NASA SkyView (RA/Dec)
    │                                           │
    ├──→ Safety filter (3 layers)               ├──→ T3: SDSS SkyServer (RA/Dec)
    │         ├──→ L1: Gemini BLOCK_MEDIUM      │
    │         ├──→ L2: UNSAFE_WORDS (60+)       ├──→ T4: Hubble Heritage (name)
    │         └──→ L3: Retry → fallback         │
    │                                           ├──→ T5: Wikimedia Commons
    ├──→ parse_story()                          │
    │         └──→ Extract title + haiku        ├──→ T6: NASA APOD
    │                                           │
    ├──→ validate_haiku()                       └──→ T7: Fallback Starfield
    │         └──→ syllables.estimate()                 │
    │                                                   │
    └──→ generate_fun_facts()                           │
             │                                          │
             └──────────────────┬───────────────────────┘
                                ↓
                      app.py.generate_story_flow()
                                │
                                ├──→ Streaming MCP Activity Log
                                │
                      ┌─────────┴─────────┐
                      ↓                   ↓
              format_story_for_display()  Sharing/Export handlers
                      │
                      ├──→ HTML rendering
                      ├──→ Location banner
                      ├──→ Haiku gradient box
                      └──→ "Did You Know?" facts
                                │
                                ↓
                      Gradio UI (gr.Blocks)
                                │
                                ├──→ 🏠 Generate Story
                                │         ├──→ City autocomplete (60+)
                                │         ├──→ Language flags 🇺🇸🇮🇹🇫🇷🇪🇸
                                │         └──→ MCP Activity Log
                                │
                                ├──→ 📚 Saved Stories (max 50)
                                │         └──→ HTML export
                                │
                                ├──→ 🎨 Dream Canvas
                                │         └──→ Printable A4 template
                                │
                                ├──→ 📖 Astronomy Dictionary
                                │         └──→ 18 terms × 4 languages
                                │
                                └──→ ℹ️ About
```

---

## 🔮 How It Works

The app combines **real astronomical data** with **AI creativity**:

### 1. **Location-Based Star Selection** (MCP + Skyfield)
- Enter your city (or use auto-geolocation)
- MCP agent calculates visible celestial objects using Skyfield library
- Selects the most interesting star/planet for tonight's story

### 2. **Story Generation** (Google Gemini 2.5 Flash)
- Generates age-appropriate narrative (2-8 years old)
- Follows 4-act structure inspired by Japanese storytelling
- Triple-layer safety filtering ensures 100% child-appropriate content

### 3. **Real Astronomical Images** (Multi-API Strategy)
- **Priority 1**: Curated star images (Wikimedia/ESO/NASA)
- **Priority 2**: NASA SkyView (uses RA/Dec coordinates)
- **Priority 3**: SDSS + SkyServer (real coordinates from Skyfield)
- **Priority 4**: Hubble Heritage Archive (search by name)
- **Priority 5**: NASA Images API (search by name)

### 4. **Enhanced Features**
- Haiku poetry generation (5-7-5 syllables for Italian, flexible for others)
- "Did You Know?" astronomy facts
- Printable Dream Canvas for kids to draw
- Astronomy Dictionary with 18 terms

---

## 🏗️ Technical Architecture

### Track 1: MCP Server (Building MCP)

The app includes an **MCP-compatible server** that exposes astronomy tools:

```python
# MCP Tools exposed via Gradio 6
- select_celestial(lat, lon, date) → Returns best object for location
- get_story_prompt(object, location) → Generates Gemini prompt
- generate_image_prompt(object) → Creates image search query
```

**Data Flow**:
```
User Location → MCP Server → Skyfield Calculation
    ↓
Visible Stars/Planets (Top 10 by magnitude)
    ↓
MCP Agent Selects Best Object
    ↓
Gemini API generates story → Image APIs fetch photo
```

### Track 2: Gradio UI (MCP in Action)

Beautiful **Gradio 6.0 interface** with:
- Autocomplete city selector (60+ popular cities)
- Streaming MCP activity logs
- Multi-tab navigation (Generate, Saved Stories, Dream Canvas, Dictionary, About)
- Responsive mobile-first design
- Custom CSS with animated starry background

---

## 🔧 MCP Server Tools

The project exposes **3 MCP-compatible tools** via Gradio 6.0:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `select_celestial()` | Choose best visible object | `lat`, `lon`, `date` | `{object_name, type, ra, dec, magnitude, score}` |
| `get_story_prompt()` | Generate narrative template | `object_name`, `language` | Formatted prompt string |
| `generate_image_prompt()` | Image search strategy | `object_name`, `object_type` | `{strategy, hubble_url, sdss_url, ...}` |

### MCP Endpoints

```
SSE:    http://localhost:7860/gradio_api/mcp/sse
Schema: http://localhost:7860/gradio_api/mcp/schema
```

---

## 🗂️ Data Sources & External APIs

| API | Purpose | Auth | Fallback |
|-----|---------|------|----------|
| **Skyfield + Hipparcos** | Real-time star visibility calculation | None (local) | Hemisphere-based stars |
| **Visible Planets API** | Planet positions | None | Level 3 fallback |
| **Google Gemini 2.5 Flash** | Story generation | API Key | Pre-written fallback stories |
| **NASA SkyView** | Real sky images (RA/Dec) | None | Next tier |
| **SDSS SkyServer** | Astronomical survey images | None | Next tier |
| **Hubble Heritage** | HST images by name | None | Next tier |
| **Wikimedia Commons** | Astronomy images | None | Next tier |
| **NASA APOD** | Picture of the Day | DEMO_KEY | Starfield fallback |
| **ipapi.co** | IP geolocation | None | Manual city input |

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Model** | Google Gemini 2.5 Flash | Story generation with safety filters |
| **UI Framework** | Gradio 6.0 | UI + MCP server capabilities |
| **Protocol** | Model Context Protocol | Agent orchestration |
| **Astronomy** | Skyfield | Real-time star visibility calculations |
| **Ephemeris** | JPL DE421 | Planetary positions |
| **Star Catalog** | Hipparcos | 118,218 stars |
| **APIs** | Visible Planets, Arcsecond, Hubble, NASA | Astronomical data and images |
| **Languages** | Python 3.10+ | Backend logic |
| **Styling** | Custom CSS + Fredoka font | Child-friendly design |
| **Safety** | Multi-layer | Child content filtering |

---
## 📁 Project Structure

```
zen-IT-story/
│
├── app.py                          # Main Gradio 6.0 UI (2900+ lines)
│                                   # - 5-tab interface
│                                   # - Streaming MCP logs
│                                   # - Custom CSS with starfield
│                                   # - Multi-language translations
│                                   # - Dream Canvas generator
│
├── src/
│   ├── __init__.py                 # Package marker
│   │
│   ├── mcp_server.py               # MCP Server (Track 1)
│   │                               # - select_celestial(): 3-level selection
│   │                               # - get_story_prompt(): Template builder
│   │                               # - generate_image_prompt(): Strategy chain
│   │                               # - Skyfield integration
│   │
│   ├── story_generator.py          # Gemini AI Integration
│   │                               # - generate_story(): Main generator
│   │                               # - parse_story(): Extract title/haiku
│   │                               # - validate_haiku(): Syllable checking
│   │                               # - safety_filter(): Content validation
│   │                               # - generate_fun_facts(): Educational facts
│   │
│   ├── image_fetcher.py            # Self-Healing Image Chain
│   │                               # - 7-tier fallback system
│   │                               # - HEAD check for auto-skip
│   │                               # - Curated star mapping
│   │                               # - NASA/SDSS/Hubble integration
│   │
│   ├── astronomy_api.py            # Astronomy Utilities
│   │                               # - parse_location_input(): City resolver
│   │                               # - get_user_location_from_ip(): Geo fallback
│   │                               # - Caching layer (TTL 1h)
│   │
│   └── config.py                   # Configuration Hub
│                                   # - 300+ cities with coordinates
│                                   # - 4-language i18n strings
│                                   # - UNSAFE_WORDS blacklist (60+ terms)
│                                   # - Gemini safety settings
│                                   # - Story prompt template
│                                   # - 18-term astronomy dictionary
│
├── de421.bsp                       # NASA JPL Ephemeris (16 MB)
├── hip_main.dat                    # Hipparcos Star Catalog (53 MB)
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

---

## 📖 Story Format

Each story follows a **4-act structure** inspired by Japanese storytelling:

| Act | Content | Duration |
|-----|---------|----------|
| **I. The Encounter** | Child meets the celestial object | 2-3 sentences |
| **II. The Message** | Star shares observations about Earth | 4-6 sentences |
| **III. The Promise** | Closing message of hope | 2-4 sentences |
| **IV. Haiku** | Contemplative 5-7-5 poem | 3 lines |

---

## 🚀 Quick Start

### Run Locally

```bash
# Clone repository
git clone https://huggingface.co/spaces/MCP-1st-Birthday/zen-it-story
cd zen-it-story

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run app
python app.py
```

Open http://localhost:7860

### API Key

Get a **free** Google Gemini API key:  
👉 [Google AI Studio](https://aistudio.google.com/app/apikey)


---

## 🌍 Supported Languages

| Language | Code | UI | Stories | Haiku | Dictionary |
|----------|------|:--:|:-------:|:-----:|:----------:|
| 🇺🇸 English | `en` | ✅ | ✅ | ✅ flexible | ✅ 18 terms |
| 🇮🇹 Italian | `it` | ✅ | ✅ | ✅ strict 5-7-5 | ✅ 18 terms |
| 🇫🇷 French | `fr` | ✅ | ✅ | ✅ flexible | ✅ 18 terms |
| 🇪🇸 Spanish | `es` | ✅ | ✅ | ✅ flexible | ✅ 18 terms |

---

## 🎨 Design Philosophy

### For Children (Ages 2-8)
- **Simple language**: No complex jargon, warm and calm tone
- **Visual beauty**: Real space imagery (not AI-generated)
- **Safety first**: Triple-layer content filtering
- **Interactive**: Printable Dream Canvas to draw their dreams

### For Parents
- **Educational**: Real scientific facts woven into narratives
- **Convenient**: Works on any device, mobile-responsive
- **Shareable**: Easy social media export
- **Trustworthy**: Open source, transparent AI usage

### For Educators
- **Multilingual**: Expand reach across cultures
- **Accurate astronomy**: NASA/ESA data sources
- **STEM Gateway**: Stories spark interest in science

---

## 🏆 MCP Hackathon Submission

Built for **MCP's 1st Birthday Hackathon** (Nov 14-30, 2025)

### Submission Tracks
- **Track 1: Building MCP**
- **Track 2: MCP in Action**
 
### Why This Project Stands Out

✅ **Completeness** → Full MCP server + Gradio UI + comprehensive docs  
✅ **Design/UI-UX** → Mobile-responsive, polished, child-friendly  
✅ **Functionality** → Multi-API integration, real astronomy, AI safety  
✅ **Creativity** → Unique concept: astronomy + storytelling + poetry  
✅ **Real-World Impact** → Educational value for families worldwide  
✅ **Documentation** → Clear README, inline code comments, guides  

---

## 📜 License

**MIT License** - See [LICENSE](LICENSE) file

Free to use, modify, and distribute with attribution.

---

## 🙏 Acknowledgments

- **Anthropic & Gradio**: For hosting the MCP Hackathon
- **Google Gemini**: For AI capabilities and sponsorship
- **NASA, ESA, Hubble Heritage**: For stunning, free imagery
- **Arcsecond.io & Visible Planets API**: For accessible astronomy data
- **Open source community**: For the amazing tools

---

## 🔗 Links

- **Social Media**: [X Thread](https://x.com/s_a_c99/status/1995255819600867538?s=20)
- **MCP Hackathon**: [https://huggingface.co/MCP-1st-Birthday](https://huggingface.co/MCP-1st-Birthday)

---

## 🌙 Philosophy

> *"We are all made of star stuff"* — Carl Sagan

Zen-IT Story believes astronomy is not just science—it's **wonder, poetry, and connection**. Every child who looks up at the stars asks: *What's out there?*

Our answer is a bedtime story.

Because **wonder should be gentle**, **knowledge should be joyful**, and every night sky deserves to be celebrated.

---

**Sweet dreams and clear skies !!** ✨🌟🌙

---


*Built with ❤️ for families who love the stars*  

