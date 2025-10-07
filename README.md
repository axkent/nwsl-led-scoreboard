# NWSL LED Scoreboard

Display live NWSL (National Women's Soccer League) scores and schedules on an RGB LED matrix powered by Raspberry Pi.

![NWSL Scoreboard Demo](https://img.shields.io/badge/status-active-success)

## Features

- 🏆 Live game scores with real-time updates
- 📅 Upcoming game schedules with date/time
- ⚽ Goal animations when scores change
- 🎨 Team-specific color schemes
- 🔄 Auto-refresh every 45 seconds
- 🌍 Timezone support (Pacific, Eastern, Central, Mountain, etc.)
- 👥 Filter by favorite team or show all games

## Hardware Requirements

**Note:** This project has been tested and confirmed working with:
- Raspberry Pi 4
- 64x32 RGB LED Matrix
- Adafruit RGB Matrix Bonnet

While other configurations (Raspberry Pi 3B+, 5, or HAT instead of Bonnet) may work, they have not been tested. You may need to adjust the `hardware_mapping` setting in the configuration.

**For users new to Raspberry Pi:**
This [Adafruit wishlist](https://www.adafruit.com/wishlists/612118) contains the materials I used to get this project and other popular LED projects to work. The [MLB-LED-Scoreboard Wiki](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard/wiki) has helpful guidance on getting started. This [YouTube video](https://www.youtube.com/watch?v=7sL1TUR2JeM) was helpful in figuring out how to set up the Matrix Bonnet. I may draft a how-to video in the near future for more guidance.

## Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- Internet connection

## Installation

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/yourusername/nwsl-led-scoreboard.git
cd nwsl-led-scoreboard
```

### 2. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv git
```

### 3. Set Up Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Install RGB Matrix Library

The `rpi-rgb-led-matrix` library requires building from source:

```bash
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

Copy the built library to your virtual environment:

```bash
cp bindings/python/rgbmatrix.so ~/nwsl-led-scoreboard/venv/lib/python3.*/site-packages/
```

### 6. Configure Your LED Matrix

Edit `/home/pi/rpi-rgb-led-matrix/bindings/python/rgbmatrix/core.pyx` if your hardware differs from the default Adafruit HAT configuration.

## Usage

### Quick Start (Show All Games)

```bash
cd ~/nwsl-led-scoreboard
source venv/bin/activate
sudo ./venv/bin/python3 main.py
```

### Filter by Favorite Team

```bash
sudo ./venv/bin/python3 main.py --team SD
```

Available team codes: 
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

### Change Timezone

```bash
# Eastern Time
sudo ./venv/bin/python3 main.py --tz America/New_York

# Central Time
sudo ./venv/bin/python3 main.py --tz America/Chicago

# Mountain Time
sudo ./venv/bin/python3 main.py --tz America/Denver
```

### Auto-Refresh Mode

For continuous operation with automatic data updates:

```bash
# Terminal 1: Start auto-refresh service
source venv/bin/activate
python3 auto_refresh.py --tz America/Los_Angeles

# Terminal 2: Start display
source venv/bin/activate
sudo ./venv/bin/python3 run_nwsl_scoreboard.py
```

Or use `screen` or `tmux` to run both in the background:

```bash
screen -dmS nwsl-refresh bash -c "cd ~/nwsl-led-scoreboard && source venv/bin/activate && python3 auto_refresh.py"
screen -dmS nwsl-display bash -c "cd ~/nwsl-led-scoreboard && source venv/bin/activate && sudo ./venv/bin/python3 run_nwsl_scoreboard.py"
```

### Stop the Scoreboard

```bash
./stop_scoreboard.sh
```

## Run at Startup (Optional)

To automatically start the scoreboard when your Raspberry Pi boots:

1. Edit your crontab:
```bash
sudo crontab -e
```

2. Add these lines:
```bash
@reboot sleep 30 && cd /home/pi/nwsl-led-scoreboard && /home/pi/nwsl-led-scoreboard/venv/bin/python3 auto_refresh.py --tz America/Los_Angeles > /tmp/nwsl_refresh.log 2>&1 &
@reboot sleep 35 && cd /home/pi/nwsl-led-scoreboard && sudo /home/pi/nwsl-led-scoreboard/venv/bin/python3 run_nwsl_scoreboard.py > /tmp/nwsl_display.log 2>&1 &
```

## Troubleshooting

### Permission Denied Errors

The LED matrix requires root access. Always use `sudo` when running `main.py` or `run_nwsl_scoreboard.py`.

### Module Not Found: rgbmatrix

Make sure you've copied the `rgbmatrix.so` file to your virtual environment's site-packages directory (see Installation Step 5).

### No Games Displayed

- Check your internet connection
- Verify the NWSL season is active (typically March-November)
- Check `/tmp/nwsl_schedule.json` to see what data was fetched

### Display Issues

- Verify your LED matrix is properly connected
- Check hardware_mapping setting in `run_nwsl_scoreboard.py` (line 48)
- Adjust brightness if needed (line 49)

## Configuration

### Adjusting Display Settings

Edit `run_nwsl_scoreboard.py`:

```python
options.rows = 32          # Matrix height
options.cols = 64          # Matrix width
options.brightness = 75    # 0-100
options.hardware_mapping = 'adafruit-hat'  # or 'regular', 'adafruit-hat-pwm'
```

### Changing Refresh Interval

Edit `auto_refresh.py`:

```python
REFRESH_INTERVAL = 45  # Change to desired seconds
```

### Modifying Team Colors

Edit the `team_colors` dictionary in `run_nwsl_scoreboard.py` (starting at line 22).

## Project Structure

```
nwsl-led-scoreboard/
├── main.py                    # Main entry point
├── nwsl-live.py              # ESPN API data fetcher
├── run_nwsl_scoreboard.py    # LED display controller
├── auto_refresh.py           # Background refresh service
├── stop_scoreboard.sh        # Stop all processes
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── venv/                     # Virtual environment (created during setup)
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

This project was heavily inspired by [MLB-LED-Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard).

- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) by Henner Zeller
- ESPN API for NWSL data
- NWSL teams and fans

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review logs in `/tmp/nwsl_refresh.log` and `/tmp/nwsl_display.log`
3. Open an issue on GitHub with details about your setup and error messages

---

**Enjoy your NWSL LED Scoreboard!** ⚽✨
