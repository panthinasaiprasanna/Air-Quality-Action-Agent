"""
Flask API Server
Exposes the multi-agent system as a REST API consumed by the dashboard.
"""
import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from orchestrator import AirQualityOrchestrator

load_dotenv()

app = Flask(__name__)
CORS(app)

# Singleton orchestrator (avoid re-init on every request)
orchestrator = AirQualityOrchestrator()

# ------------------------------------------------------------------
# API Routes
# ------------------------------------------------------------------

@app.route("/")
def serve_dashboard():
    """Serve the interactive dashboard"""
    return send_from_directory(".", "dashboard.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """System health check"""
    from granite_client import granite_client
    return jsonify({
        "status": "operational",
        "agents": ["AQI Data", "Health Advisory", "Forecasting", "Community Action"],
        "granite_available": granite_client.is_available(),
        "version": "1.0.0",
    })


@app.route("/api/aqi/<city>", methods=["GET"])
def get_aqi(city: str):
    """Fetch current AQI for a city"""
    profile = _extract_profile(request)
    try:
        aqi_data = orchestrator.aqi_agent.fetch_aqi(city, profile)
        return jsonify({"success": True, "data": aqi_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/full-report/<city>", methods=["POST"])
def full_report(city: str):
    """Run full multi-agent analysis pipeline for a city"""
    body = request.get_json(silent=True) or {}
    profile = body.get("profile", {
        "age": 35,
        "conditions": [],
        "activity_level": "moderate",
        "has_children": False,
        "pregnant": False,
    })
    try:
        report = orchestrator.run_full_analysis(city, profile)
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/forecast/<city>", methods=["GET"])
def get_forecast(city: str):
    """Get 7-day AQI forecast for a city"""
    try:
        aqi_data = orchestrator.aqi_agent.fetch_aqi(city)
        historical = orchestrator.aqi_agent.get_historical_aqi(city, days=7)
        forecast = orchestrator.forecast_agent.generate_forecast(aqi_data, historical)
        seasonal = orchestrator.forecast_agent.get_seasonal_outlook()
        hotspots = orchestrator.forecast_agent.get_pollution_hotspots(city)
        return jsonify({
            "success": True,
            "forecast": forecast,
            "seasonal": seasonal,
            "hotspots": hotspots,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health-advisory/<city>", methods=["POST"])
def get_health_advisory(city: str):
    """Get personalized health advisory"""
    body = request.get_json(silent=True) or {}
    profile = body.get("profile", {"age": 35, "conditions": [], "activity_level": "moderate"})
    try:
        aqi_data = orchestrator.aqi_agent.fetch_aqi(city, profile)
        advisory = orchestrator.health_agent.generate_advisory(aqi_data, profile)
        schedule = orchestrator.health_agent.get_activity_schedule(aqi_data, profile)
        diet = orchestrator.health_agent.get_diet_recommendations(aqi_data.get("aqi", 100))
        return jsonify({
            "success": True,
            "advisory": advisory,
            "activity_schedule": schedule,
            "diet_tips": diet,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/community/<city>", methods=["GET"])
def get_community_report(city: str):
    """Get community action and policy report"""
    try:
        aqi_data = orchestrator.aqi_agent.fetch_aqi(city)
        community = orchestrator.community_agent.generate_community_report(aqi_data)
        campaign = orchestrator.community_agent.get_campaign_kit(aqi_data)
        return jsonify({
            "success": True,
            "community": community,
            "campaign_kit": campaign,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/historical/<city>", methods=["GET"])
def get_historical(city: str):
    """Get historical AQI data"""
    days = int(request.args.get("days", 7))
    try:
        historical = orchestrator.aqi_agent.get_historical_aqi(city, days=days)
        hourly = orchestrator.aqi_agent.get_hourly_aqi(city)
        return jsonify({
            "success": True,
            "historical": historical,
            "hourly_today": hourly,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/quick-check/<city>", methods=["GET"])
def quick_check(city: str):
    """Quick AQI check for a city"""
    try:
        result = orchestrator.run_quick_check(city)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/aqi-categories", methods=["GET"])
def aqi_categories():
    """Return AQI category reference"""
    categories = orchestrator.aqi_agent.get_aqi_categories()
    return jsonify({"success": True, "categories": categories})


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _extract_profile(request) -> dict:
    """Extract user profile from query params"""
    return {
        "age": int(request.args.get("age", 35)),
        "conditions": request.args.getlist("conditions"),
        "activity_level": request.args.get("activity_level", "moderate"),
        "has_children": request.args.get("has_children", "false").lower() == "true",
        "pregnant": request.args.get("pregnant", "false").lower() == "true",
    }


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"\n🚀 Air Quality Action Agent API starting on port {port}")
    print(f"   Dashboard: http://localhost:{port}")
    print(f"   API Docs:  http://localhost:{port}/api/health\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
