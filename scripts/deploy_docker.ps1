# Docker Deployment Script for Windows
# Run this script to deploy using Docker and Docker Compose

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker installation
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "Docker not found. Please install Docker Desktop for Windows." -ForegroundColor Red
    Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# Check Docker Compose
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
$dockerComposeVersion = docker-compose --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker Compose found: $dockerComposeVersion" -ForegroundColor Green
} else {
    Write-Host "Docker Compose not found." -ForegroundColor Red
    exit 1
}

# Navigate to docker directory
Write-Host "Navigating to docker directory..." -ForegroundColor Yellow
Set-Location docker

# Create .env file if it doesn't exist
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your configuration." -ForegroundColor Cyan
    Write-Host "Press Enter to continue after editing .env file..."
    Read-Host
}

# Build and start services
Write-Host "Building and starting Docker services..." -ForegroundColor Yellow
docker-compose up -d --build
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker services started successfully." -ForegroundColor Green
} else {
    Write-Host "Failed to start Docker services." -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
docker-compose exec backend python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations completed successfully." -ForegroundColor Green
} else {
    Write-Host "Migration failed. Please check your database configuration." -ForegroundColor Red
}

# Create superuser (optional)
Write-Host "Do you want to create a superuser? (y/n)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -eq 'y' -or $createSuperuser -eq 'Y') {
    docker-compose exec backend python manage.py createsuperuser
}

# Display service status
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor Cyan
docker-compose ps
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "- Frontend: http://localhost" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000/api" -ForegroundColor White
Write-Host "- API Documentation: http://localhost:8000/swagger/" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "- View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "- Stop services: docker-compose down" -ForegroundColor White
Write-Host "- Restart services: docker-compose restart" -ForegroundColor White
