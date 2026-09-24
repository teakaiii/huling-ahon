# PostgreSQL Connection Test Script for AI Flood Detection System
# This script tests the connection to PostgreSQL database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Connection Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "Checking PostgreSQL installation..." -ForegroundColor Yellow
try {
    $psqlVersion = psql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL is installed: $psqlVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ PostgreSQL is not installed or not in PATH" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install PostgreSQL from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ PostgreSQL is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install PostgreSQL from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if PostgreSQL service is running
Write-Host "Checking PostgreSQL service..." -ForegroundColor Yellow
$serviceName = "postgresql-x64-*"
$services = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if ($services) {
    foreach ($service in $services) {
        if ($service.Status -eq 'Running') {
            Write-Host "✓ PostgreSQL service is running: $($service.Name)" -ForegroundColor Green
        } else {
            Write-Host "✗ PostgreSQL service is not running: $($service.Name)" -ForegroundColor Red
            Write-Host "  Starting service..." -ForegroundColor Yellow
            Start-Service -Name $service.Name
            Start-Sleep -Seconds 3
            if ((Get-Service -Name $service.Name).Status -eq 'Running') {
                Write-Host "✓ PostgreSQL service started successfully" -ForegroundColor Green
            } else {
                Write-Host "✗ Failed to start PostgreSQL service" -ForegroundColor Red
                exit 1
            }
        }
    }
} else {
    Write-Host "✗ PostgreSQL service not found" -ForegroundColor Red
    Write-Host "  Please ensure PostgreSQL is installed correctly" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test database connection using Django
Write-Host "Testing Django database connection..." -ForegroundColor Yellow
$backendDir = "backend\Django"
if (Test-Path $backendDir) {
    Set-Location $backendDir
    
    # Activate virtual environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
        
        # Test connection
        Write-Host "Running Django connection test..." -ForegroundColor Yellow
        python manage.py dbshell -c "\q" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Django can connect to PostgreSQL successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Django cannot connect to PostgreSQL" -ForegroundColor Red
            Write-Host ""
            Write-Host "Please check your .env file configuration:" -ForegroundColor Yellow
            Write-Host "  - DB_NAME" -ForegroundColor Yellow
            Write-Host "  - DB_USER" -ForegroundColor Yellow
            Write-Host "  - DB_PASSWORD" -ForegroundColor Yellow
            Write-Host "  - DB_HOST" -ForegroundColor Yellow
            Write-Host "  - DB_PORT" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "✗ Virtual environment not found" -ForegroundColor Red
        Write-Host "  Please run: python -m venv venv" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✗ Backend directory not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ All PostgreSQL checks passed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run Django migrations:" -ForegroundColor Yellow
Write-Host "  python manage.py migrate" -ForegroundColor Yellow
Write-Host ""
