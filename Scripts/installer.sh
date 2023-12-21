#!/bin/bash

# Download and install Google Chrome
echo "Downloading and installing Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Install dependencies
rm google-chrome-stable_current_amd64.deb # Remove the 

# Download and install MPV
echo "Downloading and installing MPV..."
sudo apt-get install mpv

echo "Installation complete."
