# Quick Setup Script (No Docker Required)
# Run this to get started quickly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Software Factory - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pythonVersion`n" -ForegroundColor Green

# Step 2: Install dependencies
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed`n" -ForegroundColor Green

# Step 3: Setup .env file
Write-Host "[3/4] Setting up environment..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Copy-Item ".env.template" ".env"
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host "`nIMPORTANT: Edit .env and add your API keys:" -ForegroundColor Yellow
    Write-Host "  1. OPENROUTER_API_KEY (from https://openrouter.ai/keys)" -ForegroundColor White
    Write-Host "  2. QDRANT credentials OR use ChromaDB (see ALTERNATIVE_SETUP.md)`n" -ForegroundColor White
} else {
    Write-Host "✓ .env file already exists`n" -ForegroundColor Green
}

# Step 4: Create output directory
Write-Host "[4/4] Creating output directory..." -ForegroundColor Yellow
if (-Not (Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
}
Write-Host "✓ Output directory ready`n" -ForegroundColor Green

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your API keys" -ForegroundColor White
Write-Host "2. Choose vector database (see ALTERNATIVE_SETUP.md):" -ForegroundColor White
Write-Host "   - Option A: Qdrant Cloud (recommended, no Docker)" -ForegroundColor White
Write-Host "   - Option B: ChromaDB (lightweight, local)" -ForegroundColor White
Write-Host "3. Run the factory:`n" -ForegroundColor White
Write-Host "   Interactive mode:" -ForegroundColor Cyan
Write-Host "   python ai_factory.py`n" -ForegroundColor White
Write-Host "   One-shot command:" -ForegroundColor Cyan
Write-Host "   python ai_factory.py `"Build a calculator`"`n" -ForegroundColor White

Write-Host "For detailed instructions, see:" -ForegroundColor Yellow
Write-Host "  - QUICKSTART.md" -ForegroundColor White
Write-Host "  - ALTERNATIVE_SETUP.md`n" -ForegroundColor White
