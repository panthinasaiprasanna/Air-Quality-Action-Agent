"""
Forecasting Agent
Predicts future AQI trends using time-series analysis,
weather pattern correlation, and IBM Granite for narrative forecasts.
"""
import random
import json
from datetime import datetime, timedelta
from granite_client import granite_client


# Seasonal multipliers (Northern Hemisphere)
SEASONAL_FACTORS = {
    1:  1.3,  # Jan — winter inversions
    2:  1.25,
    3:  1.0,
    4:  0.85,
    5:  0.8,  # May — spring, good dispersion
    6:  0.9,  # Jun — ozone season starts
    7:  1.0,
    8:  1.0,
    9:  0.9,
    10: 1.1,
    11: 1.2,  # Nov — crop burning + onset of winter
    12: 1.35, # Dec — worst winter pollution
}

# Weather condition impact on AQI
WEATHER_AQI_IMPACT = {
    "sunny":       0.9,   # UV breaks down some pollutants
    "windy":       0.7,   # wind disperses pollutants
    "rainy":       0.6,   # rain washes out particles
    "calm":        1.2,   # stagnant air traps pollutants
    "foggy":       1.3,   # fog traps near-surface particles
    "hot":         1.1,   # heat increases ozone formation
    "cloudy":      1.0,
    "snow":        0.8,
}

RISK_THRESHOLDS = {
    "critical":    {"aqi": 200, "label": "Hazardous", "action": "ALERT"},
    "very_high":   {"aqi": 150, "label": "Very Unhealthy", "action": "WARNING"},
    "high":        {"aqi": 100, "label": "Unhealthy", "action": "WATCH"},
    "moderate":    {"aqi": 50,  "label": "Moderate",  "action": "ADVISORY"},
}


class ForecastingAgent:
    """
    Agent responsible for predicting AQI trends, issuing early warnings,
    and generating AI-powered forecast narratives using IBM Granite.
    """

    def __init__(self):
        self.forecast_cache = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_forecast(self, aqi_data: dict, historical: list = None) -> dict:
        """
        Generate a 7-day AQI forecast with risk alerts and narrative.
        """
        current_aqi = aqi_data.get("aqi", 100)
        city = aqi_data.get("city", "Unknown")

        daily_forecast = self._forecast_7day(current_aqi, city)
        hourly_forecast = self._forecast_24h(current_aqi)
        risk_alerts = self._generate_alerts(daily_forecast, city)
        trend = self._analyze_trend(daily_forecast)
        ai_narrative = self._granite_forecast(aqi_data, daily_forecast, trend)

        return {
            "city": city,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_aqi": current_aqi,
            "trend": trend,
            "daily_forecast": daily_forecast,
            "hourly_forecast": hourly_forecast,
            "risk_alerts": risk_alerts,
            "worst_day": self._find_worst_day(daily_forecast),
            "best_day": self._find_best_day(daily_forecast),
            "ai_narrative": ai_narrative,
            "commute_advisory": self._commute_advisory(hourly_forecast),
            "weekly_summary": self._weekly_summary(daily_forecast),
        }

    def get_pollution_hotspots(self, city: str) -> list:
        """Return simulated pollution hotspot data for the city"""
        hotspot_templates = [
            {"zone": "Industrial Area",    "factor": 1.8, "pollutant": "SO₂, NOₓ"},
            {"zone": "Highway Corridor",   "factor": 1.6, "pollutant": "NO₂, CO"},
            {"zone": "City Centre",        "factor": 1.3, "pollutant": "PM2.5, CO"},
            {"zone": "Construction Zone",  "factor": 1.5, "pollutant": "PM10"},
            {"zone": "Residential Area",   "factor": 1.0, "pollutant": "PM2.5"},
            {"zone": "Green Belt/Parks",   "factor": 0.6, "pollutant": "Low"},
        ]
        return [
            {
                **hs,
                "zone": f"{city.title()} {hs['zone']}",
                "risk_level": ("High" if hs["factor"] > 1.5
                               else "Moderate" if hs["factor"] > 1.1
                               else "Low" if hs["factor"] > 0.8
                               else "Very Low"),
                "avoidance_tip": self._avoidance_tip(hs["zone"])
            }
            for hs in hotspot_templates
        ]

    def get_seasonal_outlook(self) -> dict:
        """Return a seasonal air quality outlook"""
        month = datetime.now().month
        season = self._get_season(month)
        factor = SEASONAL_FACTORS[month]

        messages = {
            "Winter": "Winter inversions trap pollutants near ground level. Expect consistently higher AQI.",
            "Spring": "Improving conditions as winds pick up. Pollen adds to particle load.",
            "Summer": "Ozone levels rise due to UV radiation and heat. Watch for afternoon peaks.",
            "Autumn": "Crop residue burning may spike AQI significantly in agricultural regions.",
        }

        return {
            "season": season,
            "month": datetime.now().strftime("%B"),
            "seasonal_factor": factor,
            "outlook": messages.get(season, "Seasonal conditions vary."),
            "risk_trend": "↑ Higher" if factor > 1.1 else "→ Average" if factor > 0.9 else "↓ Lower",
        }

    # ------------------------------------------------------------------
    # Forecasting engine
    # ------------------------------------------------------------------

    def _forecast_7day(self, current_aqi: int, city: str) -> list:
        """Generate 7-day forecast using trend + seasonal + weather simulation"""
        forecast = []
        month = datetime.now().month
        seasonal = SEASONAL_FACTORS.get(month, 1.0)

        aqi = current_aqi
        for day_offset in range(1, 8):
            date = (datetime.now() + timedelta(days=day_offset))
            weather = random.choice(list(WEATHER_AQI_IMPACT.keys()))
            weather_factor = WEATHER_AQI_IMPACT[weather]

            # Random walk with seasonal constraint
            drift = random.uniform(-0.08, 0.08)
            aqi = max(10, min(400, int(aqi * (1 + drift) * weather_factor * seasonal)))

            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "aqi": aqi,
                "category": self._category_label(aqi),
                "color": self._category_color(aqi),
                "weather": weather.title(),
                "weather_factor": weather_factor,
                "confidence": round(max(0.5, 0.95 - day_offset * 0.05), 2),
                "safe_for_outdoor": aqi <= 100,
            })

        return forecast

    def _forecast_24h(self, current_aqi: int) -> list:
        """Generate 24-hour hourly forecast"""
        forecast = []
        aqi = current_aqi

        # Diurnal pattern: higher in morning and evening rush hours
        diurnal = {
            0: 0.85, 1: 0.80, 2: 0.78, 3: 0.78, 4: 0.80, 5: 0.85,
            6: 0.95, 7: 1.15, 8: 1.25, 9: 1.10, 10: 1.05, 11: 1.00,
            12: 0.98, 13: 1.00, 14: 1.05, 15: 1.10, 16: 1.15, 17: 1.25,
            18: 1.20, 19: 1.10, 20: 1.00, 21: 0.95, 22: 0.90, 23: 0.87,
        }

        for hour in range(24):
            h_aqi = max(10, min(400, int(current_aqi * diurnal[hour] + random.randint(-5, 5))))
            forecast.append({
                "hour": f"{hour:02d}:00",
                "aqi": h_aqi,
                "category": self._category_label(h_aqi),
                "color": self._category_color(h_aqi),
                "safe": h_aqi <= 100,
            })

        return forecast

    def _generate_alerts(self, forecast: list, city: str) -> list:
        """Generate risk alerts for days exceeding thresholds"""
        alerts = []
        for day in forecast:
            aqi = day["aqi"]
            for risk_key, threshold in RISK_THRESHOLDS.items():
                if aqi >= threshold["aqi"]:
                    alerts.append({
                        "date": day["date"],
                        "day_name": day["day_name"],
                        "aqi": aqi,
                        "severity": threshold["action"],
                        "label": threshold["label"],
                        "message": self._alert_message(aqi, day["day_name"], city),
                    })
                    break  # highest matching threshold only
        return sorted(alerts, key=lambda x: x["aqi"], reverse=True)

    def _alert_message(self, aqi: int, day: str, city: str) -> str:
        if aqi >= 200:
            return f"🆘 HAZARDOUS conditions expected {day} in {city}. Stay indoors. Seek medical help if symptoms occur."
        elif aqi >= 150:
            return f"🚨 Very unhealthy air expected {day} in {city}. Avoid outdoor activities. N95 mandatory."
        elif aqi >= 100:
            return f"⚠️ Unhealthy air quality expected {day} in {city}. Sensitive groups should stay indoors."
        else:
            return f"📢 Moderate air quality expected {day} in {city}. Sensitive groups take precautions."

    # ------------------------------------------------------------------
    # Analysis helpers
    # ------------------------------------------------------------------

    def _analyze_trend(self, forecast: list) -> dict:
        """Determine overall trend from 7-day forecast"""
        aqis = [d["aqi"] for d in forecast]
        avg = sum(aqis) / len(aqis)
        first_half = sum(aqis[:3]) / 3
        second_half = sum(aqis[4:]) / 3

        if second_half > first_half * 1.1:
            direction = "Worsening"
            icon = "📈"
        elif second_half < first_half * 0.9:
            direction = "Improving"
            icon = "📉"
        else:
            direction = "Stable"
            icon = "➡️"

        return {
            "direction": direction,
            "icon": icon,
            "weekly_avg": round(avg, 1),
            "peak_aqi": max(aqis),
            "min_aqi": min(aqis),
        }

    def _find_worst_day(self, forecast: list) -> dict:
        return max(forecast, key=lambda x: x["aqi"])

    def _find_best_day(self, forecast: list) -> dict:
        return min(forecast, key=lambda x: x["aqi"])

    def _weekly_summary(self, forecast: list) -> str:
        bad_days = [d for d in forecast if d["aqi"] > 150]
        good_days = [d for d in forecast if d["aqi"] <= 50]
        if len(bad_days) >= 3:
            return f"Difficult week ahead — {len(bad_days)} days of very poor air quality expected."
        elif len(good_days) >= 3:
            return f"Relatively clean week — {len(good_days)} days of good air quality expected."
        else:
            return "Mixed air quality expected this week — stay updated daily."

    def _commute_advisory(self, hourly: list) -> dict:
        """Identify best and worst commute windows"""
        morning = [h for h in hourly if 6 <= int(h["hour"].split(":")[0]) <= 9]
        evening = [h for h in hourly if 17 <= int(h["hour"].split(":")[0]) <= 20]

        best_morning = min(morning, key=lambda x: x["aqi"]) if morning else {}
        best_evening = min(evening, key=lambda x: x["aqi"]) if evening else {}

        return {
            "morning_commute_aqi": best_morning.get("aqi", "N/A"),
            "morning_best_time": best_morning.get("hour", "N/A"),
            "evening_commute_aqi": best_evening.get("aqi", "N/A"),
            "evening_best_time": best_evening.get("hour", "N/A"),
            "advice": (
                "Use public transport today — car windows up and AC on recirculate."
                if best_morning.get("aqi", 0) > 100
                else "Normal commute is fine — enjoy the fresh air!"
            )
        }

    # ------------------------------------------------------------------
    # Granite narrative
    # ------------------------------------------------------------------

    def _granite_forecast(self, aqi_data: dict, forecast: list, trend: dict) -> str:
        """Generate a 7-day forecast narrative using IBM Granite"""
        forecast_summary = [
            f"{d['day_name']} ({d['date']}): AQI {d['aqi']} ({d['category']}, {d['weather']})"
            for d in forecast
        ]

        prompt = (
            f"You are an environmental meteorologist. Based on the following 7-day AQI forecast for "
            f"{aqi_data.get('city', 'the city')}, write a brief forecast bulletin.\n\n"
            f"Current AQI: {aqi_data.get('aqi', 100)} ({aqi_data.get('aqi_category', 'Moderate')})\n"
            f"Forecast trend: {trend['direction']}\n"
            f"7-Day Forecast:\n" + "\n".join(forecast_summary) + "\n\n"
            f"Write: 1) Overall outlook, 2) Worst risk period, 3) Best day for outdoor activities, "
            f"4) One preventive measure. Keep under 100 words."
        )
        return granite_client.generate(prompt)

    # ------------------------------------------------------------------
    # Category utilities
    # ------------------------------------------------------------------

    def _category_label(self, aqi: int) -> str:
        if aqi <= 50:   return "Good"
        if aqi <= 100:  return "Moderate"
        if aqi <= 150:  return "USG"
        if aqi <= 200:  return "Unhealthy"
        if aqi <= 300:  return "Very Unhealthy"
        return "Hazardous"

    def _category_color(self, aqi: int) -> str:
        if aqi <= 50:   return "#00e400"
        if aqi <= 100:  return "#ffff00"
        if aqi <= 150:  return "#ff7e00"
        if aqi <= 200:  return "#ff0000"
        if aqi <= 300:  return "#8f3f97"
        return "#7e0023"

    def _get_season(self, month: int) -> str:
        if month in (12, 1, 2):   return "Winter"
        if month in (3, 4, 5):    return "Spring"
        if month in (6, 7, 8):    return "Summer"
        return "Autumn"

    def _avoidance_tip(self, zone: str) -> str:
        tips = {
            "Industrial Area":   "Avoid during morning and evening when emissions peak",
            "Highway Corridor":  "Use alternate routes or travel during off-peak hours",
            "City Centre":       "Walk through parks when possible; avoid ground-level vehicle exhaust",
            "Construction Zone": "Use dust mask and keep distance from active construction",
            "Residential Area":  "Normal precautions; watch for neighbourhood burning",
            "Green Belt/Parks":  "Best zone — recommended for outdoor exercise",
        }
        for key, tip in tips.items():
            if key in zone:
                return tip
        return "Stay aware of local pollution sources"
