---
title: Zen IT Story
emoji: 🌖
colorFrom: blue
colorTo: pink
sdk: gradio
sdk_version: 6.0.1
app_file: app.py
pinned: false
license: mit
short_description: MCP-powered bedtime astronomy stories for families
tags:
- building-mcp-track-customer
- building-mcp-track-creative
- mcp-in-action-track-consumer
- mcp-in-action-track-creative
---

---
title: Zen-IT Story
emoji: 🔭
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.0.0
app_file: app.py
pinned: false
license: mit
short_description: AI-powered bedtime astronomy stories for families
tags:
  - building-mcp-track-consumer
  - building-mcp-track-creative
  - mcp-in-action-track-consumer
  - mcp-in-action-track-creative
---

# 🌌 Zen-IT Story 🔭

**Transform the night sky into magical bedtime stories combining real astronomy, AI narratives, and haiku poetry**

[![Gradio](https://img.shields.io/badge/Gradio-6.0-orange)](https://gradio.app)
[![Gemini](https://img.shields.io/badge/Google-Gemini%20AI-green)](https://ai.google.dev)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)
[![MCP Hackathon](https://img.shields.io/badge/MCP-Hackathon%202025-blue)](https://huggingface.co/MCP-1st-Birthday)

> Every night, a new star. Every star, a new story. Perfect for curious young minds aged 2-8 and their families! ✨

---

## 🎥 Demo Video

**Watch Zen-IT Story in action:**

[![Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

[▶️ Watch full demo on YouTube](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

---

## 📱 Social Media

**Follow the launch:**
- [🐦 Twitter/X Announcement](https://x.com/YOUR_HANDLE/status/TWEET_ID)

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

## 🔮 How It Works

The app combines **real astronomical data** with **AI creativity**:

### 1. **Location-Based Star Selection** (MCP + Skyfield)
- Enter your city (or use auto-geolocation)
- MCP agent calculates visible celestial objects using Skyfield library
- Selects the most interesting star/planet for tonight's story

### 2. **Story Generation** (Google Gemini 1.5)
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
- Dark/Light mode toggle

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

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Model** | Google Gemini 1.5 Pro | Story generation with safety filters |
| **Framework** | Gradio 6.0 | UI + MCP server capabilities |
| **Protocol** | Model Context Protocol | Agent orchestration |
| **Astronomy** | Skyfield | Real-time star visibility calculations |
| **APIs** | Visible Planets, Arcsecond, Hubble, NASA | Astronomical data and images |
| **Languages** | Python 3.10+ | Backend logic |
| **Styling** | Custom CSS + Fredoka font | Child-friendly design |

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

## 📖 Story Format

Each story follows a **4-act structure**:

### Act I - The Encounter (2-3 sentences)
Child meets the celestial object as it begins to speak

### Act II - The Message (4-6 sentences)
Star/planet shares observations about Earth and humanity

### Act III - The Promise (2-4 sentences)
Closing message of hope and wonder

### Act IV - Haiku (3 lines)
Contemplative poem capturing the essence

**Example** (English):

> **The Promise of Altair**
>
> Above the sleeping city, the summer wind carries whispers.  
> A bright blue light shimmers stronger than the others.  
> It is Altair, the star of the celestial river.
>
> "Good evening, little human," her voice hums in the darkness.  
> "Every night I watch over your planet of water and dreams..."
>
> **Haiku of Altair**  
> *Blue above the sea —*  
> *I hear the human heartbeat,*  
> *cradle of light.*

---

## 🌍 Supported Languages

| Language | Code | UI | Stories | Haiku | Dictionary |
|----------|------|----|---------| ------|------------|
| English | `en` | ✅ | ✅ | ✅ | ✅ (18 terms) |
| Italian | `it` | ✅ | ✅ | ✅ (5-7-5) | ✅ (18 terms) |
| French | `fr` | ✅ | ✅ | ✅ | ✅ (18 terms) |
| Spanish | `es` | ✅ | ✅ | ✅ | ✅ (18 terms) |

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
- **Track 1: Building MCP** - Consumer category
- **Track 2: MCP in Action** - Creative category

### Why This Project Stands Out

✅ **Completeness** → Full MCP server + Gradio UI + comprehensive docs  
✅ **Design/UI-UX** → Mobile-responsive, polished, child-friendly  
✅ **Functionality** → Multi-API integration, real astronomy, AI safety  
✅ **Creativity** → Unique concept: astronomy + storytelling + poetry  
✅ **Real-World Impact** → Educational value for families worldwide  
✅ **Documentation** → Clear README, inline code comments, guides  

---

## 📁 Project Structure

```
zen-it-story/
├── app.py                    # Main Gradio UI (MCP-enabled)
├── src/
│   ├── __init__.py
│   ├── mcp_server.py         # MCP server tools
│   ├── story_generator.py    # Gemini AI integration
│   ├── astronomy_api.py      # Skyfield + API integrations
│   ├── image_fetcher.py      # Multi-source image retrieval
│   └── config.py             # Configuration & constants
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🤝 Contributing

Post-hackathon contributions welcome! Ideas:

- 🌍 More languages (German, Portuguese, Japanese, Arabic)
- 🔊 Audio narration (ElevenLabs TTS)
- 📱 Progressive Web App (offline support)
- 🏫 Teacher dashboard for classroom use
- 🌟 Community story gallery
- 🎮 Interactive constellation games

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

- **GitHub Repository**: [https://github.com/s-a-c99/zen-it-story](https://github.com/s-a-c99/zen-it-story)
- **Live Demo**: [This Space!](https://huggingface.co/spaces/MCP-1st-Birthday/zen-it-story)
- **Demo Video**: [YouTube Link](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
- **Social Media**: [Twitter/X Thread](https://x.com/YOUR_HANDLE/status/TWEET_ID)
- **MCP Hackathon**: [https://huggingface.co/MCP-1st-Birthday](https://huggingface.co/MCP-1st-Birthday)

---

## 🌙 Philosophy

> *"We are all made of star stuff"* — Carl Sagan

Zen-IT Story believes astronomy is not just science—it's **wonder, poetry, and connection**. Every child who looks up at the stars asks: *What's out there?*

Our answer is a bedtime story.

Because **wonder should be gentle**, **knowledge should be joyful**, and every night sky deserves to be celebrated.

---

**Sweet dreams and clear skies!** ✨🌟🌙

---

*Built with ❤️ for families who love the stars*  
*November 2025 | MCP 1st Birthday Hackathon Submission*