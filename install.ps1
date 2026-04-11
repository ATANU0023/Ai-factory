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
Write-Host 'Installing AI Software Factory from PyPI...' -ForegroundColor Cyan
# Run via python -m pipx to completely bypass path mapping issues
python -m pipx install ai-software-factory --force

# 4. Configure Application Mode
Write-Host ''
Write-Host '4. Configuration' -ForegroundColor Cyan
Write-Host 'The AI Software Factory can run in TWO modes:' -ForegroundColor White
Write-Host '  1. 🟢 Local Mode  - Completely FREE, runs on your CPU, no key needed.' -ForegroundColor Green
Write-Host '  2. 🔵 Cloud Mode  - Fast, premium quality, requires OpenRouter API key.' -ForegroundColor Blue
Write-Host ''
$wantKey = Read-Host 'Would you like to set up a Cloud API key now? If no, we will use Local Mode (Y/N)'
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
        if (Test-Path $envFilePath) {
            $existing = Get-Content $envFilePath -Raw
            if ($existing -match 'OPENROUTER_API_KEY=') {
                $existing = $existing -replace 'OPENROUTER_API_KEY=.*', $envLine
                Set-Content $envFilePath $existing -Encoding UTF8
            } else {
                Add-Content $envFilePath $envLine -Encoding UTF8
            }
        } else {
            Set-Content $envFilePath $envLine -Encoding UTF8
        }
        Write-Host '[SUCCESS] API Key saved permanently!' -ForegroundColor Green
    }
} else {
    Write-Host 'Skipped API key setup. Run "ai-factory auth" later to configure.' -ForegroundColor Yellow
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
