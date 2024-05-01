#!/bin/bash
# Check the operating system
if dpkg -l | grep -q google-chrome-stable; then
    echo "Google Chrome is already installed."
else
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Download and install Google Chrome
        echo "Downloading and installing Google Chrome..."
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        # Install the package
        sudo dpkg -i google-chrome-stable_current_amd64.deb
        # Check the exit code of the last command
        if [ $? -ne 0 ]; then
            echo "Error installing Google Chrome"
            exit 1
        fi
        sudo apt-get install -f  
        # Clean up the package file
        rm google-chrome-stable_current_amd64.deb

        # Download and install MPV
        echo "Downloading and installing MPV..."
        sudo apt-get install mpv
        # Check the exit code of the last command
        if [ $? -ne 0 ]; then
            echo "Error installing MPV"
            exit 1
        fi
    else 
        echo "Operating system not supported."
        exit 1
    fi
    echo "Installation complete."
fi
