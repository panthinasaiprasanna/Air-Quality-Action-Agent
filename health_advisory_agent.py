"""
Health Advisory Agent
Generates personalized health recommendations based on AQI data,
user profile (age, health conditions, activity level), and location.
"""
import json
from granite_client import granite_client


# Sensitive group definitions
SENSITIVE_GROUPS = {
    "children":     {"age_range": (0, 17),   "risk_multiplier": 1.4},
    "elderly":      {"age_range": (65, 120),  "risk_multiplier": 1.3},
    "pregnant":     {"age_range": (18, 55),   "risk_multiplier": 1.3},
    "respiratory":  {"conditions": ["asthma", "copd", "bronchitis"], "risk_multiplier": 1.5},
    "cardiac":      {"conditions": ["heart disease", "hypertension"], "risk_multiplier": 1.4},
    "diabetic":     {"conditions": ["diabetes"], "risk_multiplier": 1.2},
}

# Mask recommendations by AQI
MASK_GUIDE = {
    (0,  50):  "No mask needed",
    (51, 100): "Optional surgical mask for sensitive groups",
    (101,150): "N95/KN95 recommended for sensitive groups",
    (151,200): "N95/KN95 mandatory for everyone outdoors",
    (201,300): "N95/P100 respirator essential",
    (301,500): "Stay indoors; respirator required if venturing out",
}

# Exercise recommendations by AQI
EXERCISE_GUIDE = {
    (0,  50):  "All outdoor activities safe",
    (51, 100): "Outdoor exercise safe for most; sensitive groups should reduce intensity",
    (101,150): "Reduce prolonged outdoor exertion; sensitive groups avoid outdoor exercise",
    (151,200): "Avoid outdoor exercise; move all activity indoors",
    (201,300): "No outdoor activity; sensitive groups should stay indoors entirely",
    (301,500): "Emergency: stay indoors with sealed windows and air purifier",
}

# Diet & wellness tips by AQI severity
WELLNESS_TIPS = {
    "mild":    ["Stay hydrated", "Eat antioxidant-rich foods (berries, leafy greens)", "Normal sleep schedule"],
    "moderate":["Increase Vitamin C and E intake", "Avoid smoking and secondhand smoke", "Use air purifier indoors",
                "Keep nasal passages moist with saline spray"],
    "severe":  ["Minimize all outdoor exposure", "Take prescribed respiratory medications proactively",
                "Use HEPA air purifier in main living areas", "Monitor blood pressure and oxygen saturation",
                "Consult doctor if experiencing breathing difficulty"],
}


class HealthAdvisoryAgent:
    """
    Agent that delivers personalized, actionable health advice
    based on current AQI data and individual user profiles.
    """

    def __init__(self):
        self.advice_cache = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_advisory(self, aqi_data: dict, user_profile: dict) -> dict:
        """
        Core method: produce a full personalized health advisory.
        Returns structured advisory with Granite-enhanced recommendations.
        """
        aqi = aqi_data.get("aqi", 0)
        city = aqi_data.get("city", "your city")
        category = aqi_data.get("aqi_category", "Unknown")

        # Determine risk level for this user
        risk_level, risk_multiplier = self._assess_personal_risk(aqi, user_profile)
        adjusted_aqi = min(500, int(aqi * risk_multiplier))

        # Build rule-based base recommendations
        base_recs = self._build_base_recommendations(aqi, user_profile, risk_level)

        # Enhance with IBM Granite
        ai_recs = self._granite_advisory(aqi_data, user_profile, risk_level)

        # Compile full advisory
        advisory = {
            "city": city,
            "aqi": aqi,
            "aqi_category": category,
            "user_profile": user_profile,
            "risk_level": risk_level,
            "adjusted_aqi_for_profile": adjusted_aqi,
            "sensitive_group": self._identify_sensitive_group(user_profile),
            "immediate_actions": base_recs["immediate_actions"],
            "mask_recommendation": self._get_guide(MASK_GUIDE, aqi),
            "exercise_recommendation": self._get_guide(EXERCISE_GUIDE, aqi),
            "wellness_tips": base_recs["wellness_tips"],
            "indoor_air_quality_tips": self._indoor_tips(aqi),
            "children_advisory": self._children_advisory(aqi, user_profile),
            "medication_reminder": self._medication_reminder(aqi, user_profile),
            "ai_recommendation": ai_recs,
            "emergency_contacts": self._emergency_contacts(city),
            "next_safe_window": self._estimate_safe_window(aqi),
        }
        return advisory

    def get_activity_schedule(self, aqi_data: dict, user_profile: dict) -> list:
        """Generate a safe hourly activity schedule for the day"""
        aqi = aqi_data.get("aqi", 100)
        schedule = []

        hourly_template = [
            ("06:00–08:00", "Morning"),
            ("08:00–12:00", "Late Morning"),
            ("12:00–14:00", "Afternoon"),
            ("14:00–17:00", "Late Afternoon"),
            ("17:00–19:00", "Evening"),
            ("19:00–21:00", "Night"),
        ]

        for time_slot, period in hourly_template:
            # Traffic peaks make mornings and evenings worse
            period_aqi = aqi * 1.2 if period in ("Morning", "Evening") else aqi * 0.9
            period_aqi = int(period_aqi)
            safety = self._period_safety(period_aqi, user_profile)
            schedule.append({
                "time": time_slot,
                "period": period,
                "estimated_aqi": period_aqi,
                "safety_rating": safety["rating"],
                "recommendation": safety["recommendation"],
                "outdoor_ok": safety["outdoor_ok"],
            })

        return schedule

    def get_diet_recommendations(self, aqi: int) -> list:
        """Return dietary recommendations to combat pollution effects"""
        tips = []
        if aqi > 50:
            tips.extend([
                "🥦 Eat cruciferous vegetables (broccoli, kale) — boost lung defense enzymes",
                "🍊 Increase Vitamin C intake — neutralizes free radicals from pollution",
                "🫁 Omega-3 fatty acids (fish, walnuts) — reduce airway inflammation",
            ])
        if aqi > 100:
            tips.extend([
                "🫐 Antioxidant-rich berries — protect against oxidative stress",
                "🍵 Green tea — anti-inflammatory polyphenols",
                "💧 Drink at least 8–10 glasses of water — helps flush pollutants",
                "🧄 Garlic and onions — natural expectorants",
            ])
        if aqi > 150:
            tips.extend([
                "🚫 Avoid fried/processed foods — worsen inflammation",
                "🚫 Reduce dairy if experiencing congestion",
                "💊 Consider Vitamin D supplement (stay indoors = less sunlight)",
            ])
        if not tips:
            tips.append("✅ Normal balanced diet is sufficient today.")
        return tips

    # ------------------------------------------------------------------
    # Risk assessment
    # ------------------------------------------------------------------

    def _assess_personal_risk(self, aqi: int, profile: dict) -> tuple[str, float]:
        """Assess personal risk level and return (level, multiplier)"""
        age = profile.get("age", 30)
        conditions = [c.lower() for c in profile.get("conditions", [])]

        multiplier = 1.0

        # Age-based risk
        if age < 18:
            multiplier = max(multiplier, 1.4)
        elif age > 65:
            multiplier = max(multiplier, 1.3)

        # Condition-based risk
        for group, info in SENSITIVE_GROUPS.items():
            if "conditions" in info:
                if any(cond in conditions for cond in info["conditions"]):
                    multiplier = max(multiplier, info["risk_multiplier"])

        if profile.get("pregnant", False):
            multiplier = max(multiplier, 1.3)

        adjusted = aqi * multiplier

        if adjusted <= 50:
            return "Low", multiplier
        elif adjusted <= 100:
            return "Moderate", multiplier
        elif adjusted <= 150:
            return "High", multiplier
        elif adjusted <= 200:
            return "Very High", multiplier
        else:
            return "Extreme", multiplier

    def _identify_sensitive_group(self, profile: dict) -> str:
        """Identify if user belongs to a sensitive group"""
        age = profile.get("age", 30)
        conditions = [c.lower() for c in profile.get("conditions", [])]

        groups = []
        if age < 18:
            groups.append("Children")
        if age > 65:
            groups.append("Elderly")
        if profile.get("pregnant", False):
            groups.append("Pregnant")
        respiratory = ["asthma", "copd", "bronchitis"]
        if any(c in conditions for c in respiratory):
            groups.append("Respiratory condition")
        cardiac = ["heart disease", "hypertension"]
        if any(c in conditions for c in cardiac):
            groups.append("Cardiac condition")
        if "diabetes" in conditions:
            groups.append("Diabetic")

        return ", ".join(groups) if groups else "General population"

    # ------------------------------------------------------------------
    # Recommendation builders
    # ------------------------------------------------------------------

    def _build_base_recommendations(self, aqi: int, profile: dict, risk_level: str) -> dict:
        """Build structured rule-based recommendations"""
        immediate_actions = []

        if aqi <= 50:
            immediate_actions = [
                "✅ Air quality is good — enjoy outdoor activities freely",
                "🌿 Great day for a morning walk or run",
                "🪟 Open windows for natural ventilation",
            ]
            wellness = WELLNESS_TIPS["mild"]
        elif aqi <= 100:
            immediate_actions = [
                "⚠️ Air quality is acceptable but some pollutants may concern sensitive groups",
                "🚶 Reduce intensity of outdoor exercise if you feel irritation",
                "🏠 Keep air purifier running indoors",
            ]
            wellness = WELLNESS_TIPS["mild"] + WELLNESS_TIPS["moderate"][:2]
        elif aqi <= 150:
            immediate_actions = [
                "😷 Wear N95/KN95 mask if going outdoors",
                "🏠 Sensitive groups (children, elderly, asthma) should stay indoors",
                "🪟 Keep windows and doors closed",
                "🚗 Avoid idling in traffic — roll up car windows",
            ]
            wellness = WELLNESS_TIPS["moderate"]
        elif aqi <= 200:
            immediate_actions = [
                "🚨 Unhealthy air — minimize outdoor exposure for ALL groups",
                "😷 Wear N95 mask; avoid surgical masks as they are insufficient",
                "🏠 Stay indoors with HEPA air purifier",
                "🧒 Children should not attend outdoor school activities today",
                "🏃 Cancel all outdoor sports and exercise",
            ]
            wellness = WELLNESS_TIPS["severe"]
        else:
            immediate_actions = [
                "🆘 HAZARDOUS — Emergency air quality conditions",
                "🏠 STAY INDOORS — do not go outside without respirator",
                "🪟 Seal gaps in doors/windows with damp cloth if no AC",
                "🏥 Seek medical attention immediately if breathing difficulties occur",
                "📵 Report any industrial violations to local authorities",
            ]
            wellness = WELLNESS_TIPS["severe"]

        # Add profile-specific actions
        age = profile.get("age", 30)
        conditions = profile.get("conditions", [])
        activity = profile.get("activity_level", "moderate")

        if age < 18 and aqi > 100:
            immediate_actions.append("👧 Keep children away from busy roads and playgrounds today")
        if age > 65 and aqi > 100:
            immediate_actions.append("👴 Elderly: avoid stairs and heavy physical effort outdoors")
        if "asthma" in [c.lower() for c in conditions] and aqi > 100:
            immediate_actions.append("💊 Asthma patients: carry rescue inhaler; consider preventive dose")
        if activity == "athlete" and aqi > 100:
            immediate_actions.append("🏋️ Athletes: move training indoors; outdoor competition not advised")

        return {"immediate_actions": immediate_actions, "wellness_tips": wellness}

    def _indoor_tips(self, aqi: int) -> list:
        """Return indoor air quality improvement tips"""
        tips = ["🌿 Place air-purifying plants (snake plant, peace lily) indoors"]
        if aqi > 50:
            tips += [
                "💨 Run HEPA air purifier in bedroom and living room",
                "🚫 Avoid cooking methods that produce smoke (grilling, deep frying)",
                "🕯️ Avoid candles, incense, and air freshener sprays",
            ]
        if aqi > 100:
            tips += [
                "🪟 Seal door/window gaps with weatherstripping",
                "🔄 Recirculate car AC — do not use fresh air intake in heavy traffic",
                "👕 Change clothes and wash hands when coming in from outdoors",
            ]
        if aqi > 150:
            tips += [
                "🏠 Designate one 'clean room' with the best air purifier",
                "💧 Use a humidifier at 40–50% to trap particulates",
                "🛏️ Place air purifier near sleeping area — we breathe deeply at night",
            ]
        return tips

    def _children_advisory(self, aqi: int, profile: dict) -> str:
        """Specific advisory if household has children"""
        has_child = profile.get("has_children", False) or profile.get("age", 30) < 18
        if not has_child:
            return ""
        if aqi <= 50:
            return "Children can play outdoors freely today."
        elif aqi <= 100:
            return "Children may play outdoors but avoid dusty areas. Bring them in if they start coughing."
        elif aqi <= 150:
            return "Limit children's outdoor time to under 30 minutes. Avoid playgrounds near roads."
        elif aqi <= 200:
            return "Keep children indoors. Cancel outdoor school activities. Use air purifier in children's room."
        else:
            return "EMERGENCY: Keep children strictly indoors. Close all windows. Seek shelter in sealed room."

    def _medication_reminder(self, aqi: int, profile: dict) -> str:
        """Return medication reminder for relevant health conditions"""
        conditions = [c.lower() for c in profile.get("conditions", [])]
        reminders = []
        if "asthma" in conditions and aqi > 100:
            reminders.append("Asthma: use preventive inhaler before any outdoor exposure")
        if "copd" in conditions and aqi > 100:
            reminders.append("COPD: increase monitoring frequency; have bronchodilator ready")
        if "heart disease" in conditions and aqi > 150:
            reminders.append("Cardiac: avoid exertion; consult cardiologist if symptoms worsen")
        if "hypertension" in conditions and aqi > 100:
            reminders.append("Hypertension: PM2.5 raises blood pressure — check BP twice today")
        return "; ".join(reminders) if reminders else ""

    def _emergency_contacts(self, city: str) -> dict:
        return {
            "emergency": "112",
            "health_helpline": "104",
            "pollution_control_board": "1800-11-XXXX (check local PCB)",
            "nearest_hospital": f"Search 'hospitals near {city}' on Google Maps",
        }

    def _estimate_safe_window(self, aqi: int) -> str:
        """Estimate when outdoor activity will next be safe"""
        if aqi <= 50:
            return "Safe all day"
        elif aqi <= 100:
            return "Safe for most people — early morning (5–7 AM) is best"
        elif aqi <= 150:
            return "Early morning before sunrise (5–6 AM) may be acceptable for healthy adults"
        elif aqi <= 200:
            return "Not safe today — monitor tomorrow morning"
        else:
            return "Multiple days of poor air quality expected — stay indoors"

    def _period_safety(self, aqi: int, profile: dict) -> dict:
        _, multiplier = self._assess_personal_risk(aqi, profile)
        adj = aqi * multiplier
        if adj <= 50:
            return {"rating": "Safe",    "outdoor_ok": True,  "recommendation": "Outdoor activity is safe"}
        elif adj <= 100:
            return {"rating": "Caution", "outdoor_ok": True,  "recommendation": "Reduce intensity; monitor symptoms"}
        elif adj <= 150:
            return {"rating": "Limit",   "outdoor_ok": False, "recommendation": "Sensitive groups stay indoors"}
        else:
            return {"rating": "Avoid",   "outdoor_ok": False, "recommendation": "All groups should avoid outdoors"}

    # ------------------------------------------------------------------
    # Granite-enhanced advisory
    # ------------------------------------------------------------------

    def _granite_advisory(self, aqi_data: dict, profile: dict, risk_level: str) -> str:
        """Generate personalized AI advisory using IBM Granite"""
        age = profile.get("age", 30)
        conditions = profile.get("conditions", [])
        activity = profile.get("activity_level", "moderate")

        prompt = (
            f"You are a personalized health advisor specializing in air quality impacts.\n\n"
            f"Generate a health recommendation for the following person:\n"
            f"- Age: {age}\n"
            f"- Health conditions: {', '.join(conditions) if conditions else 'None'}\n"
            f"- Activity level: {activity}\n"
            f"- Location: {aqi_data.get('city', 'Unknown')}\n"
            f"- Current AQI: {aqi_data.get('aqi', 100)} ({aqi_data.get('aqi_category', 'Moderate')})\n"
            f"- Dominant pollutant: {aqi_data.get('dominant_pollutant', 'PM2.5')}\n"
            f"- Personal risk level: {risk_level}\n\n"
            f"Provide: specific daily schedule adjustments, dietary advice, and any medication notes. "
            f"Be practical and actionable. Under 120 words."
        )
        return granite_client.generate(prompt)

    def _get_guide(self, guide: dict, aqi: int) -> str:
        """Match AQI to the appropriate guide entry"""
        for (lo, hi), text in guide.items():
            if lo <= aqi <= hi:
                return text
        return guide[max(guide.keys())]
