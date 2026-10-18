# 🌫️ Daily Air Quality Action Agent
### IBM Granite × IBM Cloud × watsonx.ai

> An AI-powered multi-agent system that translates air quality data into **actionable daily insights** for citizens, policymakers, and organizations.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Multi-Agent Orchestrator (orchestrator.py)      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  AQI Data    │  │ Forecasting  │  │  Health Advisory │  │
│  │   Agent      │→ │    Agent     │→ │      Agent       │  │
│  │  (WAQI/OW)   │  │ (7-day pred) │  │ (personalized)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                      ┌──────────────────┐  │
│                                      │  Community Action│  │
│                                      │      Agent       │  │
│                                      │ (policy/campaigns│  │
│                                      └──────────────────┘  │
│                                                             │
│              IBM Granite 3.8B Instruct (watsonx.ai)         │
│        ↑ Narrative synthesis across all 4 agent outputs     │
└─────────────────────────────────────────────────────────────┘
         ↓
  Flask REST API (app.py)
         ↓
  Interactive Dashboard (dashboard.html)
```

---

## 🤖 Agents

| Agent | Responsibility | Key Output |
|-------|---------------|------------|
| **AQI Data Agent** | Fetches real-time AQI from WAQI / OpenWeather APIs | Structured pollutant data + AI interpretation |
| **Forecasting Agent** | Predicts 7-day AQI trends with weather correlation | Daily forecast + risk alerts + commute advisory |
| **Health Advisory Agent** | Personalized health recommendations based on age, health conditions | Immediate actions + activity schedule + diet tips |
| **Community Action Agent** | Policy advisories + public awareness campaigns | Social media content + sector action plans |
| **IBM Granite LLM** | Synthesizes all agent outputs into a coherent executive brief | Natural language narrative + policy summary |

---

## 🚀 Quick Start

### 1. Clone & install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys (optional)
```bash
cp .env.example .env
# Edit .env with your keys:
# - IBM_CLOUD_API_KEY        → IBM watsonx.ai API key
# - IBM_WATSONX_PROJECT_ID  → watsonx.ai project ID
# - WAQI_API_TOKEN           → https://aqicn.org/api/
# - OPENWEATHER_API_KEY      → https://openweathermap.org/api
```
> ⚡ The system works **without any API keys** using simulated realistic data.

### 3. Run CLI analysis
```bash
python main.py Delhi
python main.py "New York"
python main.py Beijing
```

### 4. Launch web dashboard
```bash
python app.py
# Open http://localhost:5000
```

---

## 📡 REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Interactive dashboard |
| `GET /api/health` | GET | System health check |
| `GET /api/aqi/<city>` | GET | Current AQI data |
| `POST /api/full-report/<city>` | POST | Full multi-agent analysis |
| `GET /api/forecast/<city>` | GET | 7-day forecast |
| `POST /api/health-advisory/<city>` | POST | Personalized health advisory |
| `GET /api/community/<city>` | GET | Community action report |
| `GET /api/historical/<city>` | GET | Historical AQI data |
| `GET /api/quick-check/<city>` | GET | Quick AQI summary |
| `GET /api/aqi-categories` | GET | AQI category reference |

### Example: Full analysis
```bash
curl -X POST http://localhost:5000/api/full-report/Delhi \
  -H "Content-Type: application/json" \
  -d '{"profile": {"age": 35, "conditions": ["asthma"], "activity_level": "moderate"}}'
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI/LLM** | IBM Granite 3.8B Instruct via IBM watsonx.ai |
| **Cloud** | IBM Cloud (watsonx.ai endpoint) |
| **Multi-Agent Framework** | Custom Python agent orchestration |
| **AQI Data** | WAQI (World Air Quality Index) API + OpenWeather Air Pollution API |
| **Backend** | Python 3.10+ · Flask 3.x |
| **Dashboard** | Pure HTML/CSS/JS with Chart.js |
| **ML** | Rule-based + statistical forecasting (scikit-learn ready) |

---

## 📁 Project Structure

```
Air quality Action agent/
├── agents/
│   ├── __init__.py
│   ├── aqi_data_agent.py          # Agent 1: AQI data fetching & interpretation
│   ├── health_advisory_agent.py   # Agent 2: Personalized health recommendations
│   ├── forecasting_agent.py       # Agent 3: 7-day AQI prediction & alerts
│   └── community_action_agent.py  # Agent 4: Community & policy action
├── granite_client.py              # IBM Granite LLM client (watsonx.ai)
├── orchestrator.py                # Multi-agent pipeline coordinator
├── app.py                         # Flask REST API server
├── main.py                        # CLI entry point
├── dashboard.html                 # Interactive visualization dashboard
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🌟 Features

### AQI Data Agent
- Live data from WAQI / OpenWeather APIs (city-seeded demo fallback)
- Full pollutant breakdown: PM2.5, PM10, O₃, NO₂, SO₂, CO
- EPA standard AQI categories with color coding
- Historical 7-day and hourly today data
- IBM Granite AI interpretation of conditions

### Health Advisory Agent
- Personalized risk assessment by age, health conditions, activity level
- Mask, exercise, wellness recommendations per AQI level
- Day-part activity safety schedule
- Diet & nutrition anti-pollution tips
- Medication reminders for asthma, COPD, cardiac conditions
- Children and elderly-specific advisories

### Forecasting Agent
- 7-day AQI prediction with weather correlation
- 24-hour diurnal AQI pattern
- Automated risk alerts (ALERT / WARNING / WATCH)
- Pollution hotspot mapping
- Seasonal outlook analysis
- Commute advisory with best travel windows

### Community Action Agent
- 7-sector action plans (transport, energy, waste, green spaces, etc.)
- Policy advisories by AQI severity level (school/construction/traffic)
- Ready-to-post social media content (Twitter, WhatsApp, Instagram)
- Awareness event templates
- NGO contact directory
- IBM Granite AI campaign message and policy brief

### Visualization Dashboard
- Real-time AQI gauge with color-coded needle
- Historical and hourly Chart.js visualizations
- 7-day forecast cards with weather indicators
- Personal activity safety schedule
- Interactive community sector action plans
- Social media copy-to-clipboard content
- Pollution hotspot risk table

---

## 🔑 IBM API Setup

### IBM watsonx.ai (for IBM Granite)
1. Create an IBM Cloud account at [cloud.ibm.com](https://cloud.ibm.com)
2. Create a **watsonx.ai** service instance
3. Generate an **API key** from IAM
4. Create a **project** in watsonx.ai and note the Project ID
5. Add to `.env`:
   ```
   IBM_CLOUD_API_KEY=your_api_key
   IBM_WATSONX_PROJECT_ID=your_project_id
   IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
   ```

### WAQI API (real AQI data)
1. Register at [aqicn.org/api](https://aqicn.org/api/)
2. Get a free token (covers 10,000 queries/day)
3. Add to `.env`: `WAQI_API_TOKEN=your_token`

---

## 📊 Supported Cities (Demo)
Delhi · Mumbai · Beijing · London · New York · Paris · Tokyo · Shanghai · Los Angeles · Chennai · Bangalore · Kolkata *(and any city globally with real API keys)*

---

## 🏆 Problem Statement
**PS #15 — The Daily Air Quality Action Agent**  
Built for: IBM Innovation Challenge  
Stack: IBM Bob + IBM Cloud + IBM Granite ✅
