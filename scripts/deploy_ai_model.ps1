# AI Model Training and Deployment Script for Windows
# Run this script to train and deploy the AI flood prediction model

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Model Training and Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python not found. Please install Python 3.9 or later." -ForegroundColor Red
    exit 1
}

# Navigate to AI directory
Write-Host "Navigating to AI directory..." -ForegroundColor Yellow
Set-Location backend\ai

# Create models directory if it doesn't exist
Write-Host "Creating models directory..." -ForegroundColor Yellow
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path models -Force
    Write-Host "Models directory created." -ForegroundColor Green
}

# Install AI dependencies
Write-Host "Installing AI dependencies..." -ForegroundColor Yellow
pip install pandas numpy scikit-learn joblib
if ($LASTEXITCODE -eq 0) {
    Write-Host "AI dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "Failed to install AI dependencies." -ForegroundColor Red
    exit 1
}

# Run the training script
Write-Host "Training AI flood prediction model..." -ForegroundColor Yellow
python flood_prediction.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Model training completed successfully." -ForegroundColor Green
    Write-Host "Model saved to backend/ai/models/flood_prediction_model.pkl" -ForegroundColor Cyan
} else {
    Write-Host "Model training failed." -ForegroundColor Red
    exit 1
}

# Test the model
Write-Host "Testing the trained model..." -ForegroundColor Yellow
Write-Host "Running sample predictions..." -ForegroundColor Cyan

$testScript = @"
from flood_prediction import FloodPredictionModel

# Load the trained model
predictor = FloodPredictionModel()
predictor.load_model('models/flood_prediction_model.pkl')

# Test predictions
print('\n=== Sample Predictions ===')
for level in [20, 40, 55, 70, 85]:
    result = predictor.predict(water_level=level)
    print(f'Water Level: {level}cm -> {result[\"predicted_status\"]} ({result[\"confidence_score\"]:.1f}% confidence)')
"@

python -c $testScript

Write-Host ""
Write-Host "AI model deployment completed successfully!" -ForegroundColor Green
Write-Host "The model is ready for integration with the Django backend." -ForegroundColor Cyan
