# React Frontend Deployment Script for Windows
# Run this script to deploy the React frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "React Frontend Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js installation
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js not found. Please install Node.js 16 or later." -ForegroundColor Red
    exit 1
}

# Check npm installation
Write-Host "Checking npm installation..." -ForegroundColor Yellow
$npmVersion = npm --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "npm found: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "npm not found." -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Write-Host "Navigating to frontend directory..." -ForegroundColor Yellow
Set-Location frontend\React

# Install dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your configuration." -ForegroundColor Cyan
    Write-Host "Press Enter to continue after editing .env file..."
    Read-Host
}

# Build for production
Write-Host "Building React application for production..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully." -ForegroundColor Green
    Write-Host "Built files are in the 'dist' directory." -ForegroundColor Cyan
} else {
    Write-Host "Build failed." -ForegroundColor Red
    exit 1
}

# Ask if user wants to start development server
Write-Host "Do you want to start the development server? (y/n)" -ForegroundColor Yellow
$startDevServer = Read-Host
if ($startDevServer -eq 'y' -or $startDevServer -eq 'Y') {
    Write-Host "Starting development server..." -ForegroundColor Green
    Write-Host "Server will be available at http://localhost:5173" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Cyan
    Write-Host ""
    npm run dev
} else {
    Write-Host "Deployment completed. You can serve the 'dist' directory with a web server." -ForegroundColor Green
}
