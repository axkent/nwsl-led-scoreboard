# NWSL LED Scoreboard

An LED scoreboard for the National Women's Soccer League (NWSL). Displays live scores and schedules for your favorite team on a Raspberry Pi-powered LED matrix.

![NWSL Scoreboard](https://img.shields.io/badge/status-active-success) ![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-red)

![IMG_6962](https://github.com/user-attachments/assets/9b468052-b406-4b66-ae9b-7121ad3d1457)

![IMG_6961](https://github.com/user-attachments/assets/07e25b9d-e83e-4a65-9da0-76bfb7ea8bac)

## Features

- 🏆 Live game scores with real-time updates
- 📅 Upcoming game schedules with date/time
- ⚽ Goal animations when scores change
- 🎨 Team-specific color schemes
- 🔄 Auto-refresh every 45 seconds
- 🌍 Timezone support (Pacific, Eastern, Central, Mountain, etc.)
- 👥 Filter by favorite team or show all games

## Hardware Requirements

**Tested Configuration:**
- Raspberry Pi 4
- 64x32 RGB LED Matrix
- Adafruit RGB Matrix Bonnet
- 5V Power Supply (4A+ recommended for LED matrix)

**Note:** This project has been tested and confirmed working with the configuration above. Other setups (Raspberry Pi 3B+, 5, HAT instead of Bonnet, different matrix sizes) may work but have not been tested. You may need to adjust the `hardware_mapping` setting in `run_nwsl_scoreboard.py`.

**For users new to Raspberry Pi:**
This [Adafruit wishlist](https://www.adafruit.com/wishlists/612118) contains the materials I used to get this project and other popular LED projects to work. The [MLB-LED-Scoreboard Wiki](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki) has helpful guidance on getting started. This [YouTube video](https://www.youtube.com/watch?v=7sL1TUR2JeM) was helpful in figuring out how to set up the Matrix Bonnet. I may draft a how-to video in the near future for more guidance.

## Prerequisites

- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- Internet connection

## Installation (One Command)

```bash
git clone https://github.com/axkent/nwsl-led-scoreboard.git
cd nwsl-led-scoreboard
bash install.sh
```

The installation script will:
1. Install system dependencies
2. Create a Python virtual environment
3. Install required Python packages
4. Build and install the RGB Matrix library
5. Copy necessary fonts

**Installation takes about 5-10 minutes.**

## Usage

### First Run - Test Your Scoreboard

After installation completes, test your scoreboard:

```bash
cd nwsl-led-scoreboard
sudo venv/bin/python3 main.py
```

This will:
- Fetch the latest NWSL game data from ESPN
- Start auto-refresh (updates every 45 seconds)
- Display games on your LED matrix
- Use Pacific Time by default
- Show all teams

Press `Ctrl+C` to stop.

### Show Only Your Favorite Team

```bash
cd nwsl-led-scoreboard
sudo venv/bin/python3 main.py --team SD

# Or other teams:
sudo venv/bin/python3 main.py --team BAY
sudo venv/bin/python3 main.py --team SEA
```

**Team Codes:**
- `SD` - San Diego Wave FC
- `BAY` - Bay FC
- `SEA` - Seattle Reign FC
- `KC` - Kansas City Current
- `UTA` - Utah Royals FC
- `LOU` - Racing Louisville FC
- `ORL` - Orlando Pride
- `WAS` - Washington Spirit
- `POR` - Portland Thorns FC
- `GFC` - NJ/NY Gotham FC
- `LA` - Angel City FC
- `CHI` - Chicago Red Stars
- `NC` - North Carolina Courage
- `HOU` - Houston Dash

### Use Your Local Timezone

```bash
cd nwsl-led-scoreboard

# Eastern Time
sudo venv/bin/python3 main.py --tz America/New_York

# Central Time
sudo venv/bin/python3 main.py --tz America/Chicago

# Mountain Time
sudo venv/bin/python3 main.py --tz America/Denver
```

### Auto-Refresh Mode (Built-in)

The scoreboard now automatically refreshes data every 45 seconds when you run `main.py`. No additional setup needed!

The display will:
- Update live game scores in real-time
- Refresh the game clock every 45 seconds
- Switch between multiple games if showing all teams

Just run:
```bash
cd nwsl-led-scoreboard
sudo venv/bin/python3 main.py
```

Press `Ctrl+C` to stop both the refresh and display.

### Stop the Scoreboard

Press `Ctrl+C` in the terminal where the scoreboard is running.

Or use the stop script:
```bash
cd nwsl-led-scoreboard
bash stop_scoreboard.sh
```

## Configuration

### Adjust LED Matrix Settings

Edit `run_nwsl_scoreboard.py` (around line 95):

```python
options.rows = 32          # Matrix height
options.cols = 64          # Matrix width
options.brightness = 75    # 0-100
options.hardware_mapping = 'adafruit-hat'  # Change to 'adafruit-hat-pwm' for Bonnet
```

### Change Data Refresh Interval

Edit `auto_refresh.py`:

```python
REFRESH_INTERVAL = 45  # Change to desired seconds
```

### Modify Team Colors

Edit the `team_colors` dictionary in `run_nwsl_scoreboard.py` (starting around line 22).

## Troubleshooting

### Permission Denied Errors
The LED matrix requires root access. Always use `sudo` when running `main.py` or `run_nwsl_scoreboard.py`.

### Module Not Found: rgbmatrix
Make sure you've run the `install.sh` script completely. The RGB matrix library should be copied to your virtual environment.

### No Games Displayed
- Check your internet connection
- Verify the NWSL season is active (typically March-November)
- Check `/tmp/nwsl_schedule.json` to see what data was fetched
- Try running `sudo python3 nwsl-live.py` manually to test the data fetch

### Fonts Not Found
The install script copies fonts to a `fonts/` directory in the project. If you see font errors, verify the fonts exist:
```bash
ls nwsl-led-scoreboard/fonts/
```

### Display Issues
- Verify your LED matrix is properly connected to GPIO pins
- Try changing `hardware_mapping` from `'adafruit-hat'` to `'adafruit-hat-pwm'`
- Check that your power supply provides enough current (4A+ recommended)
- Adjust brightness if the display is too dim or too bright

## Project Structure

```
nwsl-led-scoreboard/
├── main.py                    # Main entry point - fetches data and starts display
├── nwsl-live.py              # ESPN API data fetcher
├── run_nwsl_scoreboard.py    # LED display controller
├── auto_refresh.py           # Background refresh service
├── stop_scoreboard.sh        # Stop all processes
├── install.sh                # Installation script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── fonts/                    # BDF fonts (created during install)
└── venv/                     # Virtual environment (created during install)
```

## How It Works

1. **Data Fetching**: `nwsl-live.py` queries the ESPN NWSL API for game data
2. **Data Processing**: Games are filtered to show live games, recent finals (within 24 hours), or next upcoming games
3. **Display**: `run_nwsl_scoreboard.py` renders the games on your LED matrix with team colors
4. **Auto-Refresh**: `auto_refresh.py` keeps the data fresh by re-fetching every 45 seconds

## Run at Startup (Optional)

To automatically start the scoreboard when your Raspberry Pi boots:

1. Edit your crontab:
```bash
sudo crontab -e
```

2. Add these lines (adjust paths if needed):
```bash
@reboot sleep 30 && cd /home/pi/nwsl-led-scoreboard && /home/pi/nwsl-led-scoreboard/venv/bin/python3 auto_refresh.py --tz America/Los_Angeles > /tmp/nwsl_refresh.log 2>&1 &
@reboot sleep 35 && cd /home/pi/nwsl-led-scoreboard && sudo /home/pi/nwsl-led-scoreboard/venv/bin/python3 run_nwsl_scoreboard.py > /tmp/nwsl_display.log 2>&1 &
```

## Data Source

Game data is fetched from the ESPN NWSL API in real-time. No API key required.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This project is provided "as is" without warranty of any kind. I am not responsible for any damage to your hardware, software, or data that may result from using this project. Use at your own risk.

This is a hobby project and is not affiliated with or endorsed by NWSL, ESPN, Adafruit, or any teams.

## License

MIT License - feel free to use and modify for your own projects.

## Acknowledgments

- This project was heavily inspired by [MLB-LED-Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard).
- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) by Henner Zeller
- ESPN API for NWSL data
- NWSL teams and fans


## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review logs in `/tmp/nwsl_refresh.log` and `/tmp/nwsl_display.log` (if using cron)
3. Open an issue on GitHub with details about your setup and error messages
