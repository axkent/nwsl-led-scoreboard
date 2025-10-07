#!/usr/bin/env python3
"""
Main script to fetch NWSL data and display on LED matrix with auto-refresh
Usage:
    sudo python3 main.py                              # Show all games (Pacific time)
    sudo python3 main.py --team SD                    # Show only SD games
    sudo python3 main.py --tz America/New_York        # Use Eastern time
    sudo python3 main.py --team BAY --tz America/Chicago  # Team filter + Central time
"""
import subprocess
import sys
import argparse
import time
import signal
import os

# Global variable to track child processes
refresh_process = None
display_process = None

def cleanup(signum, frame):
    """Clean up child processes on exit"""
    print("\n\nStopping scoreboard...")
    if refresh_process:
        refresh_process.terminate()
    if display_process:
        display_process.terminate()
    sys.exit(0)

def main():
    global refresh_process, display_process
    
    parser = argparse.ArgumentParser(description='NWSL LED Scoreboard - Fetch and Display')
    parser.add_argument('--team', type=str, help='Filter by favorite team (e.g., SD, BAY, CHI)')
    parser.add_argument('--tz', type=str, default='America/Los_Angeles', 
                        help='Timezone (default: America/Los_Angeles). Examples: America/New_York, America/Chicago, America/Denver')
    args = parser.parse_args()

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("=" * 60)
    print("NWSL LED Scoreboard")
    print(f"Timezone: {args.tz}")
    if args.team:
        print(f"Team filter: {args.team}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Step 1: Initial data fetch
    print("\n[1/3] Fetching initial NWSL data from ESPN API...")
    try:
        result = subprocess.run(['python3', 'nwsl-live.py', '--tz', args.tz],
                                capture_output=True,
                                text=True,
                                check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching data: {e}")
        print(e.stderr)
        sys.exit(1)

    # Step 2: Start auto-refresh in background
    print("\n[2/3] Starting auto-refresh service (updates every 45 seconds)...")
    refresh_process = subprocess.Popen(
        ['python3', 'auto_refresh.py', '--tz', args.tz],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    print("   ✓ Auto-refresh started")

    # Give it a moment to start
    time.sleep(1)

    # Step 3: Start the display
    print("\n[3/3] Starting LED matrix display...")
    display_cmd = ['python3', 'run_nwsl_scoreboard.py']
    if args.team:
        display_cmd.extend(['--team', args.team])
    
    display_process = subprocess.Popen(
        display_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print("   ✓ Display started")
    print("\n" + "=" * 60)
    print("Scoreboard is running!")
    print("Data will refresh every 45 seconds")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    # Monitor both processes and print their output
    try:
        while True:
            # Check if processes are still running
            if refresh_process.poll() is not None:
                print("⚠️  Auto-refresh process stopped unexpectedly")
                break
            if display_process.poll() is not None:
                print("⚠️  Display process stopped unexpectedly")
                break
            
            # Print any output from refresh process
            if refresh_process.stdout:
                line = refresh_process.stdout.readline()
                if line:
                    print(f"[Refresh] {line.strip()}")
            
            # Print any output from display process
            if display_process.stdout:
                line = display_process.stdout.readline()
                if line:
                    print(f"[Display] {line.strip()}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        cleanup(None, None)

if __name__ == "__main__":
    main()
