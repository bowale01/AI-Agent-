  

"""
AI Agent: Automated Head-to-Head Match Analyzer

This script connects to football data APIs (API-Football, Football-Data.org) to fetch historical match data.
It analyzes head-to-head records to find matchups where one team has never lost to the other.
Now automated for multiple team pairs and outputs results to a file.

Instructions:
- Insert your API keys for API-Football and Football-Data.org below.
- Add team pairs to the TEAM_PAIRS list (IDs and names).
- Run the script to fetch and analyze data automatically.
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

from datetime import datetime

def fetch_today_fixtures():
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={today}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print(f"API-Football error (fixtures): {response.status_code}")
        return []

def get_teams_from_fixture(fixture):
    home = fixture["teams"]["home"]
    away = fixture["teams"]["away"]
    return home["id"], away["id"], home["name"], away["name"]

def fetch_h2h(team1_id, team2_id, team1_name, team2_name):
    url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={team1_id}-{team2_id}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API-Football error: {response.status_code}")
        return None

def analyze_h2h_results(h2h_data, team1_name, team2_name):
    all_over_1_5 = True
    for match in h2h_data.get("response", []):
        goals_home = match.get("goals", {}).get("home")
        goals_away = match.get("goals", {}).get("away")
        goals_home = goals_home if goals_home is not None else 0
        goals_away = goals_away if goals_away is not None else 0
        total_goals = goals_home + goals_away
        if total_goals <= 1.5:
            all_over_1_5 = False
            break
    result = {
        "team1": team1_name,
        "team2": team2_name,
        "all_over_1_5": all_over_1_5
    }
    return result

def automate_daily_h2h_analysis():
    fixtures = fetch_today_fixtures()
    results = []
    for fixture in fixtures:
        team1_id, team2_id, team1_name, team2_name = get_teams_from_fixture(fixture)
        print(f"Analyzing {team1_name} vs {team2_name}...")
        h2h_data = fetch_h2h(team1_id, team2_id, team1_name, team2_name)
        if h2h_data:
            analysis = analyze_h2h_results(h2h_data, team1_name, team2_name)
            if analysis["all_over_1_5"]:
                print(f"{team1_name} vs {team2_name}: All head-to-head matches are over 1.5 goals!")
                results.append(analysis)
        time.sleep(1)  # Avoid hitting API rate limits
    return results

def save_results(results, filename="h2h_results.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"{r['team1']} vs {r['team2']}: All head-to-head matches are over 1.5 goals!\n")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    print("Fetching today's fixtures and analyzing head-to-head...")
    results = automate_daily_h2h_analysis()
    save_results(results)
