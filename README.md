# 🌌 Zen-IT Story 🔭

**AI-powered bedtime astronomy tales for families**

[![MCP Hackathon](https://img.shields.io/badge/MCP-Hackathon%202025-blue)](https://huggingface.co/MCP-1st-Birthday)
[![Gradio](https://img.shields.io/badge/Gradio-6.0-orange)](https://gradio.app)
[![Gemini](https://img.shields.io/badge/Google-Gemini%20AI-green)](https://ai.google.dev)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)

> Transform the night sky into personalized bedtime stories combining real astronomical data, AI-generated narratives, and haiku poetry. Educational, magical, and perfect for curious young minds! ✨

---

## 🎯 What is Zen-IT Story?

Zen-IT Story is an **educational-creative web application** that turns celestial objects visible in your night sky into personalized bedtime stories for children (ages 2-8) and their families.

**Every night is a new adventure** based on real astronomy:
- 🌍 **Real-time astronomy**: Uses your location to find visible planets, stars, and constellations
- 🤖 **AI storytelling**: Google Gemini generates unique, child-safe narratives
- 🎨 **Beautiful imagery**: Real photos from Hubble, SDSS, and NASA archives
- 📖 **Haiku poetry**: Each story ends with a contemplative haiku
- 🌐 **Multi-language**: English, Italian, French, Spanish
- 📱 **Mobile-first**: Responsive design perfect for bedtime reading

---

## ✨ Features

### 🌟 Core Features
- **Intelligent Object Selection**: MCP-powered agent chooses the most interesting celestial object for your location
- **Safe Content**: Triple-layer safety filters ensure 100% child-appropriate stories
- **Multi-language Support**: Stories and UI in 4 languages
- **Social Sharing**: WhatsApp, Email, X (Twitter), Facebook, Instagram, Telegram
- **Bookmarking**: Save favorite stories locally
- **Print/PDF**: Download stories as beautiful PDFs
- **Dark/Light Mode**: Night-friendly dark mode (default) or daytime light mode

### 🎨 Enhanced Features
- **"Did You Know?" Facts**: Educational astronomy facts with each story
- **Astronomy Dictionary**: Simple definitions for scientific terms
- **Instagram Stories Format**: Share as vertical 9:16 image
- **Create Postcard**: Combined image + text JPG for easy sharing
- **Error Messages**: Even errors are poetic and child-friendly!
- **Beautiful Typography**: Fredoka One font for a warm, playful feel

---

## 🏗️ Architecture

### Track 1: MCP Server (Building MCP)

```
┌─────────────────────────┐
│   MCP Server            │
│  (Gradio 6 + Python)    │
├─────────────────────────┤
│                         │
│  Tools:                 │
│  • select_celestial()   │
│  • get_story_prompt()   │
│  • generate_image_prompt│
│                         │
│  APIs:                  │
│  • Visible Planets v3   │
│  • Arcsecond.io         │
│  • Hubble Heritage      │
└─────────────────────────┘
```

### Track 2: Gradio UI (MCP in Action)

```
┌──────────────────────────────────┐
│   Gradio ChatInterface           │
│   (User-facing application)      │
├──────────────────────────────────┤
│                                  │
│  Components:                     │
│  • Location Selector (1000+ cities)
│  • Language Switcher (4 langs)  │
│  • Story Generator (Gemini AI)  │
│  • Image Fetcher (3-tier fallback)│
│  • Social Sharing Buttons        │
│  • Bookmark System               │
│  • Print/PDF Export              │
│                                  │
│  Integrations:                   │
│  • MCP Client → MCP Server       │
│  • Google Gemini API             │
│  • Astronomy APIs                │
└──────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))

### Installation

```bash
# Clone repository
git clone https://github.com/s-a-c99/Zen-IT-Story.git
cd Zen-IT-Story

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Run Locally

**Option 1: Full UI (recommended)**
```bash
python src/app.py
```
Open http://localhost:7860

**Option 2: MCP Server only**
```bash
python src/mcp_server.py
```
Connect with Claude Desktop or other MCP clients.

---

## 📖 Story Format

Each story follows a structured 4-act format inspired by Japanese storytelling:

### Act I - The Encounter (2-3 sentences)
The child meets the celestial object as it begins to speak

### Act II - The Message (4-6 sentences)
The star/planet shares observations about Earth and humanity

### Act III - The Promise (2-4 sentences)
A closing message of hope and wonder

### Act IV - Haiku (3 lines)
A contemplative poem capturing the essence (5-7-5 syllables for Italian, flexible for other languages)

**Example (English):**

> **The Promise of Altair**
>
> Above the sleeping city, the summer wind carries whispers.
> A bright blue light shimmers stronger than the others.
> It is Altair, the star of the celestial river.
>
> "Good evening, little human," her voice hums in the darkness.
> "Every night I watch over your planet of water and dreams.
> From up here I see oceans breathing, mountains moving,
> and millions of hearts beating together, even when they don't realize it."
>
> The child listens, eyes closed, with a slow smile.
> "Altair," asks softly, "are you lonely up there?"
>
> "Never," responds the star, "because the Earth sings.
> Every laugh, every hug, every story you tell
> reaches me like a little spark of life."
>
> Altair shines brighter, and the sky feels closer.
>
> **Haiku of Altair**
> Blue above the sea —
> I hear the human heartbeat,
> cradle of light.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | Google Gemini 1.5 Pro | Story generation |
| **Framework** | Gradio 6 | UI + MCP server |
| **Protocol** | Model Context Protocol (MCP) | Agent orchestration |
| **APIs** | Visible Planets, Arcsecond, Hubble | Astronomy data |
| **Languages** | Python 3.10+ | Backend |
| **Styling** | Custom CSS + Fredoka One font | UI design |
| **Safety** | Multi-layer content filters | Child protection |

---

## 📁 Project Structure

```
Zen-IT-Story/
├── src/                      # Source code
│   ├── app.py                # Main Gradio UI
│   ├── mcp_server.py         # MCP Server (Track 1)
│   ├── story_generator.py    # Gemini AI integration
│   ├── astronomy_api.py      # API integrations
│   ├── image_fetcher.py      # Image retrieval
│   └── config.py             # Configuration & settings
├── tests/                    # Test suites
│   ├── test_story_generator.py
│   └── test_astronomy_api.py
├── docs/                     # Documentation
│   ├── deployment/           # Deployment guides
│   ├── agents/               # Agent completion reports
│   ├── technical/            # Technical documentation
│   └── planning/             # Project planning
├── assets/                   # Static resources
│   └── custom.css            # UI styling
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🎨 Design Philosophy

### For Children
- **Simple language**: No complex astronomical jargon
- **Warm tone**: Calm, affectionate, contemplative
- **Visual beauty**: Real space imagery (not AI-generated)
- **Safety first**: Triple-layer content filtering

### For Parents
- **Educational**: Real scientific facts woven into narratives
- **Convenient**: Works on any device, mobile-first
- **Shareable**: Easy export to social media
- **Trustworthy**: Open source, transparent content generation

### For Educators
- **Multilingual**: Expand reach across cultures
- **Accurate astronomy**: Real data from NASA and scientific databases
- **Engagement**: Stories as gateway to STEM learning

---

## 🌍 Supported Languages

| Language | Code | UI | Stories | Haiku |
|----------|------|----|---------| ------|
| English | `en` | ✅ | ✅ | ✅ (flexible) |
| Italian | `it` | ✅ | ✅ | ✅ (5-7-5 strict) |
| French | `fr` | ✅ | ✅ | ✅ (flexible) |
| Spanish | `es` | ✅ | ✅ | ✅ (flexible) |

*More languages coming post-hackathon!*

---

## 🏆 MCP Hackathon Submission

This project was built for the **MCP's 1st Birthday Hackathon** (Nov 14-30, 2025) hosted by Anthropic and Gradio.

### Tracks
- **Track 1**: Building MCP - Consumer category
- **Track 2**: MCP in Action - Creative category

### Tags
- `building-mcp-track-consumer`
- `mcp-in-action-track-creative`

### Judging Criteria
- ✅ **Completeness**: Full MCP server + Gradio UI + comprehensive docs
- ✅ **Design/UI-UX**: Mobile-responsive, child-friendly, polished
- ✅ **Functionality**: Gemini AI + MCP + multi-language + safety
- ✅ **Creativity**: Unique concept combining astronomy, storytelling, and poetry
- ✅ **Documentation**: 30+ pages of guides, reports, and technical docs
- ✅ **Real-World Impact**: Educational value for families worldwide

---

## 🤝 Contributing

Contributions are welcome post-hackathon! Areas for improvement:

- Additional languages (German, Portuguese, Japanese, Arabic, etc.)
- More astronomical data sources
- Audio narration (ElevenLabs integration)
- Offline PWA support
- Community story gallery
- Teacher dashboard for classroom use

See [`docs/planning/FUTURE_IMPLEMENTATIONS.md`](docs/planning/FUTURE_IMPLEMENTATIONS.md) for full roadmap.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic & Gradio**: For hosting the MCP Hackathon
- **Google Gemini**: For providing the AI backbone (and sponsoring!)
- **NASA & Hubble Heritage**: For beautiful, free astronomy imagery
- **Arcsecond.io & Visible Planets**: For accessible astronomy APIs
- **Open source community**: For the amazing tools that made this possible

---

## 📞 Contact & Links

- **Demo**: [Coming soon - HuggingFace Space]
- **Video**: [Coming soon - YouTube demo]
- **Hackathon**: https://huggingface.co/MCP-1st-Birthday
- **Issues**: https://github.com/s-a-c99/Zen-IT-Story/issues

---

## 🌙 Philosophy

> "We are all made of star stuff" - Carl Sagan

Zen-IT Story believes that astronomy is not just science—it's wonder, poetry, and connection. Every child who looks up at the stars is asking the same question humanity has asked for millennia: *What's out there?*

Our answer is a bedtime story. Because wonder should be gentle, knowledge should be joyful, and every night sky deserves to be celebrated.

**Sweet dreams and clear skies!** ✨🌟🌙

---

*Built with ❤️ for families who love the stars*
*November 2025 | MCP Hackathon Submission*
