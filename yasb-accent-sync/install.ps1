# ====================================================
# Installer for Komorebi + YASB + Cava + configs
# Sequence: install software → copy configs → autostart
# Author: shk0ln1k
# Version: 6.1 (English)
# ====================================================

param(
    [switch]$SkipSoftwareInstall  # skip software installation, only configs
)

# ---- Admin check ----
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run PowerShell as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
    exit 1
}

# ---- Functions ----
function Write-Step { param($Message) Write-Host ">> $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }

# ---- Check winget ----
Write-Step "Checking winget..."
$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Error "winget not found. Please install App Installer from Microsoft Store."
    Write-Warning "Script cannot install software automatically."
    Write-Warning "You can install software manually, then run script with -SkipSoftwareInstall"
    exit 1
}
Write-Success "winget found."

# ---- Install software ----
if (-not $SkipSoftwareInstall) {
    Write-Step "Installing software via winget..."

    # 1. Komorebi
    Write-Step "Installing Komorebi..."
    winget install LGUG2Z.komorebi --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Komorebi installed."
    } else {
        Write-Error "Failed to install Komorebi."
    }

    # 2. whkd
    Write-Step "Installing whkd..."
    winget install LGUG2Z.whkd --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Success "whkd installed."
    } else {
        Write-Error "Failed to install whkd."
    }

    # 3. YASB
    Write-Step "Installing YASB..."
    winget install AmN.yasb --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Success "YASB installed."
    } else {
        Write-Error "Failed to install YASB."
    }

    # 4. Cava
    Write-Step "Installing Cava..."
    winget install karlstav.cava --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Cava installed."
    } else {
        Write-Error "Failed to install Cava."
    }

    # 5. Visual C++ 2012 (required for Cava)
    Write-Step "Installing Visual C++ 2012 (VC++ 11.0) Update 4..."
    $vcRedistUrl = "https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe"
    $vcInstaller = "$env:TEMP\vcredist_x64.exe"
    Write-Host "   Downloading installer..."
    try {
        Invoke-WebRequest -Uri $vcRedistUrl -OutFile $vcInstaller -UseBasicParsing -ErrorAction Stop
        Write-Host "   Running installer (silent)..."
        Start-Process -FilePath $vcInstaller -ArgumentList "/quiet /norestart" -Wait -NoNewWindow
        Remove-Item $vcInstaller -Force -ErrorAction SilentlyContinue
        Write-Success "Visual C++ 2012 installed."
    } catch {
        Write-Error "Failed to download/install Visual C++ 2012. Please install manually: https://www.microsoft.com/en-us/download/details.aspx?id=30679"
    }

    # 6. Start Komorebi (daemon)
    Write-Step "Starting Komorebi..."
    komorebic start --whkd
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Komorebi started."
    } else {
        Write-Warning "Could not start Komorebi. A reboot may be required."
    }

    # 7. Enable autostart for Komorebi
    Write-Step "Enabling autostart for Komorebi..."
    komorebic enable-autostart --whkd
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Komorebi autostart enabled."
    } else {
        Write-Warning "Could not enable Komorebi autostart."
    }

} else {
    Write-Warning "Software installation skipped (-SkipSoftwareInstall)."
}

# ---- Copy config files ----
Write-Step "Copying configuration files..."

$REPO_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$YASB_CONFIG_DIR = "$env:USERPROFILE\.config\yasb"
$WHKD_CONFIG_DIR = "$env:USERPROFILE\.config\whkd"

# Create folders
$dirs = @($YASB_CONFIG_DIR, $WHKD_CONFIG_DIR)
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   Created: $dir"
    }
}

# File mapping
$FILE_MAP = @{
    "sys_accent.py" = "$YASB_CONFIG_DIR\sys_accent.py"
    "styles.css" = "$YASB_CONFIG_DIR\styles.css"
    "config.yaml" = "$YASB_CONFIG_DIR\config.yaml"
    "komorebi.json" = "$env:USERPROFILE\komorebi.json"
    "applications.json" = "$env:USERPROFILE\applications.json"
    "whkdrc" = "$WHKD_CONFIG_DIR\whkdrc"
}

foreach ($src in $FILE_MAP.Keys) {
    $srcPath = Join-Path $REPO_ROOT $src
    $dstPath = $FILE_MAP[$src]
    if (Test-Path $srcPath) {
        if (Test-Path $dstPath) {
            $backup = $dstPath + ".bak"
            Copy-Item -Path $dstPath -Destination $backup -Force
            Write-Host "   Backup: $backup"
        }
        Copy-Item -Path $srcPath -Destination $dstPath -Force
        Write-Host "   Copied: $src -> $dstPath"
    } else {
        Write-Warning "   File not found: $src (skipping)"
    }
}
Write-Success "Config files copied."

# ---- Install Python and dependencies ----
Write-Step "Checking Python..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Step "Python not found. Installing via winget..."
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install Python. Please install manually from python.org"
        exit 1
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Error "Python not found after installation. Please restart PowerShell."
        exit 1
    }
    Write-Success "Python installed."
} else {
    Write-Success "Python already installed."
}

Write-Step "Installing Python dependencies (pyyaml)..."
try {
    & python -m pip install --upgrade pip --quiet
    & python -m pip install pyyaml --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "pyyaml installed."
    } else {
        Write-Error "Failed to install pyyaml."
    }
} catch {
    Write-Error "Error installing pyyaml: $_"
}

# ---- Autostart for Python script ----
Write-Step "Setting up autostart for YASB Accent Sync..."
$TASK_NAME = "YASB-Accent-Sync"
$SCRIPT_PATH = "$YASB_CONFIG_DIR\sys_accent.py"
$PYTHON_EXE = (Get-Command python).Source

if (-not (Test-Path $SCRIPT_PATH)) {
    Write-Error "File $SCRIPT_PATH not found. Autostart not configured."
} else {
    schtasks /query /tn $TASK_NAME 2>$null
    if ($?) {
        schtasks /delete /tn $TASK_NAME /f | Out-Null
        Write-Host "   Removed old task."
    }
    $action = New-ScheduledTaskAction -Execute $PYTHON_EXE -Argument "`"$SCRIPT_PATH`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
    try {
        Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
        Write-Success "Task '$TASK_NAME' created."
    } catch {
        Write-Error "Failed to create task: $_"
        Write-Warning "You can manually add a shortcut to shell:startup."
    }
}

# ---- Done ----
Write-Success "Installation complete!"
Write-Host ""
Write-Host "Summary:"
Write-Host "  - Installed: Komorebi, whkd, YASB, Cava, Visual C++ 2012"
Write-Host "  - Config files copied to appropriate folders"
Write-Host "  - Python and pyyaml installed"
Write-Host "  - Autostart configured"
Write-Host ""
Write-Host "After reboot, everything should work automatically."
Write-Host "If something went wrong, check logs and install missing components manually."