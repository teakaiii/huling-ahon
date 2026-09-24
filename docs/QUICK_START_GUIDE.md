# Quick Start Guide

This guide provides step-by-step instructions to get AHON FloodWatch up and running quickly.

## Prerequisites

- **Python 3.9+** - For backend development
- **Node.js 16+** - For frontend development
- **PostgreSQL 13+** - For database (or use Docker)
- **Docker & Docker Compose** - For containerized deployment (optional)
- **Git** - For cloning the repository

## Quick Deployment Options

### Option 1: Docker Deployment (Recommended)

This is the fastest way to deploy the entire system using Docker containers.

#### Steps:

1. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ai-flood-detection-system
   ```

3. **Configure Environment**
   ```bash
   cd docker
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run Deployment Script**
   ```powershell
   # On Windows
   .\scripts\deploy_docker.ps1
   
   # On Linux/Mac
   bash scripts/deploy_docker.sh
   ```

5. **Access the Application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000/api
   - API Documentation: http://localhost:8000/swagger/

### Option 2: Local Development Setup

For development without Docker, set up each component separately.

#### Backend Setup:

1. **Navigate to Backend Directory**
   ```bash
   cd backend/Django
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup:

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend/React
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   ```

5. **Access Frontend**
   - Open http://localhost:5173 in your browser

### Option 3: Production Deployment

For production deployment, follow the detailed Deployment Guide in `docs/DEPLOYMENT_GUIDE.md`.

## Configuration

### Required Configuration Items

#### Backend (.env)
```ini
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database
DB_NAME=flood_detection
DB_USER=flood_detection_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_PATH=/path/to/service-account-key.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
```

#### Frontend (.env)
```ini
VITE_API_URL=http://localhost:8000/api
```

### Firebase Setup

1. **Create Firebase Project**
   - Go to https://console.firebase.google.com
   - Create new project
   - Enable Realtime Database

2. **Generate Service Account Key**
   - Project Settings → Service Accounts
   - Generate Private Key
   - Save as `service-account-key.json`

3. **Update Configuration**
   - Add Firebase credentials to .env file
   - Update firmware with Firebase credentials

## Hardware Setup

### Arduino Deployment

1. **Install Arduino IDE**
   - Download from https://www.arduino.cc/en/software

2. **Open Firmware**
   - Open `hardware/Arduino/flood_detection.ino`

3. **Configure Settings**
   - Update pin definitions
   - Set flood thresholds
   - Add Firebase credentials
   - Configure SMS settings

4. **Upload to Arduino**
   - Connect Arduino via USB
   - Select board and port
   - Upload firmware

5. **Install Hardware**
   - Follow Hardware Setup Guide in `docs/HARDWARE_SETUP.md`
   - Connect water level sensor
   - Connect SIM800L module
   - Install power system

## Testing

### Backend Tests
```bash
cd backend/Django
python manage.py test
```

### Frontend Tests
```bash
cd frontend/React
npm test
```

### AI Model Test
```bash
cd backend/ai
python flood_prediction.py
```

## Troubleshooting

### Common Issues

#### Django Server Won't Start
- Check if port 8000 is available
- Verify database connection in .env
- Check Python dependencies are installed

#### Frontend Won't Build
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (16+ required)
- Verify .env file exists

#### Docker Issues
- Ensure Docker Desktop is running
- Check Docker has sufficient resources
- Verify ports are not in use

#### Database Connection Failed
- Verify PostgreSQL is running
- Check database credentials in .env
- Ensure database exists

## Next Steps

After successful deployment:

1. **Create Admin User**
   - Access Django admin at http://localhost:8000/admin
   - Create admin account

2. **Add Residents**
   - Use the Residents page to add residents
   - Enable SMS notifications for residents

3. **Configure Thresholds**
   - Set flood thresholds in Settings
   - Adjust based on local conditions

4. **Test SMS Alerts**
   - Send test SMS to verify functionality
   - Check SMS logs for delivery status

5. **Monitor Dashboard**
   - Monitor water levels in real-time
   - Review alerts and predictions
   - Generate reports as needed

## Support

For detailed information:
- **API Documentation**: `docs/API_DOCUMENTATION.md`
- **User Manual**: `docs/USER_MANUAL.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
- **Hardware Setup**: `docs/HARDWARE_SETUP.md`
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md`
- **Security Guide**: `docs/SECURITY_GUIDE.md`

## Deployment Scripts

Automated deployment scripts are available in the `scripts/` directory:

- `deploy_backend.ps1` - Django backend deployment
- `deploy_frontend.ps1` - React frontend deployment
- `deploy_ai_model.ps1` - AI model training
- `deploy_docker.ps1` - Docker deployment

Run these scripts to automate the deployment process.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 50 GB
- **Network**: Stable internet connection

### Recommended Requirements
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 100 GB
- **Network**: High-speed internet with static IP

## Security Notes

- **Change default passwords** immediately
- **Use strong SECRET_KEY** in production
- **Enable HTTPS** in production
- **Configure firewall** rules
- **Regular updates** of dependencies
- **Backup database** regularly

## License

This project is for educational and community use. Please refer to the LICENSE file for specific terms.

## Version

Current Version: 1.0.0
Release Date: July 13, 2026
