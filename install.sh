#!/bin/bash
# Shadow Installation Script
# For Linux & Termux

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              SHADOW - Installation Script                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found! Installing..."
    if command -v apt &> /dev/null; then
        apt update && apt install -y python3 python3-pip
    elif command -v pkg &> /dev/null; then
        pkg install -y python python-pip
    else
        echo "[✗] Cannot install Python automatically. Please install manually."
        exit 1
    fi
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "[!] pip3 not found! Installing..."
    python3 -m ensurepip --upgrade
fi

# Install dependencies
echo "[*] Installing dependencies..."
pip3 install -r requirements.txt

# Make shadow executable
echo "[*] Setting up executable..."
chmod +x src/shadow.py

# Create symlink (optional)
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$(pwd)/src/shadow.py" "$HOME/.local/bin/shadow"
    echo "[✓] Created symlink: shadow -> $(pwd)/src/shadow.py"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Installation Complete! ✓                         ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Run: python3 src/shadow.py                                  ║"
echo "║  Or:  shadow (if symlink created)                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
