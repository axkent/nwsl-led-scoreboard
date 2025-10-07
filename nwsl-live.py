import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import argparse
import pytz

# ---------- CONFIG ----------
season_year = 2025
lookback_days = 14
lookahead_days = 14

# Team colors/logos
team_lookup = pd.DataFrame({
    "team": ["SD", "POR", "SEA", "LA", "CHI", "KC", "NC", "HOU",
             "ORL", "WAS", "UTA", "BAY", "GFC", "LOU"],
    "bg_color": ["#002F65","#004B25","#002244","#552583","#DA291C","#004B87",
                 "#002F56","#FF6F00","#61259E","#C8102E","#002F65","#1E1E1E",
                 "#00A19C","#C8B3F6"],
    "text_color": ["#FFFFFF"]*14,
    "logo_url": [
        "https://a.espncdn.com/i/teamlogos/soccer/500/11256.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/210.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/233.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/11897.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/187.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/8726.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/10183.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/6074.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/5730.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/8823.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/11307.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/11767.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/11766.png",
        "https://a.espncdn.com/i/teamlogos/soccer/500/20905.png"
    ]
})

# Parse timezone argument
parser = argparse.ArgumentParser()
parser.add_argument('--tz', type=str, default='America/Los_Angeles', 
                    help='Timezone for display (e.g., America/New_York, America/Chicago, America/Denver)')
args = parser.parse_args()

# Get the target timezone
target_tz = pytz.timezone(args.tz)
print(f"Using timezone: {args.tz}")

# ---------- HELPER ----------
def safe_int(x):
    try:
        return int(x)
    except:
        return None

def get_games_for_date(d):
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/usa.nwsl/scoreboard?dates={d.strftime('%Y%m%d')}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return pd.DataFrame()
    data = resp.json()
    events = data.get("events", [])
    if not events:
        return pd.DataFrame()
    
    rows = []
    for game in events:
        comp = game["competitions"][0]
        competitors = comp["competitors"]
        home = next((c for c in competitors if c["homeAway"]=="home"), {})
        away = next((c for c in competitors if c["homeAway"]=="away"), {})
        
        rows.append({
            "event_id": comp.get("id"),
            "date": pd.to_datetime(game.get("date")),
            "away_team": away.get("team", {}).get("abbreviation"),
            "home_team": home.get("team", {}).get("abbreviation"),
            "away_score": safe_int(away.get("score")),
            "home_score": safe_int(home.get("score")),
            "state": game.get("status", {}).get("type", {}).get("state"),
            "description": game.get("status", {}).get("type", {}).get("description"),
            "displayClock": game.get("status", {}).get("displayClock")
        })
    return pd.DataFrame(rows)

# ---------- PULL GAMES ----------
dates = [datetime.now().date() - timedelta(days=lookback_days) + timedelta(days=i)
         for i in range(lookback_days + lookahead_days + 1)]
df_list = [get_games_for_date(d) for d in dates]
df = pd.concat(df_list, ignore_index=True)

if df.empty:
    print("⚠️  No games found in date range")
    exit(0)

# ---------- LOGIC: Show live game, recent completed, or next scheduled ----------
now = datetime.now(target_tz)
now_utc = now.astimezone(pytz.UTC)
cutoff_time = now_utc - timedelta(hours=24)

# Track which teams have been processed
games_to_show = []
teams_with_games = set()  # Track teams that already have a game selected

for team in team_lookup['team']:
    # Skip if this team already has a game (from a live game that includes both teams)
    if team in teams_with_games:
        print(f"  → Skipping {team} - already showing game for this team")
        continue
    
    # Get all games for this team
    team_games = df[(df['home_team'] == team) | (df['away_team'] == team)].copy()
    
    if team_games.empty:
        continue
    
    # Sort by date
    team_games = team_games.sort_values('date')
    
    # PRIORITY 1: Check for live games first (highest priority)
    live_games = team_games[team_games['state'] == 'in']
    
    if not live_games.empty:
        # Show live game - this is the ONLY game we want for this team
        game_to_show = live_games.iloc[0]
        print(f"  → Selected LIVE game for {team}")
        
        # Add BOTH teams from this game to the processed set
        teams_with_games.add(game_to_show['home_team'])
        teams_with_games.add(game_to_show['away_team'])
        
    else:
        # PRIORITY 2: Check for recent completed games (within 24 hours)
        recent_completed = team_games[
            (team_games['state'] == 'post') & 
            (team_games['date'] >= cutoff_time)
        ]
        
        if not recent_completed.empty:
            # Show the most recent completed game
            game_to_show = recent_completed.iloc[-1]
            print(f"  → Selected RECENT game for {team}")
            teams_with_games.add(team)
        else:
            # PRIORITY 3: Show next upcoming game
            today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
            upcoming = team_games[
                (team_games['state'] == 'pre') &
                (team_games['date'] >= today_start)
            ]
            
            if not upcoming.empty:
                game_to_show = upcoming.iloc[0]
                print(f"  → Selected UPCOMING game for {team}")
                teams_with_games.add(team)
            else:
                # PRIORITY 4: No upcoming games, show most recent completed
                completed = team_games[team_games['state'] == 'post']
                if not completed.empty:
                    game_to_show = completed.iloc[-1]
                    print(f"  → Selected OLD completed game for {team}")
                    teams_with_games.add(team)
                else:
                    print(f"  → SKIPPING {team} - no valid games")
                    continue
    
    # Add to list if not already there (avoid duplicates from same event)
    if game_to_show['event_id'] not in [g['event_id'] for g in games_to_show]:
        games_to_show.append(game_to_show.to_dict())
        print(f"  ✓ Added event {game_to_show['event_id']} to list")
    else:
        print(f"  ✗ Skipped event {game_to_show['event_id']} - already in list")

# Convert to DataFrame and remove duplicate events
df_display = pd.DataFrame(games_to_show)
df_display = df_display.drop_duplicates(subset=['event_id'], keep='first')

# Convert times from UTC to specified timezone, then remove timezone info
df_display['date'] = pd.to_datetime(df_display['date']).dt.tz_convert(target_tz).dt.tz_localize(None)

# ---------- LONG FORMAT (both teams per game) ----------
df_long = df_display.melt(
    id_vars=["event_id","date","away_score","home_score","state","description","displayClock"],
    value_vars=["away_team","home_team"],
    var_name="location",
    value_name="team"
)

# Map location properly
df_long['location'] = df_long['location'].map({'away_team': 'away_team', 'home_team': 'home_team'})

# ---------- MERGE COLORS/LOGOS ----------
team_games = df_long.merge(team_lookup, on="team", how="left")

# ---------- SAVE JSON ----------
team_games.to_json("/tmp/nwsl_schedule.json", orient="records", date_format="iso", indent=2)
os.chmod("/tmp/nwsl_schedule.json", 0o666)
print(f"✅ JSON saved with {len(games_to_show)} games to display!")
print(f"   Games within 24hrs or next scheduled games shown")
print(f"   Times displayed in: {args.tz}")
