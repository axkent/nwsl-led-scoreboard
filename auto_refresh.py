#!/usr/bin/env python3

"""
Background data refresh script - runs nwsl-live.py every 15 seconds

Run this in a separate terminal or as a background process

Usage:
    python3 auto_refresh.py                    # Use Pacific time (default)
    python3 auto_refresh.py --tz America/New_York   # Use Eastern time
    python3 auto_refresh.py --tz America/Chicago    # Use Central time
"""

import subprocess
import time
import sys
import argparse

REFRESH_INTERVAL = 15  # 15 seconds


def fetch_data(tz):
    """Run nwsl-live.py to fetch latest data"""
    try:
        # FIX: Removed 'sudo' here — main.py now launches this script with sudo,
        # so calling sudo again inside would cause permission/TTY issues and timeouts.
        result = subprocess.run(
            ['python3', 'nwsl-live.py', '--tz', tz],
            capture_output=True,
            text=True,
            timeout=20,  # FIX: Increased from 12s to 20s to avoid timeout-induced stalls on Pi
            check=True
        )
        print(f"[{time.strftime('%H:%M:%S')}] {result.stdout.strip()}")
        return True
    except subprocess.TimeoutExpired:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Data fetch timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%H:%M:%S')}] ❌ Error fetching data: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='NWSL Auto-Refresh Service')
    parser.add_argument('--tz', type=str, default='America/Los_Angeles',
                        help='Timezone (default: America/Los_Angeles). Examples: America/New_York, America/Chicago')
    args = parser.parse_args()

    print("=" * 60)
    print("NWSL Auto-Refresh Service")
    print(f"Refreshing data every {REFRESH_INTERVAL} seconds")
    print(f"Timezone: {args.tz}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Initial fetch
    print(f"\n[{time.strftime('%H:%M:%S')}] Initial data fetch...")
    fetch_data(args.tz)

    try:
        while True:
            time.sleep(REFRESH_INTERVAL)
            print(f"\n[{time.strftime('%H:%M:%S')}] Refreshing data...")
            fetch_data(args.tz)
    except KeyboardInterrupt:
        print("\n\nStopping auto-refresh service...")
        sys.exit(0)


if __name__ == "__main__":
    main()