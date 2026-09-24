# Database Schema Design
## AI-Assisted Flood Detection System

### 1. Overview

This document describes the complete PostgreSQL database schema for the AI-Assisted Flood Detection System. The database follows normalization principles (3NF) and includes all necessary tables, relationships, constraints, and indexes.

### 2. Entity-Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Users       │       │  BarangayStaff  │       │   Residents     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ user_id (PK)    │───┐   │ staff_id (PK)   │       │ resident_id (PK)│
│ username        │   │   │ user_id (FK)    │◄──────│ full_name       │
│ email           │   │   │ full_name       │       │ mobile_number   │
│ password_hash   │   │   │ mobile_number   │       │ address         │
│ role            │   │   │ address         │       │ purok_zone      │
│ is_active       │   │   │ purok_zone      │       │ status          │
│ created_at      │   │   │ status          │       │ sms_enabled     │
│ updated_at      │   └───│ created_at      │       │ created_at      │
└─────────────────┘       │ updated_at      │       │ updated_at      │
                          └─────────────────┘       └─────────────────┘
                                   │
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ WaterLevel      │
                          │ Readings        │
                          ├─────────────────┤
                          │ reading_id (PK) │
                          │ water_level_cm  │
                          │ status          │
                          │ timestamp       │
                          │ sensor_status   │
                          │ gsm_status      │
                          └─────────────────┘
                                   │
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   FloodAlerts   │
                          ├─────────────────┤
                          │ alert_id (PK)   │
                          │ reading_id (FK)│
                          │ alert_level     │
                          │ message         │
                          │ timestamp       │
                          └─────────────────┘
                                   │
                                   │
                                   ▼
                          ┌─────────────────┐
                          │     SMSLogs     │
                          ├─────────────────┤
                          │ sms_id (PK)     │
                          │ alert_id (FK)   │
                          │ resident_id (FK)│
                          │ recipient       │
                          │ message         │
                          │ sent_at         │
                          │ delivery_status │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Predictions   │       │    Reports      │       │  Notifications  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ prediction_id   │       │ report_id (PK)  │       │ notif_id (PK)   │
│ (PK)            │       │ report_type     │       │ user_id (FK)    │
│ reading_id (FK) │       │ generated_by    │       │ title           │
│ flood_prob      │       │ start_date      │       │ message         │
│ severity        │       │ end_date        │       │ type            │
│ alert_level     │       │ file_path       │       │ is_read         │
│ confidence      │       │ created_at      │       │ created_at      │
│ timestamp       │       └─────────────────┘       └─────────────────┘
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  ActivityLogs   │       │    Settings     │       │  AIModels       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ log_id (PK)     │       │ setting_id (PK) │       │ model_id (PK)   │
│ user_id (FK)    │       │ key             │       │ model_name      │
│ action          │       │ value           │       │ model_type      │
│ entity          │       │ description     │       │ version         │
│ details         │       │ updated_at      │       │ accuracy        │
│ timestamp       │       │ updated_by      │       │ trained_at      │
└─────────────────┘       └─────────────────┘       │ is_active       │
                                                   └─────────────────┘
```

### 3. Detailed Table Definitions

#### 3.1 Users Table

Stores system user accounts with authentication credentials.

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'staff')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Relationships:**
- One-to-One with BarangayStaff (user_id)

#### 3.2 BarangayStaff Table

Extended profile for barangay staff members.

```sql
CREATE TABLE barangay_staff (
    staff_id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    address VARCHAR(255),
    purok_zone VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_staff_user_id ON barangay_staff(user_id);
CREATE INDEX idx_staff_purok_zone ON barangay_staff(purok_zone);
CREATE INDEX idx_staff_status ON barangay_staff(status);
```

#### 3.3 Residents Table

Stores resident information for SMS alerts.

```sql
CREATE TABLE residents (
    resident_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(20) UNIQUE NOT NULL,
    address VARCHAR(255) NOT NULL,
    purok_zone VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'evacuated')),
    sms_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_residents_mobile ON residents(mobile_number);
CREATE INDEX idx_residents_purok_zone ON residents(purok_zone);
CREATE INDEX idx_residents_status ON residents(status);
CREATE INDEX idx_residents_sms_enabled ON residents(sms_enabled);
```

#### 3.4 WaterLevelReadings Table

Stores all water level sensor readings.

```sql
CREATE TABLE water_level_readings (
    reading_id SERIAL PRIMARY KEY,
    water_level_cm DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Normal', 'Alert', 'Warning', 'Danger')),
    timestamp TIMESTAMP NOT NULL,
    sensor_status VARCHAR(20) DEFAULT 'online' CHECK (sensor_status IN ('online', 'offline', 'error')),
    gsm_status VARCHAR(20) DEFAULT 'connected' CHECK (gsm_status IN ('connected', 'disconnected', 'error')),
    firebase_synced BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_readings_timestamp ON water_level_readings(timestamp DESC);
CREATE INDEX idx_readings_status ON water_level_readings(status);
CREATE INDEX idx_readings_date ON water_level_readings(DATE(timestamp));
CREATE INDEX idx_readings_firebase_synced ON water_level_readings(firebase_synced);
```

#### 3.5 FloodAlerts Table

Stores flood alert events.

```sql
CREATE TABLE flood_alerts (
    alert_id SERIAL PRIMARY KEY,
    reading_id INTEGER NOT NULL,
    alert_level VARCHAR(20) NOT NULL CHECK (alert_level IN ('Alert', 'Warning', 'Danger')),
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES water_level_readings(reading_id) ON DELETE CASCADE
);

CREATE INDEX idx_alerts_timestamp ON flood_alerts(timestamp DESC);
CREATE INDEX idx_alerts_level ON flood_alerts(alert_level);
CREATE INDEX idx_alerts_is_active ON flood_alerts(is_active);
CREATE INDEX idx_alerts_reading_id ON flood_alerts(reading_id);
```

#### 3.6 SMSLogs Table

Stores all SMS message logs.

```sql
CREATE TABLE sms_logs (
    sms_id SERIAL PRIMARY KEY,
    alert_id INTEGER,
    resident_id INTEGER NOT NULL,
    recipient VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_status VARCHAR(20) DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'failed')),
    error_message TEXT,
    FOREIGN KEY (alert_id) REFERENCES flood_alerts(alert_id) ON DELETE SET NULL,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE CASCADE
);

CREATE INDEX idx_sms_sent_at ON sms_logs(sent_at DESC);
CREATE INDEX idx_sms_status ON sms_logs(delivery_status);
CREATE INDEX idx_sms_resident_id ON sms_logs(resident_id);
CREATE INDEX idx_sms_alert_id ON sms_logs(alert_id);
```

#### 3.7 Predictions Table

Stores AI flood prediction results.

```sql
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    reading_id INTEGER NOT NULL,
    flood_probability DECIMAL(5,2) NOT NULL CHECK (flood_probability BETWEEN 0 AND 100),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    alert_level VARCHAR(20) NOT NULL CHECK (alert_level IN ('Normal', 'Alert', 'Warning', 'Danger')),
    confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    recommended_action TEXT,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES water_level_readings(reading_id) ON DELETE CASCADE
);

CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX idx_predictions_severity ON predictions(severity);
CREATE INDEX idx_predictions_alert_level ON predictions(alert_level);
CREATE INDEX idx_predictions_reading_id ON predictions(reading_id);
```

#### 3.8 Reports Table

Stores generated reports metadata.

```sql
CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    report_type VARCHAR(20) NOT NULL CHECK (report_type IN ('daily', 'weekly', 'monthly', 'annual')),
    generated_by INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    file_path VARCHAR(255),
    file_format VARCHAR(10) CHECK (file_format IN ('pdf', 'xlsx', 'csv')),
    record_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX idx_reports_generated_by ON reports(generated_by);
CREATE INDEX idx_reports_date_range ON reports(start_date, end_date);
```

#### 3.9 Notifications Table

Stores user notifications.

```sql
CREATE TABLE notifications (
    notif_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info' CHECK (type IN ('info', 'warning', 'danger', 'success')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_notif_user_id ON notifications(user_id);
CREATE INDEX idx_notif_is_read ON notifications(is_read);
CREATE INDEX idx_notif_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notif_type ON notifications(type);
```

#### 3.10 ActivityLogs Table

Stores system activity logs for audit purposes.

```sql
CREATE TABLE activity_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    entity VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_logs_action ON activity_logs(action);
CREATE INDEX idx_logs_entity ON activity_logs(entity);
CREATE INDEX idx_logs_timestamp ON activity_logs(timestamp DESC);
CREATE INDEX idx_logs_entity_id ON activity_logs(entity_id);
```

#### 3.11 Settings Table

Stores system configuration settings.

```sql
CREATE TABLE settings (
    setting_id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_settings_key ON settings(key);
```

**Default Settings:**

```sql
INSERT INTO settings (key, value, description) VALUES
('normal_threshold', '30', 'Water level threshold for Normal status (cm)'),
('alert_threshold', '45', 'Water level threshold for Alert status (cm)'),
('warning_threshold', '60', 'Water level threshold for Warning status (cm)'),
('danger_threshold', '75', 'Water level threshold for Danger status (cm)'),
('reading_interval', '30', 'Sensor reading interval in seconds'),
('sync_interval', '60', 'Firebase sync interval in seconds'),
('sms_enabled', 'true', 'Enable SMS notifications'),
('ai_prediction_enabled', 'true', 'Enable AI flood prediction'),
('max_sms_per_hour', '100', 'Maximum SMS per hour to prevent spam'),
('system_name', 'Barangay Tonsuya Flood Detection System', 'System display name');
```

#### 3.12 AIModels Table

Stores AI model information and versions.

```sql
CREATE TABLE ai_models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('random_forest', 'decision_tree', 'logistic_regression')),
    version VARCHAR(20) NOT NULL,
    accuracy DECIMAL(5,2),
    precision DECIMAL(5,2),
    recall DECIMAL(5,2),
    f1_score DECIMAL(5,2),
    trained_at TIMESTAMP,
    model_file_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_models_name ON ai_models(model_name);
CREATE INDEX idx_ai_models_type ON ai_models(model_type);
CREATE INDEX idx_ai_models_is_active ON ai_models(is_active);
CREATE INDEX idx_ai_models_trained_at ON ai_models(trained_at DESC);
```

### 4. Views

#### 4.1 Current Water Level View

```sql
CREATE VIEW current_water_level AS
SELECT 
    reading_id,
    water_level_cm,
    status,
    timestamp,
    sensor_status,
    gsm_status
FROM water_level_readings
ORDER BY timestamp DESC
LIMIT 1;
```

#### 4.2 Recent Alerts View

```sql
CREATE VIEW recent_alerts AS
SELECT 
    fa.alert_id,
    fa.alert_level,
    fa.message,
    fa.timestamp,
    fa.is_active,
    wlr.water_level_cm
FROM flood_alerts fa
JOIN water_level_readings wlr ON fa.reading_id = wlr.reading_id
ORDER BY fa.timestamp DESC
LIMIT 10;
```

#### 4.3 SMS Statistics View

```sql
CREATE VIEW sms_statistics AS
SELECT 
    DATE(sent_at) as date,
    delivery_status,
    COUNT(*) as count
FROM sms_logs
GROUP BY DATE(sent_at), delivery_status
ORDER BY date DESC;
```

#### 4.4 Daily Water Level Summary View

```sql
CREATE VIEW daily_water_level_summary AS
SELECT 
    DATE(timestamp) as date,
    AVG(water_level_cm) as avg_level,
    MAX(water_level_cm) as max_level,
    MIN(water_level_cm) as min_level,
    COUNT(*) as reading_count
FROM water_level_readings
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### 5. Stored Procedures

#### 5.1 Create Flood Alert Procedure

```sql
CREATE OR REPLACE FUNCTION create_flood_alert(
    p_reading_id INTEGER,
    p_alert_level VARCHAR(20),
    p_message TEXT
)
RETURNS INTEGER AS $$
DECLARE
    v_alert_id INTEGER;
BEGIN
    INSERT INTO flood_alerts (reading_id, alert_level, message, timestamp)
    VALUES (p_reading_id, p_alert_level, p_message, CURRENT_TIMESTAMP)
    RETURNING alert_id INTO v_alert_id;
    
    RETURN v_alert_id;
END;
$$ LANGUAGE plpgsql;
```

#### 5.2 Log Activity Procedure

```sql
CREATE OR REPLACE FUNCTION log_activity(
    p_user_id INTEGER,
    p_action VARCHAR(50),
    p_entity VARCHAR(50),
    p_entity_id INTEGER,
    p_details JSONB,
    p_ip_address VARCHAR(45),
    p_user_agent TEXT
)
RETURNS INTEGER AS $$
DECLARE
    v_log_id INTEGER;
BEGIN
    INSERT INTO activity_logs (user_id, action, entity, entity_id, details, ip_address, user_agent)
    VALUES (p_user_id, p_action, p_entity, p_entity_id, p_details, p_ip_address, p_user_agent)
    RETURNING log_id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;
```

#### 5.3 Get Active Residents for SMS Procedure

```sql
CREATE OR REPLACE FUNCTION get_active_residents_for_sms()
RETURNS TABLE (
    resident_id INTEGER,
    full_name VARCHAR(100),
    mobile_number VARCHAR(20),
    purok_zone VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.resident_id,
        r.full_name,
        r.mobile_number,
        r.purok_zone
    FROM residents r
    WHERE r.status = 'active' AND r.sms_enabled = TRUE
    ORDER BY r.purok_zone, r.full_name;
END;
$$ LANGUAGE plpgsql;
```

### 6. Triggers

#### 6.1 Update Timestamp Trigger

```sql
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_barangay_staff_updated_at
    BEFORE UPDATE ON barangay_staff
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_residents_updated_at
    BEFORE UPDATE ON residents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_settings_updated_at
    BEFORE UPDATE ON settings
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
```

#### 6.2 Deactivate Previous Alerts Trigger

```sql
CREATE OR REPLACE FUNCTION deactivate_previous_alerts()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.alert_level IN ('Warning', 'Danger') THEN
        UPDATE flood_alerts
        SET is_active = FALSE
        WHERE is_active = TRUE AND alert_level = NEW.alert_level;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_deactivate_previous_alerts
    AFTER INSERT ON flood_alerts
    FOR EACH ROW
    EXECUTE FUNCTION deactivate_previous_alerts();
```

### 7. Database Constraints Summary

- **Primary Keys**: All tables have auto-incrementing primary keys
- **Foreign Keys**: All relationships enforced with ON DELETE CASCADE/SET NULL
- **Unique Constraints**: Username, email, mobile numbers are unique
- **Check Constraints**: Enum-like values validated (status, role, alert_level, etc.)
- **Not Null**: Required fields enforced
- **Default Values**: Timestamps, booleans, status fields have defaults

### 8. Index Summary

- **Performance Indexes**: All foreign keys, timestamps, and frequently queried fields
- **Composite Indexes**: Date ranges, user+status combinations
- **Unique Indexes**: Authentication and contact fields

### 9. Data Retention Policy

- **Water Level Readings**: Retain for 2 years
- **SMS Logs**: Retain for 1 year
- **Activity Logs**: Retain for 6 months
- **Notifications**: Retain for 3 months
- **Reports**: Permanent archive

### 10. Backup Strategy

- **Daily Full Backups**: Automated at 2:00 AM
- **Weekly Full Backups**: Sunday at 3:00 AM
- **Point-in-Time Recovery**: Enabled via WAL archiving
- **Off-site Storage**: Cloud backup replication

### 11. Security Considerations

- **Connection Security**: SSL/TLS required
- **Password Hashing**: bcrypt with salt
- **Row-Level Security**: Optional for multi-tenant scenarios
- **Audit Logging**: All sensitive operations logged
- **Regular Updates**: Automated security patching
