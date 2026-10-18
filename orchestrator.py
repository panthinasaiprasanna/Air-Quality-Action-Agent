"""
Multi-Agent Orchestrator
Coordinates all four specialized agents (AQI Data, Health Advisory,
Forecasting, Community Action) into a unified pipeline.
Acts as the central controller for the Daily Air Quality Action Agent system.
"""
import json
import sys
import os
from datetime import datetime

# Allow running from root or agents/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.aqi_data_agent import AQIDataAgent
from agents.health_advisory_agent import HealthAdvisoryAgent
from agents.forecasting_agent import ForecastingAgent
from agents.community_action_agent import CommunityActionAgent
from granite_client import granite_client


class AirQualityOrchestrator:
    """
    Central orchestrator that coordinates the multi-agent pipeline.

    Pipeline flow:
      1. AQIDataAgent      → fetch & interpret current air quality
      2. ForecastingAgent  → predict 7-day trends & issue alerts
      3. HealthAdvisoryAgent → personalized health recommendations
      4. CommunityActionAgent → community & policy insights
      5. Granite LLM       → synthesize executive summary
    """

    def __init__(self):
        print("🔧 Initializing Air Quality Multi-Agent System...")
        self.aqi_agent = AQIDataAgent()
        self.health_agent = HealthAdvisoryAgent()
        self.forecast_agent = ForecastingAgent()
        self.community_agent = CommunityActionAgent()
        print("✓ All agents initialized")

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run_full_analysis(self, city: str, user_profile: dict = None) -> dict:
        """
        Execute the complete multi-agent analysis pipeline.
        Returns a unified report from all four agents.
        """
        if user_profile is None:
            user_profile = {
                "age": 35,
                "conditions": [],
                "activity_level": "moderate",
                "has_children": False,
                "pregnant": False,
            }

        print(f"\n{'='*60}")
        print(f"  🌍 Air Quality Action Agent — {city.title()}")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # ----- Step 1: Fetch AQI Data -----
        print("\n[1/5] 📡 AQI Data Agent: Fetching air quality data...")
        aqi_data = self.aqi_agent.fetch_aqi(city, user_profile)
        historical = self.aqi_agent.get_historical_aqi(city, days=7)
        hourly_today = self.aqi_agent.get_hourly_aqi(city)
        print(f"      ✓ AQI: {aqi_data['aqi']} ({aqi_data['aqi_category']}) — Source: {aqi_data['source']}")

        # ----- Step 2: Forecast -----
        print("\n[2/5] 🔮 Forecasting Agent: Generating 7-day forecast...")
        forecast_data = self.forecast_agent.generate_forecast(aqi_data, historical)
        hotspots = self.forecast_agent.get_pollution_hotspots(city)
        seasonal = self.forecast_agent.get_seasonal_outlook()
        print(f"      ✓ Trend: {forecast_data['trend']['direction']} | Peak: {forecast_data['trend']['peak_aqi']}")

        # ----- Step 3: Health Advisory -----
        print("\n[3/5] 🏥 Health Advisory Agent: Generating personalized recommendations...")
        health_data = self.health_agent.generate_advisory(aqi_data, user_profile)
        activity_schedule = self.health_agent.get_activity_schedule(aqi_data, user_profile)
        diet_tips = self.health_agent.get_diet_recommendations(aqi_data.get("aqi", 100))
        print(f"      ✓ Risk level: {health_data['risk_level']} | Group: {health_data['sensitive_group']}")

        # ----- Step 4: Community Action -----
        print("\n[4/5] 🤝 Community Action Agent: Generating policy & awareness content...")
        community_data = self.community_agent.generate_community_report(aqi_data)
        campaign_kit = self.community_agent.get_campaign_kit(aqi_data)
        print(f"      ✓ Alert level: {community_data['alert_level']}")

        # ----- Step 5: Granite Executive Summary -----
        print("\n[5/5] 🤖 IBM Granite: Synthesizing executive summary...")
        executive_summary = self._synthesize_summary(
            aqi_data, forecast_data, health_data, community_data, user_profile
        )
        print("      ✓ Executive summary generated")

        print(f"\n{'='*60}")
        print("  ✅ Analysis complete!")
        print(f"{'='*60}\n")

        return {
            "metadata": {
                "city": city.title(),
                "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agents_used": ["AQI Data", "Forecasting", "Health Advisory", "Community Action"],
                "llm": "IBM Granite 4 H Small (ibm/granite-4-h-small)",
                "granite_available": granite_client.is_available(),
            },
            "aqi_data": aqi_data,
            "historical_aqi": historical,
            "hourly_today": hourly_today,
            "forecast": forecast_data,
            "hotspots": hotspots,
            "seasonal_outlook": seasonal,
            "health_advisory": health_data,
            "activity_schedule": activity_schedule,
            "diet_recommendations": diet_tips,
            "community_action": community_data,
            "campaign_kit": campaign_kit,
            "executive_summary": executive_summary,
        }

    def run_quick_check(self, city: str) -> dict:
        """Quick AQI check without full personalized analysis"""
        aqi_data = self.aqi_agent.fetch_aqi(city)
        alerts = self.forecast_agent.generate_forecast(aqi_data)["risk_alerts"]
        top_actions = self.community_agent.get_campaign_kit(aqi_data)["key_messages"]
        return {
            "city": city.title(),
            "aqi": aqi_data["aqi"],
            "category": aqi_data["aqi_category"],
            "icon": aqi_data["aqi_icon"],
            "color": aqi_data["aqi_color"],
            "active_alerts": len(alerts),
            "key_messages": top_actions,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # ------------------------------------------------------------------
    # Synthesis
    # ------------------------------------------------------------------

    def _synthesize_summary(
        self,
        aqi_data: dict,
        forecast: dict,
        health: dict,
        community: dict,
        profile: dict,
    ) -> str:
        """Use IBM Granite to generate a unified executive summary"""
        prompt = (
            f"You are the Daily Air Quality Action Agent for {aqi_data.get('city', 'the city')}. "
            f"Synthesize the following data into a clear, actionable daily briefing.\n\n"
            f"CURRENT STATUS:\n"
            f"- AQI: {aqi_data.get('aqi')} ({aqi_data.get('aqi_category')})\n"
            f"- Main pollutant: {aqi_data.get('dominant_pollutant', 'PM2.5').upper()}\n\n"
            f"FORECAST:\n"
            f"- Trend: {forecast.get('trend', {}).get('direction', 'stable')}\n"
            f"- Worst day this week: {forecast.get('worst_day', {}).get('day_name', 'N/A')}"
            f" (AQI {forecast.get('worst_day', {}).get('aqi', 'N/A')})\n"
            f"- Active alerts: {len(forecast.get('risk_alerts', []))}\n\n"
            f"HEALTH:\n"
            f"- Personal risk level: {health.get('risk_level', 'Moderate')}\n"
            f"- Sensitive group: {health.get('sensitive_group', 'General population')}\n"
            f"- Top recommendation: {health.get('immediate_actions', ['Stay safe'])[0]}\n\n"
            f"COMMUNITY:\n"
            f"- Alert status: {community.get('alert_level', 'Yellow')}\n"
            f"- Top community action: {community.get('priority_actions', [{}])[0].get('action', 'N/A')}\n\n"
            f"Write a 4-sentence executive briefing covering: today's situation, health priority, "
            f"outlook for the week, and one collective action. Keep under 120 words."
        )
        return granite_client.generate(prompt)

    # ------------------------------------------------------------------
    # Display utilities
    # ------------------------------------------------------------------

    def print_summary(self, report: dict) -> None:
        """Print a formatted console summary of the report"""
        aqi_data = report["aqi_data"]
        health = report["health_advisory"]
        forecast = report["forecast"]
        community = report["community_action"]

        print(f"\n{'─'*60}")
        print(f"  📍 City:          {report['metadata']['city']}")
        print(f"  📊 AQI:           {aqi_data['aqi']} {aqi_data['aqi_icon']}  ({aqi_data['aqi_category']})")
        print(f"  🔬 Dominant:      {aqi_data.get('dominant_pollutant', 'PM2.5').upper()}")
        print(f"  📡 Source:        {aqi_data.get('source', 'API')}")
        print(f"{'─'*60}")
        print(f"  ⚠️  Risk Level:    {health['risk_level']} ({health['sensitive_group']})")
        print(f"  😷 Mask:          {health['mask_recommendation']}")
        print(f"  🏋️  Exercise:      {health['exercise_recommendation']}")
        print(f"{'─'*60}")
        print(f"  📈 7-Day Trend:   {forecast['trend']['direction']} {forecast['trend']['icon']}")
        print(f"  ⚠️  Active Alerts: {len(forecast['risk_alerts'])}")
        print(f"  🔴 Worst Day:     {forecast['worst_day']['day_name']} (AQI {forecast['worst_day']['aqi']})")
        print(f"  🟢 Best Day:      {forecast['best_day']['day_name']} (AQI {forecast['best_day']['aqi']})")
        print(f"{'─'*60}")
        print(f"  🚦 Policy Status: {community['alert_level']}")
        print(f"{'─'*60}")
        print(f"\n  📝 Executive Summary:\n")
        print(f"  {report['executive_summary']}")
        print(f"\n  🏥 Top Health Actions:")
        for action in health["immediate_actions"][:3]:
            print(f"    {action}")
        print(f"\n  🤝 Top Community Actions:")
        for item in community["priority_actions"][:2]:
            print(f"    {item['icon']} {item['action']}")
        print(f"{'─'*60}\n")
