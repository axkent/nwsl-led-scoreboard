# Start Guide

An LED scoreboard for the National Women's Soccer League (NWSL). Displays a live scoreboard for your team's game on that day.

## Prerequisites

- Requires a Raspberry Pi 4 and an LED board hooked up via the GPIO pins.
- Internet connection

**For users new to Raspberry Pi:**
This [Adafruit wishlist](https://www.adafruit.com/wishlists/612118) contains the materials I used to get this project and other popular LED projects to work. The [MLB-LED-Scoreboard Wiki](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki) has helpful guidance on getting started. This [YouTube video](https://www.youtube.com/watch?v=7sL1TUR2JeM) was helpful in figuring out how to set up the Matrix Bonnet. 

I may draft a how-to video in the near future for more guidance. 

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
# San Diego Wave FC
sudo ./venv/bin/python3 main.py --team SD

# Bay FC
sudo ./venv/bin/python3 main.py --team BAY

# Seattle Reign FC
sudo ./venv/bin/python3 main.py --team SEA
```

**Team Codes:**
- SD (San Diego Wave FC), BAY (Bay FC), SEA (Seattle Reign FC)
- KC (KC Current), UTA (Utah Royals FC), LOU (Racing Louisville)
- ORL (Orlando Pride), WAS (Washington Spirit), POR (Portland Thorns)
- GFC (Gotham FC), LA (Angel City FC), CHI (Chicago Stars)
- NC (North Carolina Courage), HOU (Houston Dash)

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

### Acknowledgements
This project was heavily inspired by [MLB-LED-Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard). 
