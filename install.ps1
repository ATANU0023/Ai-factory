# AI Software Factory - Global Installer
# Run via: irm https://raw.githubusercontent.com/ATANU0023/Ai-factory/main/install.ps1 | iex

$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '   AI Software Factory Installer' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

# 1. Check Python
Write-Host 'Checking for Python...' -NoNewline
try {
    $null = Get-Command 'python' -ErrorAction Stop
    $pyVer = (python --version 2>&1)
    Write-Host (' OK ({0})' -f $pyVer) -ForegroundColor Green
} catch {
    Write-Host ' FAILED' -ForegroundColor Red
    Write-Host 'ERROR: Python 3.11+ is required but was not found!' -ForegroundColor Red
    Write-Host 'Please install from https://www.python.org/downloads/' -ForegroundColor Yellow
    exit 1
}

# 2. Check for pipx
Write-Host 'Checking for pipx (Python execution wrapper)...' -NoNewline
try {
    $null = Get-Command 'pipx' -ErrorAction Stop
    Write-Host ' OK' -ForegroundColor Green
} catch {
    Write-Host ' Installing...' -ForegroundColor Yellow
    python -m pip install --user pipx | Out-Null
    python -m pipx ensurepath | Out-Null
    Write-Host '[SUCCESS] Installed pipx.' -ForegroundColor Green
    
    # Python --user installs to AppData\Roaming\Python\PythonXXX\Scripts
    $appData = [Environment]::GetFolderPath('ApplicationData')
    $newPath = $appData + '\Python\Python313\Scripts'
    $env:PATH = $newPath + ';' + $env:PATH
}

# 3. Install AI Software Factory
Write-Host 'Choose your Engine Package:' -ForegroundColor Cyan
Write-Host '  A) Standard  - Base engine only (Fastest install)'
Write-Host '  B) Local AI  - Includes built-in AI models for 100% offline use (Recommended)'
$choice = Read-Host 'Selection (A/B)'

$installPkg = "ai-software-factory"
if ($choice -match '^[bB]') {
    $installPkg = "ai-software-factory[local]"
}

Write-Host "Installing $installPkg from PyPI..." -ForegroundColor Cyan
# Run via python -m pipx to completely bypass path mapping issues
python -m pipx install "$installPkg" --force

# 4. Configure Application Mode
Write-Host ''
Write-Host '4. Configuration' -ForegroundColor Cyan
Write-Host 'The AI Software Factory can run in TWO modes:' -ForegroundColor White
Write-Host '  1. 🟢 Local Mode  - Completely FREE, private, no key needed.' -ForegroundColor Green
Write-Host '  2. 🔵 Cloud Mode  - Premium quality using OpenRouter API key.' -ForegroundColor Blue
Write-Host ''
$wantKey = Read-Host 'Would you like to set up a Cloud API key now? If no, we will default to Local Mode (Y/N)'
if ($wantKey -match '^[yY]') {
    $apiKey = Read-Host 'Paste your OpenRouter API key here'
    if (-not [string]::IsNullOrWhiteSpace($apiKey)) {
        # Save to Windows User Variables (for future terminal sessions)
        [Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', $apiKey.Trim(), 'User')
        # Also inject into current session memory
        $env:OPENROUTER_API_KEY = $apiKey.Trim()
        # Write to ~/.ai-factory-env so the app always finds it (primary read source)
        $envFilePath = Join-Path $HOME '.ai-factory-env'
        $envLine = 'OPENROUTER_API_KEY=' + $apiKey.Trim()
        
        # Ensure directory exists for the config file
        if (-not (Test-Path $envFilePath)) {
            New-Item -Path $envFilePath -ItemType File -Force | Out-Null
        }
        Set-Content $envFilePath $envLine -Encoding UTF8
        Write-Host '[SUCCESS] API Key saved permanently!' -ForegroundColor Green
    }
} else {
    Write-Host 'Running in Local Mode. You can add a key later via "ai-factory auth".' -ForegroundColor Yellow
}

# 5. Final Instructions
Write-Host ''
Write-Host '========================================' -ForegroundColor Green
Write-Host '   Installation Complete!' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''

Write-Host 'To start the factory, open a FRESH terminal to load your variables and run:' -ForegroundColor White
Write-Host '  ai-factory' -ForegroundColor Cyan
Write-Host ''

if ($wantKey -notmatch '^[yY]') {
    Write-Host 'Since you didn`t set an API key, remember to run this before starting:' -ForegroundColor Gray
    Write-Host '  $env:OPENROUTER_API_KEY="sk-or-v1-..."' -ForegroundColor Gray
    Write-Host ''
}
