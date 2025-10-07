#!/usr/bin/env python3
"""
NWSL LED Scoreboard Display
Displays game information on RGB LED matrix
"""
import json
import time
import os
import sys
import argparse
import pandas as pd
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

class NWSLScoreboard:
    def __init__(self, favorite_team=None):
        print("Starting initialization...")
        self.favorite_team = favorite_team
        self.previous_scores = {}
        
        # Team color schemes - home colors for backgrounds, away colors for text
        self.team_colors = {
            "SD": {"home": "#041E42", "away": "#E31C79"},
            "BAY": {"home": "#051C2C", "away": "#F9423A"},
            "SEA": {"home": "#2E407A", "away": "#D0A66B"},
            "KC": {"home": "#64CCC9", "away": "#CB333B"},
            "UTA": {"home": "#001E62", "away": "#FFB81C"},
            "LOU": {"home": "#C5B4E3", "away": "#1E1A34"},
            "ORL": {"home": "#5F249F", "away": "#00A9E0"},
            "WAS": {"home": "#000000", "away": "#FEF84C"},
            "POR": {"home": "#971E1F", "away": "#020202"},
            "GFC": {"home": "#000101", "away": "#A7F0F6"},
            "LA": {"home": "#E17263", "away": "#1C1C1C"},
            "CHI": {"home": "#244E69", "away": "#C8102E"},
            "NC": {"home": "#01426A", "away": "#B3A369"},
            "HOU": {"home": "#101820", "away": "#FF6900"}
        }
        
        if favorite_team:
            print(f"Filtering for favorite team: {favorite_team}")
        
        # Load schedule data
        json_path = '/tmp/nwsl_schedule.json'
        if not os.path.exists(json_path):
            print(f"Error: {json_path} not found!")
            print("Run 'sudo python3 main.py' first to fetch game data")
            sys.exit(1)
            
        with open(json_path, 'r') as f:
            self.schedule_data = json.load(f)
        print(f"Loaded {len(self.schedule_data)} games")
        
        # Find font directory - check multiple possible locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_font_dirs = [
            os.path.join(script_dir, "fonts"),
            "/home/pi/rpi-rgb-led-matrix/fonts",
            os.path.expanduser("~/rpi-rgb-led-matrix/fonts"),
        ]
        
        font_dir = None
        for dir_path in possible_font_dirs:
            if os.path.exists(dir_path):
                font_dir = dir_path
                break
        
        if not font_dir:
            print("Error: Could not find fonts directory!")
            print("Checked locations:")
            for dir_path in possible_font_dirs:
                print(f"  - {dir_path}")
            sys.exit(1)
        
        print(f"Using fonts from: {font_dir}")
        
        # Load fonts
        self.font = graphics.Font()
        self.font.LoadFont(f"{font_dir}/5x7.bdf")
        
        self.small_font = graphics.Font()
        self.small_font.LoadFont(f"{font_dir}/4x6.bdf")
        
        # Configure LED matrix
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.brightness = 75
        
        self.matrix = RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()
        print("Initialization complete!")
    
    def hex_to_color(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def group_games_by_event(self):
        """Group games by event_id and filter by favorite team if specified"""
        events = {}
        for game in self.schedule_data:
            event_id = game['event_id']
            if event_id not in events:
                events[event_id] = []
            events[event_id].append(game)
        
        if self.favorite_team:
            filtered_events = {}
            for event_id, games in events.items():
                if any(game['team'] == self.favorite_team for game in games):
                    filtered_events[event_id] = games
            return list(filtered_events.values())
        
        return list(events.values())
    
    def check_for_goals(self, matchup):
        """Check if a goal was scored since last update"""
        home_team = next((t for t in matchup if t['location'] == 'home_team'), None)
        away_team = next((t for t in matchup if t['location'] == 'away_team'), None)
        
        if not home_team or not away_team:
            return None
        
        event_id = home_team['event_id']
        current_home_score = home_team['home_score']
        current_away_score = away_team['away_score']
        
        if event_id in self.previous_scores:
            prev_home, prev_away = self.previous_scores[event_id]
            
            if current_home_score > prev_home:
                self.previous_scores[event_id] = (current_home_score, current_away_score)
                return home_team['team']
            
            if current_away_score > prev_away:
                self.previous_scores[event_id] = (current_home_score, current_away_score)
                return away_team['team']
        else:
            self.previous_scores[event_id] = (current_home_score, current_away_score)
        
        return None

    def draw_goal_animation(self, team_abbr):
        """Display goal celebration animation"""
        self.canvas.Clear()
        white = graphics.Color(255, 255, 255)
        
        # Flash green background
        for x in range(64):
            for y in range(32):
                self.canvas.SetPixel(x, y, 0, 255, 0)
        
        graphics.DrawText(self.canvas, self.font, 10, 12, white, "GOAL!")
        graphics.DrawText(self.canvas, self.font, 12, 24, white, team_abbr)
        
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        time.sleep(2)
    
    def draw_matchup(self, matchup):
        """Draw game information on LED matrix"""
        if len(matchup) < 2:
            return
        
        home_team = next((t for t in matchup if t['location'] == 'home_team'), None)
        away_team = next((t for t in matchup if t['location'] == 'away_team'), None)
        
        if not home_team or not away_team:
            home_team = matchup[0]
            away_team = matchup[1]
        
        self.canvas.Clear()
        
        white = graphics.Color(255, 255, 255)
        yellow = graphics.Color(255, 255, 0)
        red = graphics.Color(255, 0, 0)

        is_final = home_team['state'] == 'post'
        is_live = home_team['state'] == 'in'
        
        # Get team abbreviations
        away_team_abbr = away_team['team']
        home_team_abbr = home_team['team']
        
        # Away team section (top half)
        away_bg_color = self.team_colors.get(away_team_abbr, {}).get('home', '#1E1E1E')
        away_text_color = self.team_colors.get(away_team_abbr, {}).get('away', '#FFFFFF')
        
        away_bg_r, away_bg_g, away_bg_b = self.hex_to_color(away_bg_color)
        away_text_r, away_text_g, away_text_b = self.hex_to_color(away_text_color)
        away_text = graphics.Color(away_text_r, away_text_g, away_text_b)
        
        for x in range(64):
            for y in range(16):
                self.canvas.SetPixel(x, y, away_bg_r, away_bg_g, away_bg_b)
        
        graphics.DrawText(self.canvas, self.font, 2, 7, away_text, away_team_abbr)
        if is_final or is_live:
            graphics.DrawText(self.canvas, self.font, 28, 7, away_text, str(away_team['away_score']))
        graphics.DrawText(self.canvas, self.small_font, 2, 14, away_text, "AWAY")
        
        # Home team section (bottom half)
        home_bg_color = self.team_colors.get(home_team_abbr, {}).get('home', '#1E1E1E')
        home_text_color = self.team_colors.get(home_team_abbr, {}).get('away', '#FFFFFF')
        
        home_bg_r, home_bg_g, home_bg_b = self.hex_to_color(home_bg_color)
        home_text_r, home_text_g, home_text_b = self.hex_to_color(home_text_color)
        home_text = graphics.Color(home_text_r, home_text_g, home_text_b)
        
        for x in range(64):
            for y in range(16, 32):
                self.canvas.SetPixel(x, y, home_bg_r, home_bg_g, home_bg_b)
        
        graphics.DrawText(self.canvas, self.font, 2, 23, home_text, home_team_abbr)
        if is_final or is_live:
            graphics.DrawText(self.canvas, self.font, 28, 23, home_text, str(home_team['home_score']))
        graphics.DrawText(self.canvas, self.small_font, 2, 30, home_text, "HOME")
        
        # Draw black background box on the right for game info
        for x in range(35, 64):
            for y in range(32):
                self.canvas.SetPixel(x, y, 0, 0, 0)
        
        # Draw game status
        if is_final:
            try:
                game_date = pd.to_datetime(home_team['date'])
                date_str = game_date.strftime("%m/%d")
                graphics.DrawText(self.canvas, self.small_font, 37, 24, red, date_str)
                graphics.DrawText(self.canvas, self.small_font, 37, 16, red, "Final")
            except Exception as e:
                print(f"Error parsing final game date: {e}")
                graphics.DrawText(self.canvas, self.small_font, 37, 14, red, "Final")
        elif is_live:
            clock = home_team.get('displayClock', 'Live')
            graphics.DrawText(self.canvas, self.small_font, 37, 14, red, clock)
        else:
            try:
                game_date = pd.to_datetime(home_team['date'])
                date_str = game_date.strftime("%m/%d")
                time_str = game_date.strftime("%I:%M%p").lstrip('0').lower()
                graphics.DrawText(self.canvas, self.small_font, 37, 8, red, date_str)
                graphics.DrawText(self.canvas, self.small_font, 37, 16, red, time_str)
            except Exception as e:
                print(f"Error parsing upcoming game date: {e}")
                graphics.DrawText(self.canvas, self.small_font, 37, 14, red, "Soon")
        
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
    
    def run(self):
        """Main display loop"""
        try:
            print("Starting main loop...")
            last_reload = time.time()
            
            while True:
                # Reload data every 45 seconds
                if time.time() - last_reload >= 45:
                    try:
                        json_path = '/tmp/nwsl_schedule.json'
                        with open(json_path, 'r') as f:
                            self.schedule_data = json.load(f)
                        print(f"[{time.strftime('%H:%M:%S')}] Reloaded schedule data")
                        last_reload = time.time()
                    except Exception as e:
                        print(f"Error reloading: {e}")
                
                matchups = self.group_games_by_event()
                
                if not matchups:
                    print("No games to display")
                    time.sleep(10)
                    continue
                
                for i, matchup in enumerate(matchups):
                    # Check for goals
                    scoring_team = self.check_for_goals(matchup)
                    if scoring_team:
                        print(f"GOAL! {scoring_team} scored!")
                        self.draw_goal_animation(scoring_team)
                    
                    print(f"Displaying matchup {i+1}/{len(matchups)}")
                    self.draw_matchup(matchup)
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            self.matrix.Clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NWSL LED Scoreboard')
    parser.add_argument('--team', type=str, 
                        help='Filter by favorite team (e.g., SD, BAY, CHI)')
    args = parser.parse_args()
    
    scoreboard = NWSLScoreboard(favorite_team=args.team)
    scoreboard.run()
