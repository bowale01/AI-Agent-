# Football Head-to-Head AI Agent

## Overview
This AI agent analyzes daily football fixtures using API-Football, focusing strictly on head-to-head history and recent team form. It provides data-driven predictions and recommends only the safest bets (with >70% historical success) for each match.

## Features
- Fetches today's football fixtures automatically
- Retrieves all historical head-to-head matches for each fixture
- Analyzes recent form (last 5 matches) for both teams
- Calculates win, draw, and goal rates from head-to-head data
- Recommends the safest bet (draw, win, 1X, 2X, over 1.5/2.5 goals) only if >70% historical success
- Ignores fixtures with no head-to-head history
- Prints and saves predictions, safest bets, and recent form for each match

## Safest Bet Logic
- Only outcomes with >70% historical success in head-to-head are recommended
- Possible bets: Draw, Home Win, Away Win, 1X (home win or draw), 2X (away win or draw), Over 1.5 goals, Over 2.5 goals
- If no outcome meets the threshold, the agent reports "No safest bet (>70% h2h)"

## Usage
1. Add your API-Football key to `.env` as `API_FOOTBALL_KEY=your_key_here`
2. Run the script: `python head_to_head_analyzer.py`
3. View results in the console and in `h2h_results.txt`

## Output Example
```
Arsenal vs Leeds: Predicted winner - Arsenal; Draws: 1; 1X: True; 2X: False; Likely over 1.5 goals: True; Likely over 2.5 goals: True (based on 5 head-to-head matches); Best bet: Over 2.5 goals (>70% h2h)
Recent form Arsenal: {'wins': 4, 'draws': 1, 'losses': 0, 'goals_for': 10, 'goals_against': 3}
Recent form Leeds: {'wins': 1, 'draws': 2, 'losses': 2, 'goals_for': 5, 'goals_against': 7}
```

## Requirements
- Python 3.7+
- requests
- python-dotenv

## Notes
- The agent only predicts matches with head-to-head history
- API request limits may apply
# AI-Agents
A collection of AI-powered automation scripts and agents. This repository includes tools for sports data analysis, betting insights, and other AI-driven solutions. Each agent is designed to solve specific problems, and new agents will be added over time.
