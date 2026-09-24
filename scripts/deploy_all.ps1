# Complete System Deployment Script for Windows
# This script deploys all components of the flood detection system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete System Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will deploy:" -ForegroundColor Yellow
Write-Host "1. Django Backend" -ForegroundColor White
Write-Host "2. React Frontend" -ForegroundColor White
Write-Host "3. AI Prediction Model" -ForegroundColor White
Write-Host "4. Docker Services (if Docker is available)" -ForegroundColor White
Write-Host ""

Write-Host "Do you want to continue? (y/n)" -ForegroundColor Yellow
$continue = Read-Host
if ($continue -ne 'y' -and $continue -ne 'Y') {
    Write-Host "Deployment cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Django Backend Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& "$PSScriptRoot\deploy_backend.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend deployment failed. Stopping deployment." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: React Frontend Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& "$PSScriptRoot\deploy_frontend.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend deployment failed. Stopping deployment." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: AI Model Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& "$PSScriptRoot\deploy_ai_model.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "AI model deployment failed. Stopping deployment." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 4: Docker Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerAvailable = $true
        Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "Docker not found. Skipping Docker deployment." -ForegroundColor Yellow
}

if ($dockerAvailable) {
    Write-Host "Do you want to deploy using Docker? (y/n)" -ForegroundColor Yellow
    $useDocker = Read-Host
    if ($useDocker -eq 'y' -or $useDocker -eq 'Y') {
        & .\deploy_docker.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Docker deployment failed." -ForegroundColor Red
        }
    }
} else {
    Write-Host "Docker deployment skipped." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure Firebase credentials in .env files" -ForegroundColor White
Write-Host "2. Set up PostgreSQL database" -ForegroundColor White
Write-Host "3. Configure SMS gateway (if using SMS)" -ForegroundColor White
Write-Host "4. Upload Arduino firmware to hardware" -ForegroundColor White
Write-Host "5. Access the application at http://localhost" -ForegroundColor White
Write-Host ""

Write-Host "For detailed instructions, see:" -ForegroundColor Cyan
Write-Host "- docs/QUICK_START_GUIDE.md" -ForegroundColor White
Write-Host "- docs/DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "- docs/HARDWARE_SETUP.md" -ForegroundColor White
Write-Host ""
