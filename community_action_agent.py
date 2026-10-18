"""
Community Action Agent
Drives public awareness, policy advisory, and collective action campaigns.
Generates localized community-level recommendations and policy summaries.
"""
import json
from datetime import datetime
from granite_client import granite_client


# Community action templates by sector
COMMUNITY_ACTIONS = {
    "transport": {
        "icon": "🚗",
        "title": "Sustainable Transport",
        "actions": [
            "Organize neighbourhood carpooling groups via WhatsApp/Telegram",
            "Promote work-from-home days on predicted high-pollution days",
            "Switch short trips (< 2km) to walking or cycling",
            "Use electric or CNG public transport options",
            "Coordinate office shuttle services to reduce individual car trips",
        ]
    },
    "energy": {
        "icon": "⚡",
        "title": "Clean Energy Use",
        "actions": [
            "Switch to solar water heaters and LED lighting",
            "Avoid generators during peak pollution hours — use UPS instead",
            "Report illegal coal/wood burning to pollution control authorities",
            "Advocate for renewable energy procurement in residential societies",
            "Install solar panels through government subsidy schemes",
        ]
    },
    "waste": {
        "icon": "♻️",
        "title": "Waste Management",
        "actions": [
            "Stop open burning of waste — report violators to municipal bodies",
            "Compost organic waste at home or community level",
            "Organize community clean-up and segregation drives",
            "Petition for designated e-waste collection points",
            "Reduce single-use plastics in neighbourhood events",
        ]
    },
    "green_spaces": {
        "icon": "🌳",
        "title": "Urban Green Spaces",
        "actions": [
            "Plant pollution-absorbing trees (neem, peepal, arjun) in neighbourhoods",
            "Create vertical gardens on building facades",
            "Advocate for green buffer zones near industrial areas",
            "Maintain and expand parks in residential societies",
            "Support urban forestry initiatives by local municipal bodies",
        ]
    },
    "awareness": {
        "icon": "📢",
        "title": "Public Awareness",
        "actions": [
            "Share daily AQI updates on resident WhatsApp/Telegram groups",
            "Conduct school awareness programs on air quality and health",
            "Organize 'Clean Air Week' events in your locality",
            "Display AQI boards in community centres, schools, and clinics",
            "Engage local media and influencers for clean air campaigns",
        ]
    },
    "industrial": {
        "icon": "🏭",
        "title": "Industrial Accountability",
        "actions": [
            "Report visible industrial smoke/emissions to Pollution Control Board",
            "Demand public disclosure of factory emission reports",
            "Participate in Environmental Impact Assessment (EIA) public hearings",
            "Form Citizens' Air Quality Monitoring Committees",
            "Advocate for stricter penalties for emission violations",
        ]
    },
    "agriculture": {
        "icon": "🌾",
        "title": "Agricultural Practices",
        "actions": [
            "Promote no-burn crop residue management techniques",
            "Advocate for subsidies on Happy Seeder machines",
            "Organize farmer awareness on biochar and compost alternatives",
            "Report illegal stubble burning to district authorities",
            "Support community biogas plants from crop waste",
        ]
    }
}

# Policy advisories by AQI level
POLICY_ADVISORIES = {
    "good": {
        "status": "Green Status",
        "government_actions": ["Routine monitoring", "Maintain current regulations"],
        "school_policy": "Normal school operations",
        "construction_policy": "All construction activities permitted",
        "traffic_policy": "Normal traffic management",
    },
    "moderate": {
        "status": "Yellow Status",
        "government_actions": [
            "Issue public advisories",
            "Alert sensitive-group health facilities",
        ],
        "school_policy": "Reduce outdoor sports duration",
        "construction_policy": "Dust suppression mandatory at construction sites",
        "traffic_policy": "Encourage public transport use",
    },
    "usg": {
        "status": "Orange Status",
        "government_actions": [
            "Activate Air Quality Action Plan (AQAP)",
            "Deploy additional monitoring teams",
            "Issue health alerts for sensitive groups",
        ],
        "school_policy": "Cancel outdoor physical education classes",
        "construction_policy": "Demolition and heavy dust work to be suspended",
        "traffic_policy": "Implement odd-even vehicle scheme in affected zones",
    },
    "unhealthy": {
        "status": "Red Status — Emergency",
        "government_actions": [
            "Invoke Emergency Response measures",
            "Close polluting industries temporarily",
            "Enforce strict no-burning orders (crop, garbage, fireworks)",
            "Deploy mobile health units to affected areas",
        ],
        "school_policy": "Switch to online/remote schooling",
        "construction_policy": "Halt all outdoor construction activities",
        "traffic_policy": "Implement vehicle ban; activate public transport surge",
    },
    "very_unhealthy": {
        "status": "Purple Status — Severe Emergency",
        "government_actions": [
            "Declare public health emergency",
            "Order industrial shutdowns in affected zones",
            "Mandatory work-from-home for all non-essential services",
            "Open emergency health camps and distribute masks free",
        ],
        "school_policy": "Mandatory school closures",
        "construction_policy": "All outdoor work banned",
        "traffic_policy": "Emergency traffic restrictions; free public transport",
    },
    "hazardous": {
        "status": "Maroon Status — Extreme Emergency",
        "government_actions": [
            "Invoke Disaster Management Act provisions",
            "Mass evacuation advisory for vulnerable populations",
            "Air Quality war room activated",
            "International assistance may be sought",
        ],
        "school_policy": "Indefinite school closures",
        "construction_policy": "All work banned; enforce under penalty",
        "traffic_policy": "Essential vehicles only; martial enforcement if needed",
    },
}

# Social media templates for campaigns
SOCIAL_MEDIA_TEMPLATES = {
    "twitter": "🌫️ AQI in {city} is {aqi} ({category}) today. {action} #CleanAir #AQI #BreatheSafe",
    "whatsapp": "🚨 Air Quality Alert for {city}!\n\nAQI: {aqi} ({category})\n\n✅ What you can do:\n{actions}\n\nStay safe! Share this with your neighbours. 🙏",
    "instagram": "Today's AQI in {city}: {aqi} 🌫️\n\nThe air we breathe affects us all. Here's what you can do:\n{actions}\n\n#CleanAir #AirQuality #HealthyLiving",
}


class CommunityActionAgent:
    """
    Agent that drives community-level awareness, policy recommendations,
    and collective action campaigns based on current AQI conditions.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_community_report(self, aqi_data: dict) -> dict:
        """
        Generate a comprehensive community action and policy report.
        """
        aqi = aqi_data.get("aqi", 100)
        city = aqi_data.get("city", "your city")
        category = aqi_data.get("aqi_category", "Moderate")

        priority_actions = self._get_priority_actions(aqi)
        policy_advisory = self._get_policy_advisory(aqi)
        social_content = self._generate_social_content(aqi_data)
        ai_campaign = self._granite_campaign(aqi_data)
        ngo_orgs = self._get_ngo_contacts(city)
        policy_summary = self._granite_policy_summary(aqi_data)

        return {
            "city": city,
            "aqi": aqi,
            "aqi_category": category,
            "alert_level": policy_advisory["status"],
            "priority_actions": priority_actions,
            "all_sector_actions": self._get_all_actions(),
            "policy_advisory": policy_advisory,
            "social_media_content": social_content,
            "ai_campaign_message": ai_campaign,
            "ai_policy_summary": policy_summary,
            "ngo_contacts": ngo_orgs,
            "reporting_channels": self._reporting_channels(city),
            "awareness_events": self._generate_awareness_events(aqi, city),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_sector_actions(self, sector: str) -> dict:
        """Get actions for a specific sector"""
        return COMMUNITY_ACTIONS.get(sector, {})

    def get_campaign_kit(self, aqi_data: dict) -> dict:
        """Generate a complete awareness campaign kit"""
        aqi = aqi_data.get("aqi", 100)
        city = aqi_data.get("city", "your city")
        category = aqi_data.get("aqi_category", "Moderate")

        return {
            "campaign_theme": self._campaign_theme(aqi),
            "key_messages": self._key_messages(aqi, city),
            "target_audience": ["Residents", "Schools", "Businesses", "Local Government"],
            "recommended_channels": self._recommended_channels(aqi),
            "social_posts": self._generate_social_content(aqi_data),
            "petition_template": self._petition_template(aqi, city),
            "event_ideas": self._generate_awareness_events(aqi, city),
        }

    # ------------------------------------------------------------------
    # Action generation
    # ------------------------------------------------------------------

    def _get_priority_actions(self, aqi: int) -> list:
        """Return top 5 most relevant community actions based on AQI"""
        if aqi <= 50:
            sectors = ["green_spaces", "awareness"]
        elif aqi <= 100:
            sectors = ["transport", "awareness", "green_spaces"]
        elif aqi <= 150:
            sectors = ["transport", "waste", "awareness", "industrial"]
        elif aqi <= 200:
            sectors = ["transport", "industrial", "waste", "agriculture", "awareness"]
        else:
            sectors = list(COMMUNITY_ACTIONS.keys())

        actions = []
        for sector in sectors[:4]:
            top_action = COMMUNITY_ACTIONS[sector]["actions"][0]
            actions.append({
                "sector": COMMUNITY_ACTIONS[sector]["title"],
                "icon": COMMUNITY_ACTIONS[sector]["icon"],
                "action": top_action,
            })
        return actions

    def _get_all_actions(self) -> list:
        """Return all sector actions formatted for display"""
        result = []
        for key, sector in COMMUNITY_ACTIONS.items():
            result.append({
                "sector_key": key,
                "icon": sector["icon"],
                "title": sector["title"],
                "actions": sector["actions"],
            })
        return result

    def _get_policy_advisory(self, aqi: int) -> dict:
        """Return policy advisory matching AQI level"""
        if aqi <= 50:
            return POLICY_ADVISORIES["good"]
        elif aqi <= 100:
            return POLICY_ADVISORIES["moderate"]
        elif aqi <= 150:
            return POLICY_ADVISORIES["usg"]
        elif aqi <= 200:
            return POLICY_ADVISORIES["unhealthy"]
        elif aqi <= 300:
            return POLICY_ADVISORIES["very_unhealthy"]
        else:
            return POLICY_ADVISORIES["hazardous"]

    def _generate_social_content(self, aqi_data: dict) -> dict:
        """Generate ready-to-post social media content"""
        aqi = aqi_data.get("aqi", 100)
        city = aqi_data.get("city", "your city")
        category = aqi_data.get("aqi_category", "Moderate")

        # Get 3 top actions for the post
        top_actions = self._get_priority_actions(aqi)[:3]
        actions_str = "\n".join([f"• {a['action']}" for a in top_actions])

        return {
            "twitter": SOCIAL_MEDIA_TEMPLATES["twitter"].format(
                city=city, aqi=aqi, category=category,
                action=top_actions[0]["action"] if top_actions else "Take action today!"
            ),
            "whatsapp": SOCIAL_MEDIA_TEMPLATES["whatsapp"].format(
                city=city, aqi=aqi, category=category, actions=actions_str
            ),
            "instagram": SOCIAL_MEDIA_TEMPLATES["instagram"].format(
                city=city, aqi=aqi, category=category, actions=actions_str
            ),
        }

    def _generate_awareness_events(self, aqi: int, city: str) -> list:
        events = [
            {
                "event": "Community AQI Monitoring Walk",
                "description": f"Organize a neighbourhood walk with portable AQI monitors in {city}",
                "frequency": "Monthly",
                "audience": "All residents",
            },
            {
                "event": "School Air Quality Workshop",
                "description": "Educate children on air pollution, its sources and personal protection",
                "frequency": "Quarterly",
                "audience": "Students, Teachers",
            },
            {
                "event": "Tree Plantation Drive",
                "description": f"Plant 100 air-purifying trees in {city} parks and roadways",
                "frequency": "Annual (monsoon)",
                "audience": "Volunteers, Residents",
            },
        ]
        if aqi > 150:
            events.append({
                "event": "Emergency Clean Air Rally",
                "description": f"Organize a citizen petition and awareness rally in {city} demanding immediate action",
                "frequency": "Triggered by AQI > 150",
                "audience": "All citizens",
            })
        return events

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _campaign_theme(self, aqi: int) -> str:
        if aqi <= 50:   return "Breathe Easy — Protect What We Have"
        if aqi <= 100:  return "Good Air Is Not Guaranteed — Act Now"
        if aqi <= 150:  return "Our Air Needs Help — Every Action Counts"
        if aqi <= 200:  return "Red Alert — Fight for Clean Air"
        return "Air Emergency — Demand Action Today"

    def _key_messages(self, aqi: int, city: str) -> list:
        messages = [
            f"Air quality in {city} is at AQI {aqi} — our collective choices determine tomorrow's air",
            "Small individual actions × millions of people = significant change",
            "Clean air is a fundamental right — hold polluters accountable",
        ]
        if aqi > 150:
            messages.append("This is a public health crisis — demand emergency government action")
        return messages

    def _recommended_channels(self, aqi: int) -> list:
        channels = ["WhatsApp Groups", "Instagram", "Local Newspaper"]
        if aqi > 100:
            channels += ["Twitter/X", "Local TV news", "Community FM Radio"]
        if aqi > 150:
            channels += ["Press Conference", "Government Portals", "National Media"]
        return channels

    def _petition_template(self, aqi: int, city: str) -> str:
        return (
            f"We, the citizens of {city}, are deeply concerned about the deteriorating air quality "
            f"(Current AQI: {aqi}). We urge the authorities to: "
            f"(1) Implement immediate source control measures, "
            f"(2) Enforce emission standards strictly, "
            f"(3) Expand real-time AQI monitoring infrastructure, "
            f"(4) Declare air quality emergency and mobilize resources. "
            f"Clean air is our right."
        )

    def _get_ngo_contacts(self, city: str) -> list:
        return [
            {"name": "Centre for Science and Environment (CSE)", "url": "https://www.cseindia.org", "focus": "Policy & Research"},
            {"name": "Clean Air Collective",                     "url": "https://www.cleanair.earth",  "focus": "Citizen Action"},
            {"name": "Lung Care Foundation",                     "url": "https://lungcarefoundation.com", "focus": "Health Advocacy"},
            {"name": "UrbanEmissions.info",                      "url": "https://urbanemissions.info",  "focus": "Data & Modelling"},
        ]

    def _reporting_channels(self, city: str) -> list:
        return [
            {"channel": "CPCB Complaint Portal",   "url": "https://cpcb.nic.in",      "type": "Web"},
            {"channel": "SAMEER App (India)",       "url": "https://sameer.gov.in",    "type": "Mobile App"},
            {"channel": "National Helpline 14420",  "url": "tel:14420",                "type": "Phone"},
            {"channel": "Local PCB",                "url": f"Search '{city} Pollution Control Board'", "type": "Physical/Web"},
        ]

    # ------------------------------------------------------------------
    # Granite-powered content generation
    # ------------------------------------------------------------------

    def _granite_campaign(self, aqi_data: dict) -> str:
        """Generate an AI-powered community campaign message"""
        aqi = aqi_data.get("aqi", 100)
        city = aqi_data.get("city", "the city")
        category = aqi_data.get("aqi_category", "Moderate")
        dominant = aqi_data.get("dominant_pollutant", "PM2.5")

        prompt = (
            f"You are a public health communication specialist. Write a compelling community awareness message.\n\n"
            f"City: {city}\n"
            f"Current AQI: {aqi} ({category})\n"
            f"Main Pollutant: {dominant.upper()}\n\n"
            f"Write a 3-sentence community message that: "
            f"1) States the current air quality situation urgently, "
            f"2) Identifies 2 main community-level causes, "
            f"3) Calls citizens to one specific collective action. "
            f"Tone: urgent but empowering. Under 80 words."
        )
        return granite_client.generate(prompt)

    def _granite_policy_summary(self, aqi_data: dict) -> str:
        """Generate an AI-powered policy summary for policymakers"""
        aqi = aqi_data.get("aqi", 100)
        city = aqi_data.get("city", "the city")
        category = aqi_data.get("aqi_category", "Moderate")

        prompt = (
            f"You are a policy advisor specializing in environmental health. "
            f"Write a brief policy advisory note.\n\n"
            f"City: {city} | AQI: {aqi} ({category})\n\n"
            f"Address the following: "
            f"1) Immediate government response required, "
            f"2) Short-term regulatory actions (within 48 hours), "
            f"3) Long-term structural interventions needed. "
            f"Formal tone. Under 100 words."
        )
        return granite_client.generate(prompt)
