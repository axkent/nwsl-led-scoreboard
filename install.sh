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
    echo "   Virtual environment already exists, removing and recreating..."
    rm -rf venv
fi
python3 -m venv venv
echo "   ✓ Virtual environment created"

echo ""
echo "Step 3: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✓ Python packages installed"

echo ""
echo "Step 4: Installing RGB Matrix library..."
RGB_DIR="$HOME/rpi-rgb-led-matrix"

# Check if directory exists
if [ -d "$RGB_DIR" ]; then
    echo "   RGB Matrix library directory already exists at $RGB_DIR"
    # Check if it's already built
    if [ -f "$RGB_DIR/lib/librgbmatrix.so.1" ]; then
        echo "   Library appears to be already built"
        read -p "   Do you want to rebuild it? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "   Skipping rebuild..."
            SKIP_BUILD=1
        else
            echo "   Cleaning up old installation..."
            cd "$RGB_DIR"
            make clean
            cd bindings/python
            sudo python3 setup.py clean --all 2>/dev/null || true
            cd "$HOME"
            sudo rm -rf "$RGB_DIR"
            SKIP_BUILD=0
        fi
    else
        # Directory exists but not built - rebuild
        echo "   Directory exists but library not built. Rebuilding..."
        sudo rm -rf "$RGB_DIR"
        SKIP_BUILD=0
    fi
else
    SKIP_BUILD=0
fi

# Clone and build if needed
if [ "$SKIP_BUILD" -eq 0 ]; then
    echo "   Cloning rpi-rgb-led-matrix repository..."
    cd "$HOME"
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    
    echo "   Building RGB Matrix library (this takes 5-10 minutes)..."
    cd "$RGB_DIR"
    make
    
    echo "   Building Python bindings..."
    cd bindings/python
    make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)
fi

# Verify the library is installed system-wide
echo "   Verifying installation..."
if ! python3 -c "import rgbmatrix" 2>/dev/null; then
    echo ""
    echo "❌ Error: rgbmatrix library is not importable!"
    echo "   The build may have failed. Check error messages above."
    exit 1
fi

echo "   ✓ RGB Matrix library installed system-wide"

# Copy to virtual environment
echo "   Copying library to virtual environment..."
cd "$SCRIPT_DIR"
source venv/bin/activate

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
SITE_PACKAGES="$SCRIPT_DIR/venv/lib/python${PYTHON_VERSION}/site-packages"

# Get the system-wide installation location
RGBMATRIX_PATH=$(python3 -c "import rgbmatrix, os; print(os.path.dirname(rgbmatrix.__file__))")

if [ -d "$RGBMATRIX_PATH" ]; then
    # Copy the entire rgbmatrix module
    cp -r "$RGBMATRIX_PATH" "$SITE_PACKAGES/"
    echo "   ✓ RGB Matrix library copied to virtual environment"
else
    echo "   ⚠️  Warning: Could not find rgbmatrix module to copy"
    echo "   Trying alternative method..."
    
    # Alternative: try to find the .so files and copy them
    if [ -f "$RGB_DIR/bindings/python/rgbmatrix/core.so" ]; then
        mkdir -p "$SITE_PACKAGES/rgbmatrix"
        cp "$RGB_DIR/bindings/python/rgbmatrix/"*.so "$SITE_PACKAGES/rgbmatrix/"
        cp "$RGB_DIR/bindings/python/rgbmatrix/"*.py "$SITE_PACKAGES/rgbmatrix/" 2>/dev/null || true
        echo "   ✓ RGB Matrix files copied manually"
    else
        echo "   ⚠️  Could not copy library to venv"
        echo "   The system-wide installation should still work with sudo"
    fi
fi

echo ""
echo "Step 5: Creating fonts directory..."
cd "$SCRIPT_DIR"
if [ ! -d "fonts" ]; then
    mkdir -p fonts
fi
cp "$RGB_DIR/fonts/5x7.bdf" fonts/
cp "$RGB_DIR/fonts/4x6.bdf" fonts/
echo "   ✓ Fonts copied"

echo ""
echo "Step 6: Making scripts executable..."
chmod +x main.py
chmod +x nwsl-live.py
chmod +x run_nwsl_scoreboard.py
chmod +x auto_refresh.py
chmod +x stop_scoreboard.sh
echo "   ✓ Scripts are executable"

echo ""
echo "Step 7: Testing installation..."
source venv/bin/activate
if python3 -c "import rgbmatrix" 2>/dev/null; then
    echo "   ✓ rgbmatrix can be imported from venv"
else
    echo "   ⚠️  rgbmatrix cannot be imported from venv"
    echo "   You'll need to use the system Python with sudo"
fi

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
echo "   sudo venv/bin/python3 main.py"
echo ""
echo "2. Filter by team (e.g., San Diego):"
echo "   sudo venv/bin/python3 main.py --team SD"
echo ""
echo "3. Change timezone (e.g., Eastern):"
echo "   sudo venv/bin/python3 main.py --tz America/New_York"
echo ""
echo "For continuous operation, see the 'Auto-Refresh Mode' section in README.md"
echo ""
echo "To stop the scoreboard at any time:"
echo "   ./stop_scoreboard.sh"
echo ""
