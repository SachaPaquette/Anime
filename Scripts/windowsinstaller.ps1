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
    $chrome = Get-Package -Name "Google Chrome" -ErrorAction SilentlyContinue
    if (-not $chrome) {
        # Download and install Google Chrome
        Write-Host "Openning Google Chrome webpage..."
        Start "https://www.google.com/intl/fr_ca/chrome/next-steps.html?statcb=1&installdataindex=empty&defaultbrowser=0#"
    } else {
        Write-Host "Google Chrome is already installed."
    }

    # Check if MPV is installed
    $mpv = choco list --local-only | Where-Object { $_ -match "mpv" }
    if (-not $mpv) {
        # Download and install MPV
        Write-Host "Downloading and installing MPV..."
        choco install mpv -y
    } else {
        Write-Host "MPV is already installed."
    }

} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
