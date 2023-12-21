# Script to install Windows applications Google Chrome and MPV using Chocolatey

try {
    # Check if Chocolatey is installed
    if (-not (Get-Command "choco" -ErrorAction SilentlyContinue)) {
        # Install Chocolatey
        Write-Host "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    } else {
        Write-Host "Chocolatey is already installed."
    }

    # Check if Google Chrome is installed
    if (-not (Get-Command "googlechrome" -ErrorAction SilentlyContinue)) {
        # Download and install Google Chrome
        Write-Host "Downloading and installing Google Chrome..."
        choco install googlechrome -y
    } else {
        Write-Host "Google Chrome is already installed."
    }

    # Download and install MPV
    Write-Host "Downloading and installing MPV..."
    choco install mpv
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
