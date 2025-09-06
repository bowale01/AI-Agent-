def fetch_team_form(team_id):
    # Fetch last 5 matches for the team
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"API-Football error (form): {response.status_code}")
        return None
    matches = response.json().get("response", [])
    wins, draws, losses, goals_for, goals_against = 0, 0, 0, 0, 0
    for match in matches:
        team_side = "home" if match["teams"]["home"]["id"] == team_id else "away"
        goals_team = match["goals"][team_side]
        goals_opp = match["goals"]["away" if team_side == "home" else "home"]
        goals_for += goals_team if goals_team is not None else 0
        goals_against += goals_opp if goals_opp is not None else 0
        if goals_team > goals_opp:
            wins += 1
        elif goals_team == goals_opp:
            draws += 1
        else:
            losses += 1
    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against
    }
  

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
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")

from datetime import datetime

def fetch_today_fixtures():
    today = datetime.now().strftime('%Y-%m-%d')
    fixtures = []
    if API_FOOTBALL_KEY:
        url = f"https://v3.football.api-sports.io/fixtures?date={today}"
        headers = {"x-apisports-key": API_FOOTBALL_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            fixtures = response.json().get("response", [])
        else:
            print(f"API-Football error (fixtures): {response.status_code}")
    elif FOOTBALL_DATA_KEY:
        url = f"https://api.football-data.org/v4/matches?dateFrom={today}&dateTo={today}"
        headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Football-Data.org returns matches in 'matches' key
            fixtures = response.json().get("matches", [])
        else:
            print(f"Football-Data.org error (fixtures): {response.status_code}")
    else:
        print("No API key provided for either API-Football or Football-Data.org.")
    return fixtures

# Get team IDs and names from fixture
def get_teams_from_fixture(fixture):
    if API_FOOTBALL_KEY:
        home = fixture["teams"]["home"]
        away = fixture["teams"]["away"]
        return home["id"], away["id"], home["name"], away["name"]
    elif FOOTBALL_DATA_KEY:
        home = fixture["homeTeam"]
        away = fixture["awayTeam"]
        # Football-Data.org does not provide team IDs in the same way, so use names only
        return None, None, home["name"], away["name"]

def fetch_h2h(team1_id, team2_id, team1_name, team2_name):
    if API_FOOTBALL_KEY and team1_id and team2_id:
        url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={team1_id}-{team2_id}"
        headers = {"x-apisports-key": API_FOOTBALL_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API-Football error: {response.status_code}")
            return None
    elif FOOTBALL_DATA_KEY:
        # Football-Data.org does not provide direct h2h endpoint, so filter matches manually
        url = f"https://api.football-data.org/v4/teams/{team1_name}/matches?dateFrom=1900-01-01&dateTo={datetime.now().strftime('%Y-%m-%d')}"
        headers = {"X-Auth-Token": FOOTBALL_DATA_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            # Filter only matches against team2_name
            h2h_matches = [m for m in matches if m.get("awayTeam", {}).get("name") == team2_name or m.get("homeTeam", {}).get("name") == team2_name]
            return {"response": h2h_matches}
        else:
            print(f"Football-Data.org error: {response.status_code}")
            return None
    else:
        print("No API key provided for either API-Football or Football-Data.org.")
        return None

def analyze_h2h_results(h2h_data, team1_name, team2_name):
    # Best bet recommendation logic (>70% historical success, head-to-head only)
    best_bet = None
    if total_matches > 0:
        draw_rate = draws / total_matches
        team1_win_rate = team1_wins / total_matches
        team2_win_rate = team2_wins / total_matches
        over_1_5_rate = over_1_5_count / total_matches
        over_2_5_rate = over_2_5_count / total_matches

        if draw_rate > 0.7:
            best_bet = "Draw (>70% h2h)"
        elif team1_win_rate > 0.7:
            best_bet = f"{team1_name} to win (>70% h2h)"
        elif team2_win_rate > 0.7:
            best_bet = f"{team2_name} to win (>70% h2h)"
        elif over_2_5_rate > 0.7:
            best_bet = "Over 2.5 goals (>70% h2h)"
        elif over_1_5_rate > 0.7:
            best_bet = "Over 1.5 goals (>70% h2h)"
        elif home_1x and (team1_win_rate + draw_rate) > 0.7:
            best_bet = f"{team1_name} win or draw (1X) (>70% h2h)"
        elif away_2x and (team2_win_rate + draw_rate) > 0.7:
            best_bet = f"{team2_name} win or draw (2X) (>70% h2h)"
        else:
            best_bet = "No safest bet (>70% h2h)"
    else:
        best_bet = "No head-to-head data"
    matches = h2h_data.get("response", [])
    if not matches:
        return None  # No head-to-head data

    team1_wins = 0
    team2_wins = 0
    draws = 0
    over_1_5_count = 0
    over_2_5_count = 0
    total_matches = 0

    for match in matches:
        goals_home = match.get("goals", {}).get("home", 0)
        goals_away = match.get("goals", {}).get("away", 0)
        total_goals = goals_home + goals_away
        if total_goals > 1.5:
            over_1_5_count += 1
        if total_goals > 2.5:
            over_2_5_count += 1
        total_matches += 1

        # Determine winner
        home_name = match.get("teams", {}).get("home", {}).get("name", "")
        away_name = match.get("teams", {}).get("away", {}).get("name", "")
        if goals_home > goals_away:
            if home_name == team1_name:
                team1_wins += 1
            elif home_name == team2_name:
                team2_wins += 1
        elif goals_away > goals_home:
            if away_name == team1_name:
                team1_wins += 1
            elif away_name == team2_name:
                team2_wins += 1
        else:
            draws += 1

    # Prediction logic
    if draws > team1_wins and draws > team2_wins:
        predicted_winner = "Draw"
    elif team1_wins > team2_wins:
        predicted_winner = team1_name
    elif team2_wins > team1_wins:
        predicted_winner = team2_name
    else:
        predicted_winner = "Draw"

    likely_over_1_5 = over_1_5_count / total_matches >= 0.5  # Over 50% matches
    likely_over_2_5 = over_2_5_count / total_matches >= 0.5
    home_1x = team1_wins + draws > team2_wins  # Home win or draw
    away_2x = team2_wins + draws > team1_wins  # Away win or draw

    result = {
        "team1": team1_name,
        "team2": team2_name,
        "predicted_winner": predicted_winner,
        "likely_over_1_5": likely_over_1_5,
        "likely_over_2_5": likely_over_2_5,
        "home_1x": home_1x,
        "away_2x": away_2x,
        "total_matches": total_matches,
        "draws": draws,
        "best_bet": best_bet
    }
    return result

def automate_daily_h2h_analysis():
    fixtures = fetch_today_fixtures()
    results = []
    for fixture in fixtures:
        team1_id, team2_id, team1_name, team2_name = get_teams_from_fixture(fixture)
        print(f"Analyzing {team1_name} vs {team2_name}...")
        h2h_data = fetch_h2h(team1_id, team2_id, team1_name, team2_name)
        form1 = fetch_team_form(team1_id) if team1_id else None
        form2 = fetch_team_form(team2_id) if team2_id else None
        if h2h_data:
            analysis = analyze_h2h_results(h2h_data, team1_name, team2_name)
            if analysis:
                analysis["form_team1"] = form1
                analysis["form_team2"] = form2
                print(f"{team1_name} vs {team2_name}: Predicted winner - {analysis['predicted_winner']}; Draws: {analysis['draws']}; 1X (home win or draw): {analysis['home_1x']}; 2X (away win or draw): {analysis['away_2x']}; Likely over 1.5 goals: {analysis['likely_over_1_5']}; Likely over 2.5 goals: {analysis['likely_over_2_5']} (based on {analysis['total_matches']} head-to-head matches)")
                print(f"Best bet: {analysis['best_bet']}")
                print(f"Recent form {team1_name}: {form1}")
                print(f"Recent form {team2_name}: {form2}")
                results.append(analysis)
        time.sleep(1)  # Avoid hitting API rate limits
    return results

def save_results(results, filename="h2h_results.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"{r['team1']} vs {r['team2']}: Predicted winner - {r['predicted_winner']}; Draws: {r['draws']}; 1X (home win or draw): {r['home_1x']}; 2X (away win or draw): {r['away_2x']}; Likely over 1.5 goals: {r['likely_over_1_5']}; Likely over 2.5 goals: {r['likely_over_2_5']} (based on {r['total_matches']} head-to-head matches); Best bet: {r['best_bet']}\n")
            f.write(f"Recent form {r['team1']}: {r.get('form_team1')}\n")
            f.write(f"Recent form {r['team2']}: {r.get('form_team2')}\n")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    print("Fetching today's fixtures and analyzing head-to-head...")
    results = automate_daily_h2h_analysis()
    save_results(results)
