# Quick Start Guide

Get your NWSL LED Scoreboard up and running in 5 minutes!

## Prerequisites

- Raspberry Pi with RGB LED matrix connected
- Internet connection
- Fresh Raspberry Pi OS installation

## Installation (One Command)

```bash
cd ~
git clone https://github.com/yourusername/nwsl-led-scoreboard.git
cd nwsl-led-scoreboard
chmod +x install.sh
./install.sh
```

The installation script will:
1. Install system dependencies
2. Create a Python virtual environment
3. Install required Python packages
4. Build and install the RGB Matrix library
5. Copy necessary fonts

**Installation takes about 5-10 minutes.**

## First Run

After installation completes, test your scoreboard:

```bash
sudo ./venv/bin/python3 main.py
```

This will:
- Fetch the latest NWSL game data
- Display it on your LED matrix
- Use Pacific Time by default
- Show all teams

## Common Commands

### Show Only Your Favorite Team

```bash
# San Diego Wave
sudo ./venv/bin/python3 main.py --team SD

# Bay FC
sudo ./venv/bin/python3 main.py --team BAY

# Seattle Reign
sudo ./venv/bin/python3 main.py --team SEA
```

**Team Codes:**
- SD (San Diego Wave FC)
- BAY (Bay FC)
- SEA (Seattle Reign FC)
- KC (Kansas City Current)
- UTA (Utah Royals FC)
- LOU (Racing Louisville FC)
- ORL (Orlando Pride)
- WAS (Washington Spirit)
- POR (Portland Thorns FC)
- GFC (NJ/NY Gotham FC)
- LA (Angel City FC)
- CHI (Chicago Red Stars)
- NC (North Carolina Courage)
- HOU (Houston Dash)

### Use Your Local Timezone

```bash
# Eastern Time
sudo ./venv/bin/python3 main.py --tz America/New_York

# Central Time
sudo ./venv/bin/python3 main.py --tz America/Chicago

# Mountain Time
sudo ./venv/bin/python3 main.py --tz America/Denver
```

### Stop the Scoreboard

Press `Ctrl+C` or run:

```bash
./stop_scoreboard.sh
```

## Continuous Mode (Recommended)

For 24/7 operation with automatic updates:

### Option 1: Using two terminals

**Terminal 1
