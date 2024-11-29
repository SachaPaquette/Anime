try {
    # Load the AnimeWatcherEnv python environment
    & .\AnimeWatcherEnv\Scripts\Activate.ps1
    
    # Check if Chocolatey is installed
    if (-not (Get-Command "choco" -ErrorAction SilentlyContinue)) {
        # Install Chocolatey
        Write-Host "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    } else {
        Write-Host "Chocolatey is already installed."
    }

    if (-not (Get-Package -Name "Google Chrome" -ErrorAction SilentlyContinue)) {
        # Download and install Google Chrome
        Write-Host "Opening Google Chrome webpage..."
        Start-Process "https://www.google.com/intl/en_ca/chrome/"
    } else {
        Write-Host "Google Chrome is already installed."
    }

    # Check if MPV is installed
    if (-not (choco list --local-only | Where-Object { $_ -match "mpv" })) {
        # Download and install MPV
        Write-Host "Downloading and installing MPV..."
        choco install mpv -y
    } else {
        Write-Host "MPV is already installed."
    }

    if (-not (Get-Command -Name "python" -ErrorAction SilentlyContinue)) {
        #Download Python to the machine
        choco install python --pre 
    } else {
        Write-Host "Python is already installed."
    }

    # Installing Python dependencies
    Write-Host "Now installing Python dependencies..."
    pip install -r Requirements/requirements.txt

} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
