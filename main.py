#!/usr/bin/env python3
"""
Main script to fetch NWSL data and display on LED matrix
Usage:
    sudo python3 main.py                              # Show all games (Pacific time)
    sudo python3 main.py --team SD                    # Show only SD games
    sudo python3 main.py --tz America/New_York        # Use Eastern time
    sudo python3 main.py --team BAY --tz America/Chicago  # Team filter + Central time
"""
import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='NWSL LED Scoreboard - Fetch and Display')
    parser.add_argument('--team', type=str, help='Filter by favorite team (e.g., SD, BAY, CHI)')
    parser.add_argument('--tz', type=str, default='America/Los_Angeles', 
                        help='Timezone (default: America/Los_Angeles). Examples: America/New_York, America/Chicago, America/Denver')
    args = parser.parse_args()

    print("=" * 60)
    print("NWSL LED Scoreboard")
    print(f"Timezone: {args.tz}")  # ADDED: Show timezone being used
    print("=" * 60)

    # Step 1: Fetch latest data
    print("\n[1/2] Fetching latest NWSL data from ESPN API...")
    try:
        result = subprocess.run(['sudo', 'python3', 'nwsl-live.py', '--tz', args.tz],
                                capture_output=True,
                                text=True,
                                check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching data: {e}")
        print(e.stderr)
        sys.exit(1)

    # Step 2: Run the scoreboard
    print("\n[2/2] Starting LED matrix display...")
    if args.team:
        print(f"Filtering for team: {args.team}")
        subprocess.run(['python3', 'run_nwsl_scoreboard.py', '--team', args.team])
    else:
        print("Showing all games")
        subprocess.run(['python3', 'run_nwsl_scoreboard.py'])

if __name__ == "__main__":
    main()
