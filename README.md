# 🌾 Krishi Sathi — AI-Powered Crop Recommendation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Sarvam AI](https://img.shields.io/badge/Sarvam%20AI-mayura:v1-6C63FF?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**Empowering Indian farmers with AI — in their own language.**

[Features](#-features) · [Architecture](#-architecture) · [Tech Stack](#-tech-stack) · [Setup](#-getting-started) · [API Reference](#-api-reference)

</div>

---

## 📖 Overview

**Krishi Sathi** (meaning *Farmer's Friend* in Hindi/Marathi) is an intelligent, multilingual crop recommendation system built for Indian farmers. It combines a trained Machine Learning model with a multi-agent AI orchestration pipeline to recommend the most suitable crops based on soil type, season, location, irrigation availability, and land area.

The system is designed to be **language-first** — serving all content (UI labels, state/district names, crop recommendations, farm details) in the farmer's selected language: **English**, **हिन्दी (Hindi)**, or **मराठी (Marathi)**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **ML Crop Prediction** | Random Forest classifier trained on Indian crop data predicts top recommendations with confidence scores |
| 🌐 **Full Multilingual UI** | All UI labels, headings, buttons, and placeholders switch between English, Hindi, and Marathi |
| 🗣️ **Sarvam AI Translation** | Uses `mayura:v1` from Sarvam AI for accurate, contextual translation of dynamic recommendation content |
| 🗺️ **28 States & Districts** | Pre-translated static JSON for all 28 Indian states and major districts — no live API call required |
| 🌿 **LLM-Enhanced Explanations** | OpenRouter-based LLM generates farmer-friendly explanations with automatic primary → fallback model chain |
| 🖼️ **Crop Images** | Tavily-powered image search fetches real crop photos for each recommendation card |
| 💾 **Persistent Storage** | SQLite database stores all recommendation requests, agent executions, and results |
| 🔁 **Agent Orchestration** | Multi-agent pipeline orchestrates ML prediction, regional context lookup, and LLM enrichment |
| 📋 **Farm Input Summary** | Results page shows all submitted farm inputs in the selected language alongside recommendations |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Vanilla JS)                     │
│                                                             │
│  index.html ──► app.js ──► translations.json                │
│  results.html ──► results.js                                │
│                                                             │
│  Language Selector (en | hi | mr)                           │
│       │                                                     │
│       ├─ Switches UI labels via data-i18n attributes        │
│       ├─ Passes ?lang= to location APIs                     │
│       └─ Passes language field in recommendation POST       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Flask REST API (Backend)                   │
│                                                             │
│  POST /api/v1/recommendations                               │
│  GET  /api/v1/locations/states?lang=hi                      │
│  GET  /api/v1/locations/districts?state=X&lang=mr           │
│  GET  /api/v1/soil-types                                    │
└──────────┬────────────────────┬─────────────┬──────────────┘
           │                    │             │
           ▼                    ▼             ▼
 ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
 │  Agent Service   │ │  Translation     │ │  Location API    │
 │  Orchestration   │ │  Service         │ │  (Static JSON)   │
 │                  │ │                  │ │                  │
 │  1. ML Predict   │ │  Sarvam AI       │ │ states-hi.json   │
 │  2. Regional Ctx │ │  mayura:v1       │ │ states-mr.json   │
 │  3. LLM Enhance  │ │                  │ │                  │
 └──────┬───────────┘ └──────────────────┘ └──────────────────┘
        │
        ├──► RandomForestClassifier (crop_rec_v1.0.pkl)
        │
        ├──► LLM Service (OpenRouter)
        │    Primary:  google/gemma-4-26b-a4b-it:free
        │    Fallback: nvidia/nemotron-3-super-120b-a12b:free
        │
        └──► Tavily Service (Crop Image Search, top-5 per crop)
```

### Recommendation Data Flow

```
POST /api/v1/recommendations
  { state, district, soil_type, season, irrigation, land_area, language }
        │
        ▼
  FarmerInputSchema (Pydantic v2 validation)
        │
        ▼
  AgentOrchestrationService.run(profile_dict)
     ├── ML Tool → RandomForest prediction → ranked crop list
     ├── Regional Tool → state/district context lookup
     └── LLM Tool → farmer-friendly explanations (primary → fallback model)
        │
        ▼
  Tavily Image Enrichment (top-5 images per crop)
        │
        ▼
  Save to SQLite
     (FarmerProfile, RecommendationRequest, AgentExecution, CropRecommendation)
        │
        ▼
  RecommendationService._translate_response(response, lang)
     └── Sarvam AI mayura:v1 → translates crop names, explanations, summary
        │
        ▼
  JSON Response to Frontend
```

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|---|---|
| Web Framework | Flask 3.x (Python 3.11+) |
| Data Validation | Pydantic v2 |
| ORM & Database | SQLAlchemy + SQLite |
| ML Model | scikit-learn `RandomForestClassifier` |
| Translation | Sarvam AI `mayura:v1` |
| LLM Explanations | OpenRouter (primary + fallback chain) |
| Image Search | Tavily API |
| Agent Orchestration | Custom multi-agent service (optional CrewAI) |

### Frontend
| Component | Technology |
|---|---|
| Structure | Vanilla HTML5 |
| Logic | Vanilla JavaScript (ES6+, no build step) |
| Styling | Vanilla CSS with CSS custom properties |
| i18n | Static `translations.json` + dynamic location APIs |
| State | `sessionStorage` (results) + `localStorage` (language preference) |

### External APIs
| API | Purpose | Endpoint |
|---|---|---|
| **Sarvam AI** `mayura:v1` | Translating all dynamic content to Hindi/Marathi | `https://api.sarvam.ai/translate` |
| **OpenRouter** | LLM-generated crop explanations | `https://openrouter.ai/api/v1` |
| **Tavily** | Real crop images for result cards | Tavily Search API |

---

## 📁 Project Structure

```
Krishi Sathi/
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       ├── locations.py          # State/district/soil-type endpoints
│       │       └── recommendations.py   # POST /recommendations
│       ├── core/
│       │   ├── config.py                # Env variable loader
│       │   ├── constants.py             # STATES_DISTRICTS, SOIL_TYPES, crop tables
│       │   └── database.py              # SQLAlchemy setup
│       ├── models/                      # ORM models (FarmerProfile, CropRecommendation…)
│       ├── schemas/
│       │   └── farmer_input.py          # Pydantic input validation schema
│       └── services/
│           ├── agent_service.py         # Multi-agent pipeline orchestration
│           ├── llm_service.py           # OpenRouter LLM + fallback chain
│           ├── recommendation_service.py# Core logic: prediction + translation
│           ├── tavily_service.py        # Crop image search
│           └── translation_service.py  # Sarvam AI mayura:v1 wrapper (cached)
├── frontend/
│   ├── css/
│   │   └── styles.css                   # CSS variables, layout, crop cards
│   ├── js/
│   │   ├── app.js                       # Form, language switching, API calls
│   │   └── results.js                  # Results rendering, input summary
│   ├── index.html                       # Farm input form (multilingual)
│   ├── results.html                     # Recommendation results page
│   ├── translations.json               # Static UI translations (en / hi / mr)
│   ├── states-and-districts.json        # Master English location data (28 states)
│   ├── states-and-districts-hi.json     # Pre-translated Hindi locations
│   └── states-and-districts-mr.json     # Pre-translated Marathi locations
├── ml/
│   └── crop_recommendation/
│       └── models/
│           └── crop_rec_v1.0.pkl        # Trained RandomForest model
├── .env                                 # API keys & config (not committed to git)
├── requirements.txt
├── run.py                               # App entry point
└── run_test.py                          # Quick integration smoke-test
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- API keys for: **Sarvam AI**, **OpenRouter** (optional), **Tavily** (optional)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/krishi-sathi.git
cd krishi-sathi
```

### 2. Create & Activate Virtual Environment
```bash
# conda (recommended)
conda create -n krishi python=3.11
conda activate krishi

# venv
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:

```env


```

### 5. Run the App
```bash
python run.py
```

Open **http://localhost:5000** in your browser.

---

## 🌐 API Reference

### `POST /api/v1/recommendations`
Submit a farmer's farm details and receive ranked crop recommendations.

**Request Body:**
```json
{
  "state": "Maharashtra",
  "district": "Pune",
  "village": "Hadapsar",
  "land_area": 5.0,
  "land_unit": "acres",
  "soil_type": "Black",
  "season": "Kharif",
  "irrigation_available": true,
  "language": "hi"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `state` | string | ✅ | Must match a valid state name |
| `district` | string | ✅ | Must be valid for the given state |
| `village` | string | | Optional |
| `land_area` | float | ✅ | `0.1 – 500` |
| `land_unit` | string | | `"acres"` or `"hectares"` |
| `soil_type` | string | ✅ | See supported values below |
| `season` | string | | `"Kharif"`, `"Rabi"`, or `"Zaid"` |
| `irrigation_available` | boolean | | Default: `true` |
| `language` | string | | `"en"`, `"hi"`, or `"mr"` |

**Response:**
```json
{
  "request_id": "uuid-...",
  "status": "success",
  "farmer_inputs": { "state": "महाराष्ट्र", "district": "पुणे", ... },
  "recommendations": [
    {
      "rank": 1,
      "crop_name": "सोयाबीन",
      "suitability": "उच्च",
      "suitability_score": 82.5,
      "estimated_risk": "कम",
      "estimated_return_potential": "उच्च",
      "explanation": "सोयाबीन आपके काले मिट्टी...",
      "method": "ml",
      "images": ["https://..."]
    }
  ],
  "summary": "...",
  "disclaimer": "...",
  "metadata": {
    "model_version": "crop_rec_v1.0",
    "llm_model": "...",
    "processing_time_ms": 1420,
    "generated_at": "2026-08-16T02:00:00Z"
  }
}
```

---

### `GET /api/v1/locations/states?lang=hi`
Returns all 28 Indian states, with translated names when `lang` is specified.

```json
{
  "states": [
    { "id": "Maharashtra", "name": "महाराष्ट्र" },
    { "id": "Karnataka",   "name": "कर्नाटक" }
  ]
}
```

> `id` is always the English name (used for validation and API calls). `name` is the translated display name.

---

### `GET /api/v1/locations/districts?state=Maharashtra&lang=mr`
Returns districts for a given state in the requested language.

```json
{
  "state": "Maharashtra",
  "districts": [
    { "id": "Pune",   "name": "पुणे"   },
    { "id": "Mumbai", "name": "मुंबई" }
  ]
}
```

---

### `GET /api/v1/soil-types`
Returns the list of supported soil types.

```json
{ "soil_types": ["Black", "Red", "Alluvial", "Laterite", "Sandy", "Clay", "Loamy"] }
```

---

## 📊 Supported Input Values

| Input | Supported Values |
|---|---|
| **Soil Type** | Black, Red, Alluvial, Laterite, Sandy, Clay, Loamy |
| **Season** | Kharif, Rabi, Zaid |
| **Land Unit** | acres, hectares |
| **Language** | en (English), hi (हिन्दी), mr (मराठी) |
| **States** | All 28 Indian states |

### Supported Crops (ML Model)
`Soybean` · `Cotton` · `Jowar` · `Wheat` · `Rice` · `Sugarcane` · `Gram` · `Sunflower` · `Maize` · `Groundnut` · `Tur` · `Onion`

---

## 🤖 ML Model Details

- **Algorithm:** `RandomForestClassifier` (scikit-learn)
- **Model file:** `ml/crop_recommendation/models/crop_rec_v1.0.pkl`
- **Features used:** soil type, season, irrigation availability, regional crop patterns
- **Output:** Ranked crop list with normalized confidence scores (0–100%)
- **Fallback:** If ML confidence is below threshold, template-based ranking is used

---

## 🌍 Translation Architecture

```
┌────────────────────────────────────────────────┐
│              Translation Layers                │
│                                                │
│  1. Static UI (translations.json)              │
│     Labels, buttons, placeholders              │
│     → No API call, instant                     │
│                                                │
│  2. Location Data (frontend/ static JSON)      │
│     states-and-districts-hi.json               │
│     states-and-districts-mr.json               │
│     → Pre-translated offline, loaded at        │
│       startup into memory dict                 │
│                                                │
│  3. Dynamic Content (Sarvam AI mayura:v1)      │
│     Crop names, explanations, summary,         │
│     farm input values (state, district, etc.)  │
│     → Live API call per recommendation         │
│     → Cached via functools.lru_cache           │
└────────────────────────────────────────────────┘
```

---

## ⚙️ LLM Fallback Strategy

When generating crop explanations, the system uses a **primary → fallback** model chain:

```
Primary: google/gemma-4-26b-a4b-it:free
    │  429 / 404 / Timeout?
    ▼
Fallback: nvidia/nemotron-3-super-120b-a12b:free
    │  Still fails?
    ▼
Template-based explanation (graceful degradation — app never crashes)
```

---

## 🔐 Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `SARVAM_API_KEY` | ✅ | — | Sarvam AI key for translation |
| `OPENROUTER_API_KEY` | Optional | — | OpenRouter key for LLM explanations |
| `OPENROUTER_MODEL` | Optional | `gemma-4-26b-a4b-it:free` | Primary LLM model |
| `TAVILY_API_KEY` | Optional | — | Tavily key for crop images |
| `DATABASE_URL` | Optional | `sqlite:///krishi_sathi.db` | Database connection string |
| `ML_MODEL_PATH` | Optional | See config | Path to `.pkl` ML model |
| `ML_CONFIDENCE_THRESHOLD` | Optional | `0.5` | Min confidence for ML output |
| `AGENT_TIMEOUT_SECONDS` | Optional | `30` | Max time for agent pipeline |
| `USE_CREWAI` | Optional | `false` | Enable CrewAI orchestration |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- **[Sarvam AI](https://sarvam.ai)** — `mayura:v1` for accurate Indian language translation
- **[OpenRouter](https://openrouter.ai)** — Access to open-source LLMs
- **[Tavily](https://tavily.com)** — Real-time crop image search
- **[scikit-learn](https://scikit-learn.org)** — ML pipeline
- **[Flask](https://flask.palletsprojects.com)** — Lightweight Python web framework

---

<div align="center">

Made with ❤️ for Indian farmers &nbsp;·&nbsp; Krishi Sathi Phase 1 MVP

</div>
