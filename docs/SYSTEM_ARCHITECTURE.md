# System Architecture Document
## AHON FloodWatch with SMS Messaging and Web-Based Monitoring System

### 1. Overview

AHON FloodWatch is a cloud-based IoT monitoring and early warning system designed for Barangay Tonsuya, Malabon. The system continuously monitors water levels, predicts flood risks using AI, and provides real-time monitoring through a web dashboard with SMS alert capabilities.

### 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Hardware Layer                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │ Water Level  │───▶│  Arduino Uno │───▶│   SIM800L    │              │
│  │   Sensor     │    │   (C++)      │    │  GSM/GPRS    │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│                                              │                          │
│                                              ├─────────┐                │
│                                              │         │                │
│                                              ▼         ▼                │
│                                        Firebase     SMS Alerts          │
│                                        Database    (Residents)          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Backend Layer                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Django REST Framework                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Auth API   │  │   Data API   │  │   Admin API  │          │  │
│  │  │   (JWT)      │  │  (CRUD)      │  │   (RBAC)     │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    AI Prediction Module                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Data       │  │   Model      │  │ Prediction   │          │  │
│  │  │ Processing   │  │  Training    │  │   Engine     │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL Database                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      React Web Dashboard                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │  Dashboard   │  │   Water      │  │   Resident   │          │  │
│  │  │     View     │  │  Monitoring  │  │  Management  │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │   Reports    │  │  Analytics   │  │   Settings   │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3. Component Architecture

#### 3.1 Hardware Layer

**Arduino Uno Microcontroller**
- Reads water level sensor data
- Processes sensor readings
- Determines flood category (Normal, Alert, Warning, Danger)
- Communicates with SIM800L via serial
- Manages power and error recovery

**Water Level Sensor**
- Analog ultrasonic or pressure sensor
- Measures water depth in cm
- Provides continuous readings
- Range: 0-100cm (configurable)

**SIM800L GSM/GPRS Module**
- Establishes GPRS connection
- Uploads data to Firebase via HTTP
- Sends SMS alerts to residents
- Manages connection retries
- Handles communication errors

**Power System**
- Solar panel (10W-20W)
- Rechargeable power bank/battery (10000mAh-20000mAh)
- Voltage regulator for Arduino
- Automatic power management

#### 3.2 Cloud Layer

**Firebase Realtime Database**
- Stores real-time water level readings
- Stores alert status
- Provides real-time sync to backend
- JSON structure for easy access

#### 3.3 Backend Layer

**Django REST Framework**
- RESTful API endpoints
- JWT authentication
- Role-based access control
- Request validation
- Error handling

**AI Prediction Module**
- Data preprocessing
- Model training (Random Forest/Decision Tree)
- Flood risk prediction
- Confidence scoring
- Model versioning

**PostgreSQL Database**
- Persistent data storage
- Historical records
- User management
- Audit logs
- Data relationships

#### 3.4 Frontend Layer

**React Web Application**
- Real-time dashboard
- Data visualization (Charts)
- User authentication
- Role-based UI
- Responsive design
- Material UI components

### 4. Data Flow Architecture

```
1. Sensor Data Collection:
   Water Level Sensor → Arduino Uno (Analog Read)

2. Data Processing:
   Arduino Uno → Process Reading → Determine Category

3. Cloud Upload:
   Arduino Uno → SIM800L (GPRS) → Firebase Realtime Database

4. SMS Alert (if needed):
   Arduino Uno → SIM800L (GSM) → Resident Mobile Numbers

5. Backend Sync:
   Firebase → Django (Firebase Admin SDK) → PostgreSQL

6. AI Prediction:
   PostgreSQL → AI Module → Flood Prediction → PostgreSQL

7. Frontend Display:
   Django API → React Dashboard → Real-time Updates
```

### 5. Technology Stack Details

#### 5.1 Hardware
- **Microcontroller**: Arduino Uno (ATmega328P)
- **Sensor**: Ultrasonic Sensor HC-SR04 or Water Level Sensor
- **Communication**: SIM800L GSM/GPRS Module
- **Power**: Solar Panel + Rechargeable Battery
- **Programming Language**: Arduino C++

#### 5.2 Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework 3.14+
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 15+
- **Firebase**: Firebase Admin SDK (Python)
- **AI/ML**: Scikit-learn, Pandas, NumPy
- **Python Version**: 3.11+

#### 5.3 Frontend
- **Framework**: React 18+
- **Build Tool**: Vite
- **UI Library**: Material UI (MUI) 5+
- **Routing**: React Router 6+
- **HTTP Client**: Axios
- **Charts**: Recharts or Chart.js
- **Real-time**: Firebase JavaScript SDK

#### 5.4 Cloud & Database
- **Real-time Database**: Firebase Realtime Database
- **Relational Database**: PostgreSQL
- **Hosting**: Any cloud provider (AWS, GCP, Azure)

### 6. Security Architecture

#### 6.1 Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing (bcrypt)
- Session management
- Token expiration and refresh

#### 6.2 Data Security
- Input validation and sanitization
- SQL injection prevention (ORM)
- XSS protection
- CSRF protection
- Environment variables for secrets
- Encrypted database connections (SSL/TLS)

#### 6.3 API Security
- Rate limiting
- Request throttling
- API key management
- CORS configuration
- Secure headers

#### 6.4 Audit & Logging
- Activity logs
- Access logs
- Error logs
- SMS delivery logs
- System event logs

### 7. Scalability Architecture

#### 7.1 Horizontal Scaling
- Django can be deployed with multiple workers
- PostgreSQL supports read replicas
- Firebase handles concurrent connections
- React is stateless and scalable

#### 7.2 Vertical Scaling
- Database indexing optimization
- Caching layer (Redis)
- CDN for static assets
- Database connection pooling

### 8. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Production Server                     │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Nginx      │  │   Gunicorn   │  │   Django     │ │
│  │  (Reverse    │  │  (WSGI       │  │   App        │ │
│  │   Proxy)     │  │   Server)    │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                              │                       │
│                              ▼                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ PostgreSQL   │  │   Redis      │  │   Firebase   │ │
│  │  Database    │  │   Cache      │  │   (Cloud)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    React Build                           │
│              (Served via Nginx/CDN)                     │
└─────────────────────────────────────────────────────────┘
```

### 9. System Interfaces

#### 9.1 External Interfaces
- **Firebase Realtime Database**: Real-time data sync
- **SIM800L**: GSM/GPRS communication
- **SMS Gateway**: Direct SIM800L SMS sending

#### 9.2 Internal Interfaces
- **REST API**: Django ↔ React
- **Database ORM**: Django ↔ PostgreSQL
- **Firebase SDK**: Django ↔ Firebase

### 10. Performance Requirements

- **Sensor Reading Interval**: Every 30 seconds (configurable)
- **Firebase Upload**: Every 30 seconds
- **Backend Sync**: Every 1 minute
- **API Response Time**: < 200ms
- **Dashboard Update**: Real-time (< 1 second)
- **SMS Delivery**: < 10 seconds
- **AI Prediction**: < 5 seconds

### 11. Reliability & Availability

- **System Uptime**: 99.5%
- **Data Backup**: Daily automated backups
- **Error Recovery**: Automatic retry mechanisms
- **Power Backup**: Solar + Battery (24+ hours)
- **Failover**: Graceful degradation

### 12. Monitoring & Maintenance

- **System Health Monitoring**
- **Database Performance Monitoring**
- **API Response Time Tracking**
- **Error Rate Monitoring**
- **SMS Delivery Tracking**
- **Hardware Status Monitoring**

### 13. Development Standards

- **Clean Architecture**: Separation of concerns
- **MVC Pattern**: Model-View-Controller
- **RESTful Design**: Standard HTTP methods
- **Code Quality**: PEP 8 (Python), Modern C++ (Arduino)
- **Version Control**: Git with meaningful commits
- **Testing**: Unit, Integration, E2E tests
- **Documentation**: Comprehensive technical docs
