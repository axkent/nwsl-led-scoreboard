#!/bin/bash
# NWSL LED Scoreboard Installation Script
# Run this script to set up everything automatically

set -e  # Exit on any error

echo "================================================"
echo "NWSL LED Scoreboard - Installation Script"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   The LED matrix will not work without proper hardware"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Step 1: Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv git build-essential

echo ""
echo "Step 2: Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
fi

echo ""
echo "Step 3: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✓ Python packages installed"

echo ""
echo "Step 4: Installing RGB Matrix library..."
RGB_DIR="$HOME/rpi-rgb-led-matrix"

if [ -d "$RGB_DIR" ]; then
    echo "   RGB Matrix library directory already exists"
    echo "   This usually means you've run this installer before."
    read -p "   Do you want to rebuild it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Cleaning up old installation..."
        sudo rm -rf "$RGB_DIR"
        echo "   ✓ Old directory removed"
    else
        echo "   Skipping RGB Matrix rebuild, will use existing installation"
        # Still need to copy the .so file
        echo "   Checking for rgbmatrix.so..."
        if [ -f "$RGB_DIR/bindings/python/rgbmatrix.so" ]; then
            echo "   Copying library to virtual environment..."
            PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            cp "$RGB_DIR/bindings/python/rgbmatrix.so" "$SCRIPT_DIR/venv/lib/python${PYTHON_VERSION}/site-packages/"
            echo "   ✓ RGB Matrix library copied"
            
            # Skip to fonts step
            echo ""
            echo "Step 5: Creating fonts directory..."
            cd "$SCRIPT_DIR"
            if [ ! -d "fonts" ]; then
                mkdir -p fonts
                cp "$RGB_DIR/fonts/5x7.bdf" fonts/
                cp "$RGB_DIR/fonts/4x6.bdf" fonts/
                echo "   ✓ Fonts copied"
            else
                echo "   Fonts directory already exists"
            fi
            
            echo ""
            echo "Step 6: Making scripts executable..."
            chmod +x main.py
            chmod +x nwsl-live.py
            chmod +x run_nwsl_scoreboard.py
            chmod +x auto_refresh.py
            chmod +x stop_scoreboard.sh
            echo "   ✓ Scripts are executable"
            
            echo ""
            echo "================================================"
            echo "Installation Complete! 🎉"
            echo "================================================"
            echo ""
            echo "Quick Start Commands:"
            echo ""
            echo "1. Show all games (Pacific Time):"
            echo "   cd $SCRIPT_DIR"
            echo "   source venv/bin/activate"
            echo "   sudo ./venv/bin/python3 main.py"
            echo ""
            echo "2. Filter by team (e.g., San Diego):"
            echo "   sudo ./venv/bin/python3 main.py --team SD"
            echo ""
            echo "3. Change timezone (e.g., Eastern):"
            echo "   sudo ./venv/bin/python3 main.py --tz America/New_York"
            echo ""
            echo "For continuous operation, see the 'Auto-Refresh Mode' section in README.md"
            echo ""
            echo "To stop the scoreboard at any time:"
            echo "   ./stop_scoreboard.sh"
            echo ""
            exit 0
        else
            echo "   ⚠️  rgbmatrix.so not found in existing installation"
            echo "   Will rebuild from scratch..."
            sudo rm -rf "$RGB_DIR"
        fi
    fi
fi

if [ ! -d "$RGB_DIR" ]; then
    echo "   Cloning rpi-rgb-led-matrix repository..."
    cd "$HOME"
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
fi

echo "   Building RGB Matrix library (this may take a few minutes)..."
cd "$RGB_DIR"

# Build the main library first
make

# Now build Python bindings
echo "   Building Python bindings..."
cd bindings/python
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

# Check multiple possible locations for the .so file
if [ -f "rgbmatrix.so" ]; then
    SO_FILE="rgbmatrix.so"
elif [ -f "build/lib.linux-aarch64-cpython-311/rgbmatrix.so" ]; then
    SO_FILE="build/lib.linux-aarch64-cpython-311/rgbmatrix.so"
elif [ -f "build/lib.linux-armv7l-cpython-311/rgbmatrix.so" ]; then
    SO_FILE="build/lib.linux-armv7l-cpython-311/rgbmatrix.so"
else
    SO_FILE=""
fi

# Verify the .so file exists
if [ -z "$SO_FILE" ]; then
    echo ""
    echo "❌ Error: rgbmatrix.so was not created!"
    echo "   This usually means the build failed."
    echo "   Check the error messages above."
    exit 1
fi

echo "   Copying library to virtual environment..."
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
cp "$SO_FILE" "$SCRIPT_DIR/venv/lib/python${PYTHON_VERSION}/site-packages/"
echo "   ✓ RGB Matrix library installed"

echo ""
echo "Step 5: Creating fonts directory..."
cd "$SCRIPT_DIR"
if [ ! -d "fonts" ]; then
    mkdir -p fonts
    cp "$RGB_DIR/fonts/5x7.bdf" fonts/
    cp "$RGB_DIR/fonts/4x6.bdf" fonts/
    echo "   ✓ Fonts copied"
else
    echo "   Fonts directory already exists"
fi

echo ""
echo "Step 6: Making scripts executable..."
chmod +x main.py
chmod +x nwsl-live.py
chmod +x run_nwsl_scoreboard.py
chmod +x auto_refresh.py
chmod +x stop_scoreboard.sh
echo "   ✓ Scripts are executable"

echo ""
echo "================================================"
echo "Installation Complete! 🎉"
echo "================================================"
echo ""
echo "Quick Start Commands:"
echo ""
echo "1. Show all games (Pacific Time):"
echo "   cd $SCRIPT_DIR"
echo "   source venv/bin/activate"
echo "   sudo ./venv/bin/python3 main.py"
echo ""
echo "2. Filter by team (e.g., San Diego):"
echo "   sudo ./venv/bin/python3 main.py --team SD"
echo ""
echo "3. Change timezone (e.g., Eastern):"
echo "   sudo ./venv/bin/python3 main.py --tz America/New_York"
echo ""
echo "For continuous operation, see the 'Auto-Refresh Mode' section in README.md"
echo ""
echo "To stop the scoreboard at any time:"
echo "   ./stop_scoreboard.sh"
echo ""
