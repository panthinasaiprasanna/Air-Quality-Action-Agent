"""
AQI Data Agent
Fetches real-time Air Quality Index data from multiple sources,
interprets pollutant levels, and structures data for downstream agents.
"""
import os
import json
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from granite_client import granite_client

load_dotenv()


# AQI Category Breakpoints (EPA Standard)
AQI_CATEGORIES = [
    {"range": (0, 50),   "category": "Good",              "color": "#00e400", "hex": "green",  "icon": "😊"},
    {"range": (51, 100), "category": "Moderate",          "color": "#ffff00", "hex": "yellow", "icon": "😐"},
    {"range": (101,150), "category": "Unhealthy for Sensitive Groups", "color": "#ff7e00", "hex": "orange", "icon": "😷"},
    {"range": (151,200), "category": "Unhealthy",         "color": "#ff0000", "hex": "red",    "icon": "🤢"},
    {"range": (201,300), "category": "Very Unhealthy",    "color": "#8f3f97", "hex": "purple", "icon": "☠️"},
    {"range": (301,500), "category": "Hazardous",         "color": "#7e0023", "hex": "maroon", "icon": "💀"},
]

# Primary pollutants tracked
POLLUTANTS = ["pm25", "pm10", "o3", "no2", "so2", "co"]

POLLUTANT_LABELS = {
    "pm25": "PM2.5 (Fine Particles)",
    "pm10": "PM10 (Coarse Particles)",
    "o3":   "Ozone (O₃)",
    "no2":  "Nitrogen Dioxide (NO₂)",
    "so2":  "Sulfur Dioxide (SO₂)",
    "co":   "Carbon Monoxide (CO)"
}


class AQIDataAgent:
    """
    Agent responsible for fetching, parsing, and interpreting AQI data.
    Supports WAQI API (World Air Quality Index), OpenWeather, and
    simulated data for demonstration when API keys are unavailable.
    """

    def __init__(self):
        self.waqi_token = os.getenv("WAQI_API_TOKEN", "")
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.cache = {}
        self.cache_ttl = 300  # seconds

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch_aqi(self, city: str, user_profile: dict = None) -> dict:
        """
        Main entry point. Fetches AQI for a city and returns a
        structured interpretation with all pollutant details.
        """
        cache_key = city.lower()
        cached = self.cache.get(cache_key)
        if cached and (datetime.now() - cached["timestamp"]).seconds < self.cache_ttl:
            return cached["data"]

        raw = self._fetch_from_api(city)
        structured = self._structure_data(raw, city)
        interpreted = self._interpret_with_granite(structured, user_profile)

        result = {**structured, "ai_interpretation": interpreted}
        self.cache[cache_key] = {"data": result, "timestamp": datetime.now()}
        return result

    def get_historical_aqi(self, city: str, days: int = 7) -> list:
        """Returns simulated historical AQI for trend analysis"""
        history = []
        base_aqi = random.randint(60, 120)
        for i in range(days, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            variation = random.randint(-20, 20)
            aqi = max(10, min(300, base_aqi + variation))
            base_aqi = aqi  # walk forward
            history.append({
                "date": date,
                "aqi": aqi,
                "category": self._get_category(aqi)["category"],
                "dominant_pollutant": random.choice(["pm25", "pm10", "o3"])
            })
        return history

    def get_hourly_aqi(self, city: str) -> list:
        """Returns simulated hourly AQI for the current day"""
        hourly = []
        base = random.randint(50, 150)
        for hour in range(24):
            # Traffic peaks at 8am and 6pm
            peak_factor = 1.3 if hour in range(7, 10) or hour in range(17, 20) else 1.0
            noise = random.randint(-10, 10)
            aqi = max(10, min(350, int(base * peak_factor) + noise))
            hourly.append({
                "hour": f"{hour:02d}:00",
                "aqi": aqi,
                "category": self._get_category(aqi)["category"]
            })
        return hourly

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    def _fetch_from_api(self, city: str) -> dict:
        """Try real APIs, fall back to simulated data"""
        if self.waqi_token and self.waqi_token != "your_world_air_quality_index_token_here":
            data = self._fetch_waqi(city)
            if data:
                return data

        if self.openweather_key and self.openweather_key != "your_openweather_api_key_here":
            data = self._fetch_openweather(city)
            if data:
                return data

        return self._generate_simulated_data(city)

    def _fetch_waqi(self, city: str) -> dict | None:
        """Fetch from World Air Quality Index API"""
        try:
            url = f"https://api.waqi.info/feed/{city}/?token={self.waqi_token}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("status") != "ok":
                return None

            data = payload["data"]
            pollutants = {}
            for p in POLLUTANTS:
                val = data.get("iaqi", {}).get(p, {}).get("v")
                if val is not None:
                    pollutants[p] = round(float(val), 2)

            return {
                "source": "WAQI",
                "aqi": data.get("aqi", 0),
                "city": data.get("city", {}).get("name", city),
                "station": data.get("city", {}).get("name", ""),
                "timestamp": data.get("time", {}).get("iso", datetime.now().isoformat()),
                "pollutants": pollutants,
                "dominant_pollutant": data.get("dominentpol", "pm25"),
                "coordinates": data.get("city", {}).get("geo", [0, 0])
            }
        except Exception as e:
            print(f"WAQI fetch failed: {e}")
            return None

    def _fetch_openweather(self, city: str) -> dict | None:
        """Fetch from OpenWeather Air Pollution API"""
        try:
            # Step 1: geocode the city
            geo_url = (
                f"http://api.openweathermap.org/geo/1.0/direct"
                f"?q={city}&limit=1&appid={self.openweather_key}"
            )
            geo_resp = requests.get(geo_url, timeout=10).json()
            if not geo_resp:
                return None
            lat, lon = geo_resp[0]["lat"], geo_resp[0]["lon"]

            # Step 2: fetch air pollution
            aqi_url = (
                f"http://api.openweathermap.org/data/2.5/air_pollution"
                f"?lat={lat}&lon={lon}&appid={self.openweather_key}"
            )
            aqi_resp = requests.get(aqi_url, timeout=10).json()
            components = aqi_resp["list"][0]["components"]
            ow_aqi = aqi_resp["list"][0]["main"]["aqi"]  # 1-5 scale

            # Convert OpenWeather 1-5 scale to EPA 0-500
            ow_to_epa = {1: 25, 2: 75, 3: 125, 4: 175, 5: 250}
            epa_aqi = ow_to_epa.get(ow_aqi, 100)

            return {
                "source": "OpenWeather",
                "aqi": epa_aqi,
                "city": city.title(),
                "station": city.title(),
                "timestamp": datetime.now().isoformat(),
                "pollutants": {
                    "pm25": round(components.get("pm2_5", 0), 2),
                    "pm10": round(components.get("pm10", 0), 2),
                    "o3":   round(components.get("o3", 0), 2),
                    "no2":  round(components.get("no2", 0), 2),
                    "so2":  round(components.get("so2", 0), 2),
                    "co":   round(components.get("co", 0), 2),
                },
                "dominant_pollutant": "pm25",
                "coordinates": [lat, lon]
            }
        except Exception as e:
            print(f"OpenWeather fetch failed: {e}")
            return None

    def _generate_simulated_data(self, city: str) -> dict:
        """
        Generate realistic simulated AQI data for demonstration.
        Uses city-seeded randomness for consistency within a session.
        """
        seed = sum(ord(c) for c in city.lower())
        random.seed(seed + datetime.now().hour)  # hourly variation

        # City-based base AQI profiles
        city_profiles = {
            "delhi":     (180, 250),
            "mumbai":    (100, 160),
            "beijing":   (150, 220),
            "london":    (30,  70),
            "new york":  (40,  90),
            "paris":     (35,  75),
            "tokyo":     (30,  65),
            "shanghai":  (120, 190),
            "los angeles": (55, 110),
            "chennai":   (80,  140),
            "bangalore": (60,  120),
            "kolkata":   (130, 200),
        }

        lo, hi = city_profiles.get(city.lower(), (50, 150))
        aqi = random.randint(lo, hi)

        # Realistic pollutant concentrations correlated with AQI
        factor = aqi / 100.0
        pollutants = {
            "pm25": round(random.uniform(10, 80) * factor, 2),
            "pm10": round(random.uniform(20, 150) * factor, 2),
            "o3":   round(random.uniform(20, 100) * factor, 2),
            "no2":  round(random.uniform(10, 80) * factor, 2),
            "so2":  round(random.uniform(5, 40) * factor, 2),
            "co":   round(random.uniform(200, 2000) * factor, 2),
        }

        # Dominant pollutant is the highest relative to threshold
        dominant = max(pollutants, key=lambda k: pollutants[k] / (80 if k == "pm25" else 100))

        return {
            "source": "Simulated (Demo)",
            "aqi": aqi,
            "city": city.title(),
            "station": f"{city.title()} Central Station",
            "timestamp": datetime.now().isoformat(),
            "pollutants": pollutants,
            "dominant_pollutant": dominant,
            "coordinates": [28.6, 77.2]  # default to Delhi-ish
        }

    # ------------------------------------------------------------------
    # Structuring & interpretation
    # ------------------------------------------------------------------

    def _structure_data(self, raw: dict, city: str) -> dict:
        """Enrich raw data with category, health implications, etc."""
        aqi = raw.get("aqi", 0)
        cat = self._get_category(aqi)

        return {
            **raw,
            "aqi_category": cat["category"],
            "aqi_color": cat["color"],
            "aqi_icon": cat["icon"],
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pollutant_labels": {
                k: {"value": v, "label": POLLUTANT_LABELS.get(k, k)}
                for k, v in raw.get("pollutants", {}).items()
            },
        }

    def _interpret_with_granite(self, data: dict, user_profile: dict = None) -> str:
        """Use IBM Granite to produce a natural language interpretation"""
        profile_str = ""
        if user_profile:
            profile_str = (
                f"User profile: age={user_profile.get('age', 'adult')}, "
                f"health_conditions={user_profile.get('conditions', 'none')}, "
                f"activity_level={user_profile.get('activity_level', 'moderate')}."
            )

        prompt = (
            f"You are an air quality expert. Provide a concise interpretation of the following air quality data.\n\n"
            f"City: {data['city']}\n"
            f"AQI: {data['aqi']} ({data['aqi_category']})\n"
            f"Dominant Pollutant: {data.get('dominant_pollutant', 'pm25').upper()}\n"
            f"Key Pollutants: {json.dumps(data.get('pollutants', {}))}\n"
            f"{profile_str}\n\n"
            f"Provide: 1) What the AQI level means, 2) Main health risks today, "
            f"3) Two immediate actions citizens should take. Keep it under 100 words."
        )
        return granite_client.generate(prompt)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_category(self, aqi: int) -> dict:
        for cat in AQI_CATEGORIES:
            lo, hi = cat["range"]
            if lo <= aqi <= hi:
                return cat
        return AQI_CATEGORIES[-1]  # Hazardous fallback

    def get_aqi_categories(self) -> list:
        """Return AQI category reference table"""
        return AQI_CATEGORIES

    def get_pollutant_labels(self) -> dict:
        return POLLUTANT_LABELS
