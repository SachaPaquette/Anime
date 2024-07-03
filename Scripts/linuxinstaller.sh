#!/bin/bash

# Function to check if a program is installed
check_installation() {
    if which $1 > /dev/null 2>&1; then
        echo "$1 is installed."
    else
        echo "$1 is not installed."
    fi
}

# Function to install a program using apt-get
install_program() {
    echo "Installing $1..."
    sudo apt-get install -y $1
    if [ $? -ne 0 ]; then
        echo "Error installing $1"
        exit 1
    fi
}

# Function to install a program using yum
install_program_yum() {
    echo "Installing $1..."
    sudo yum install -y $1
    if [ $? -ne 0 ]; then
        echo "Error installing $1"
        exit 1
    fi
}

install_program_pacman() {
    echo "Installing $1..."
    sudo pacman -S --noconfirm $1
    if [ $? -ne 0 ]; then
        echo "Error installing $1"
        exit 1
    fi
}

# Function to detect the Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    else
        echo "Unknown"
    fi
}

# Check the operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then

    # Check if virtual environment directory exists
    if [ -d "AnimeWatcherEnv" ]; then
        # Activate the virtual environment
        source AnimeWatcherEnv/bin/activate 
    else
        echo "Virtual environment not found."
        exit 1
    fi

    # Detect the Linux distribution
    DISTRO=$(detect_distro)
    echo "Detected Linux distribution: $DISTRO"

    case $DISTRO in
        ubuntu|debian)
            PKG_MANAGER="apt-get"
            INSTALL_FUNC=install_program
            ;;
        centos|fedora|rhel)
            PKG_MANAGER="yum"
            INSTALL_FUNC=install_program_yum
            ;;
        # For arch-based distributions
        arch)
            PKG_MANAGER="pacman"
            INSTALL_FUNC=install_program_pacman
            ;;
        *)
        # For other distributions, exit the script
            echo "Unsupported Linux distribution: $DISTRO"
            exit 1
            ;;
    esac

    # Check if google-chrome is installed
    check_installation "google-chrome"
    # Check if MPV is installed
    check_installation "mpv"
    
    # Install Google Chrome if not installed
    if ! which google-chrome > /dev/null 2>&1; then
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo dpkg -i google-chrome-stable_current_amd64.deb
        sudo $PKG_MANAGER install -f  
        rm google-chrome-stable_current_amd64.deb
    fi

    # Install MPV if not installed
    if ! which mpv > /dev/null 2>&1; then
        $INSTALL_FUNC "mpv"
    fi

    echo "Now installing Python dependencies..."
    pip install -r Requirements/requirements.txt

else 
    echo "Operating system not supported."
    exit 1
fi
# Clear the terminal
clear
# Display installation complete message
echo "Installation complete. Run the program using 'python animewatch.py'"
