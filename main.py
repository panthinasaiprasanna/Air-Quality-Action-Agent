"""
Main entry point for the Daily Air Quality Action Agent.
Demonstrates the full multi-agent pipeline via command line.
"""
import sys
from orchestrator import AirQualityOrchestrator


def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "Delhi"

    # Sample user profile
    profile = {
        "age":            32,
        "conditions":     [],          # e.g. ["asthma"]
        "activity_level": "moderate",  # sedentary / moderate / active / athlete
        "has_children":   True,
        "pregnant":       False,
    }

    orchestrator = AirQualityOrchestrator()
    report = orchestrator.run_full_analysis(city, profile)
    orchestrator.print_summary(report)

    print("\n📊 Open dashboard.html in your browser for the interactive visualization.")
    print("   Or run: python app.py  (then visit http://localhost:5000)\n")


if __name__ == "__main__":
    main()
