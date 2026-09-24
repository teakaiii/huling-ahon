# Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Hardware Development](#hardware-development)
6. [AI Model Development](#ai-model-development)
7. [Testing](#testing)
8. [Code Standards](#code-standards)
9. [Git Workflow](#git-workflow)
10. [Contributing](#contributing)

## About AHON FloodWatch

This guide is for developers working on AHON FloodWatch, a comprehensive flood detection and monitoring system for Barangay Tonsuya, Malabon.

## Development Environment Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Arduino IDE (for hardware development)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-flood-detection-system
   ```

2. **Create virtual environment**
   ```bash
   cd backend/Django
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend/React
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

### Database Setup

1. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE flood_detection;
   ```

2. **Update .env file**
   ```
   DB_NAME=flood_detection
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

## Project Structure

```
ai-flood-detection-system/
├── backend/
│   ├── Django/
│   │   ├── apps/
│   │   │   ├── authentication/
│   │   │   ├── activity_logs/
│   │   │   ├── water_level/
│   │   │   ├── residents/
│   │   │   ├── alerts/
│   │   │   ├── sms/
│   │   │   ├── predictions/
│   │   │   ├── reports/
│   │   │   ├── notifications/
│   │   │   ├── settings/
│   │   │   └── dashboard/
│   │   ├── flood_detection/
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   └── .env.example
│   ├── api/
│   │   ├── firebase_service.py
│   │   └── sms_service.py
│   └── ai/
│       └── flood_prediction.py
├── frontend/
│   └── React/
│       ├── src/
│       │   ├── components/
│       │   ├── contexts/
│       │   ├── pages/
│       │   ├── services/
│       │   ├── App.jsx
│       │   └── main.jsx
│       ├── package.json
│       └── vite.config.js
├── hardware/
│   ├── Arduino/
│   │   └── flood_detection.ino
│   └── SIM800L/
├── database/
│   └── DATABASE_SCHEMA.md
├── docs/
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── API_DOCUMENTATION.md
│   ├── USER_MANUAL.md
│   └── DEVELOPER_GUIDE.md
└── docker/
    └── docker-compose.yml
```

## Backend Development

### Django Apps

The backend is organized into modular Django apps:

- **authentication**: User management and authentication
- **activity_logs**: System activity logging
- **water_level**: Water level readings and monitoring
- **residents**: Resident management
- **alerts**: Flood alert management
- **sms**: SMS logging and tracking
- **predictions**: AI predictions and model management
- **reports**: Report generation
- **notifications**: User notifications
- **settings**: System configuration
- **dashboard**: Dashboard data aggregation

### Creating a New Django App

1. **Create the app**
   ```bash
   python manage.py startapp new_app
   ```

2. **Move to apps directory**
   ```bash
   mv new_app apps/
   ```

3. **Add to INSTALLED_APPS in settings.py**
   ```python
   INSTALLED_APPS = [
       ...
       'apps.new_app',
   ]
   ```

4. **Create models, serializers, views, and URLs**
   ```python
   # models.py
   from django.db import models
   
   class NewModel(models.Model):
       name = models.CharField(max_length=100)
       created_at = models.DateTimeField(auto_now_add=True)
   
   # serializers.py
   from rest_framework import serializers
   
   class NewModelSerializer(serializers.ModelSerializer):
       class Meta:
           model = NewModel
           fields = '__all__'
   
   # views.py
   from rest_framework import viewsets
   
   class NewModelViewSet(viewsets.ModelViewSet):
       queryset = NewModel.objects.all()
       serializer_class = NewModelSerializer
   
   # urls.py
   from django.urls import path, include
   from .views import NewModelViewSet
   
   router = DefaultRouter()
   router.register(r'new-models', NewModelViewSet)
   
   urlpatterns = [
       path('', include(router.urls)),
   ]
   ```

5. **Add URLs to main urls.py**
   ```python
   path('api/new-app/', include('apps.new_app.urls')),
   ```

6. **Create and run migrations**
   ```bash
   python manage.py makemigrations new_app
   python manage.py migrate
   ```

### API Development Guidelines

- Use Django REST Framework for all API endpoints
- Implement proper authentication and authorization
- Use serializers for data validation
- Include proper error handling
- Add API documentation using drf-yasg
- Implement pagination for list endpoints
- Use filtering and search where appropriate

### Database Models

Follow these conventions for database models:

- Use UUID for primary keys
- Include created_at and updated_at timestamps
- Add helpful __str__ methods
- Use appropriate field types and constraints
- Add indexes for frequently queried fields
- Include helpful Meta classes

### Testing

Run tests using:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test apps.authentication
```

Run with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## Frontend Development

### React Components

The frontend uses React with Material UI components:

- **Functional components** with hooks
- **Context API** for state management
- **Axios** for API calls
- **React Router** for navigation
- **Recharts** for data visualization

### Component Structure

```jsx
import React from 'react'
import { Box, Typography } from '@mui/material'

const MyComponent = ({ prop1, prop2 }) => {
  const [state, setState] = React.useState(null)
  
  const handleAction = () => {
    // Handle action
  }
  
  return (
    <Box>
      <Typography variant="h6">My Component</Typography>
      {/* Component content */}
    </Box>
  )
}

export default MyComponent
```

### API Service

Use the centralized API service for all API calls:

```javascript
import api from '../services/api'

const fetchData = async () => {
  try {
    const response = await api.get('/api/endpoint/')
    return response.data
  } catch (error) {
    console.error('Error:', error)
  }
}
```

### Styling

- Use Material UI components and theming
- Follow the established theme in main.jsx
- Use sx prop for custom styling
- Keep components responsive

### State Management

- Use React Context for global state (authentication)
- Use useState for local component state
- Use useEffect for side effects and data fetching

## Hardware Development

### Arduino Firmware

The Arduino firmware is written in C++:

- Uses SoftwareSerial for SIM800L communication
- Implements water level reading from analog sensor
- Uploads data to Firebase via GPRS
- Sends SMS alerts during emergency conditions
- Includes error handling and retry logic

### Uploading Firmware

1. **Open Arduino IDE**
2. **Load the firmware file**
   ```arduino
   File -> Open -> hardware/Arduino/flood_detection.ino
   ```
3. **Select board**
   ```arduino
   Tools -> Board -> Arduino Uno
   ```
4. **Select port**
   ```arduino
   Tools -> Port -> COMx (Windows) or /dev/ttyUSBx (Linux/Mac)
   ```
5. **Upload**
   ```arduino
   Sketch -> Upload
   ```

### Hardware Configuration

Edit the firmware configuration at the top of the file:

```cpp
// Pin Definitions
#define WATER_LEVEL_SENSOR_PIN A0
#define SIM800L_TX_PIN 7
#define SIM800L_RX_PIN 8

// Flood Thresholds (in cm)
#define NORMAL_THRESHOLD 30
#define ALERT_THRESHOLD 45
#define WARNING_THRESHOLD 60
#define DANGER_THRESHOLD 75

// Firebase Configuration
#define FIREBASE_HOST "your-project-id.firebaseio.com"
#define FIREBASE_AUTH "your-firebase-auth-token"
#define FIREBASE_PATH "/water_level"

// SMS Configuration
#define ADMIN_NUMBER "+639123456789"
```

## AI Model Development

### Flood Prediction Model

The AI module uses scikit-learn for flood prediction:

- **Random Forest Classifier**: Primary model
- **Decision Tree Classifier**: Alternative model
- **Feature Engineering**: Time-based and rolling statistics
- **Model Persistence**: Save/load trained models

### Training the Model

```python
from backend.ai.flood_prediction import FloodPredictionModel

# Create and train model
predictor = FloodPredictionModel(model_type='random_forest')
metrics = predictor.train()

# Save model
predictor.save_model('backend/ai/models/flood_prediction_model.pkl')
```

### Making Predictions

```python
# Load model
predictor = FloodPredictionModel()
predictor.load_model('backend/ai/models/flood_prediction_model.pkl')

# Make prediction
result = predictor.predict(water_level=50.0)
print(result)
```

### Model Features

The model uses the following features:
- Water level (cm)
- Hour of day
- Day of week
- Month
- Rate of change
- Rolling averages (1h, 6h, 24h)
- Rolling max/min (24h)

## Testing

### Backend Testing

Run all tests:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test apps.authentication
```

Run with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Testing

Install testing dependencies:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

Run tests:
```bash
npm test
```

### Integration Testing

Test API endpoints:
```bash
# Test authentication
curl -X POST http://localhost:8000/api/auth/login/ \
  -d "username=admin&password=adminpass123"

# Test protected endpoint
curl -X GET http://localhost:8000/api/water-level/ \
  -H "Authorization: Bearer <token>"
```

## Code Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate
- Handle exceptions properly

### JavaScript (Frontend)

- Use ES6+ features
- Use functional components with hooks
- Follow Airbnb JavaScript Style Guide
- Add JSDoc comments for complex functions
- Use meaningful variable names
- Keep components focused and small

### Git Commit Messages

Follow conventional commit format:

```
feat: add new feature
fix: fix bug
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

Example:
```
feat(authentication): add JWT token refresh
fix(water-level): correct sensor reading calculation
docs(api): update authentication endpoints
```

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Emergency fixes

### Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push to remote**
   ```bash
   git push origin feature/new-feature
   ```

4. **Create pull request**
   - Describe changes
   - Reference related issues
   - Request review

5. **Merge after approval**
   - Merge to develop
   - Delete feature branch

## Contributing

### Before Contributing

1. Read this developer guide
2. Understand the project structure
3. Set up your development environment
4. Run existing tests to ensure they pass

### Making Changes

1. **Create a branch** for your changes
2. **Write tests** for new functionality
3. **Update documentation** as needed
4. **Run tests** to ensure nothing breaks
5. **Submit a pull request** with clear description

### Code Review Process

- All changes must be reviewed before merging
- Reviewers check for:
  - Code quality and style
  - Test coverage
  - Documentation updates
  - Security considerations
  - Performance impact

### Issue Reporting

When reporting issues, include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

## Additional Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Material UI Documentation](https://mui.com/)
- [Arduino Reference](https://www.arduino.cc/reference/en/)
- [Scikit-learn Documentation](https://scikit-learn.org/)

### Tools

- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL management
- [VS Code](https://code.visualstudio.com/) - Code editor
- [Git](https://git-scm.com/) - Version control

### Support

For development support:
- Check existing documentation
- Review code examples
- Contact the development team
- Submit issues on the project repository
