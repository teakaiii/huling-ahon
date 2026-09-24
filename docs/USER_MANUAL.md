# User Manual

## Table of Contents

1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [Dashboard Navigation](#dashboard-navigation)
4. [Monitoring Water Levels](#monitoring-water-levels)
5. [Managing Residents](#managing-residents)
6. [Viewing Alerts](#viewing-alerts)
7. [Generating Reports](#generating-reports)
8. [Analytics and Statistics](#analytics-and-statistics)
9. [SMS Notifications](#sms-notifications)
10. [System Settings](#system-settings)
11. [Troubleshooting](#troubleshooting)

## System Overview

AHON FloodWatch for Barangay Tonsuya, Malabon is a comprehensive flood monitoring and alert system that provides real-time water level monitoring, AI-powered flood predictions, and automated SMS notifications to residents.

### Key Features

- **Real-time Water Level Monitoring**: Continuous monitoring of water levels with automatic status determination
- **AI Flood Prediction**: Machine learning models predict flood probability and severity
- **Automated SMS Alerts**: Automatic SMS notifications to residents during flood conditions
- **Interactive Dashboard**: Web-based dashboard for monitoring and management
- **Comprehensive Reporting**: Generate detailed reports for analysis and documentation
- **Activity Logging**: Complete audit trail of all system activities

### System Components

1. **Hardware**: Arduino Uno with water level sensor and SIM800L GSM module
2. **Backend**: Django REST API with PostgreSQL database
3. **Frontend**: React web dashboard with Material UI
4. **Cloud**: Firebase Realtime Database for real-time data sync
5. **AI Module**: Scikit-learn based flood prediction models

## Getting Started

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for dashboard access
- Mobile phone for receiving SMS alerts (for residents)

### Accessing the Dashboard

1. Open your web browser
2. Navigate to the system URL (provided by your administrator)
3. Enter your username and password
4. Click "Sign In"

### First Login

Upon first login, you will be prompted to:
- Change your password (recommended)
- Review your profile information
- Familiarize yourself with the dashboard layout

## Dashboard Navigation

### Main Navigation Menu

The dashboard sidebar provides access to the following sections:

- **Dashboard**: Overview of current system status
- **Water Level**: Detailed water level monitoring and history
- **Residents**: Manage resident information and SMS subscriptions
- **Reports**: Generate and download system reports
- **Analytics**: View system performance and data analysis
- **SMS Logs**: Track SMS notification delivery
- **Notifications**: View system notifications and alerts
- **Settings**: Configure system parameters and thresholds

### User Profile

Click on your avatar in the top-right corner to:
- View your profile
- Change your password
- Log out of the system

## Monitoring Water Levels

### Current Water Level

The dashboard displays the current water level with:
- Water level in centimeters
- Current status (Normal, Alert, Warning, Danger)
- Timestamp of last reading
- Sensor and GSM status

### Water Level Status

The system categorizes water levels as follows:

- **Normal** (< 30 cm): Safe conditions
- **Alert** (30-44 cm): Elevated water level, monitor closely
- **Warning** (45-59 cm): High water level, prepare for potential evacuation
- **Danger** (≥ 60 cm): Critical level, initiate evacuation procedures

### Historical Data

View historical water level data:
- Select time range (1 hour, 6 hours, 24 hours, 1 week)
- View trend charts
- Export data for analysis

### Water Level Statistics

Access statistics including:
- Average water level
- Maximum and minimum levels
- Total number of readings

## Managing Residents

### Adding New Residents

1. Navigate to the Residents section
2. Click "Add Resident"
3. Fill in the required information:
   - Full Name
   - Mobile Number (format: +63XXXXXXXXXX)
   - Address
   - Purok/Zone
   - Status (Active/Inactive/Evacuated)
   - SMS Enabled (Yes/No)
4. Click "Add"

### Editing Resident Information

1. Navigate to the Residents section
2. Find the resident you want to edit
3. Click the Edit icon
4. Update the information
5. Click "Update"

### Deleting Residents

1. Navigate to the Residents section
2. Find the resident you want to delete
3. Click the Delete icon
4. Confirm the deletion

### Searching and Filtering

- Use the search bar to find residents by name, mobile number, or address
- Filter by Purok/Zone using the dropdown
- View resident statistics in the summary cards

### Resident Status

- **Active**: Resident is currently living in the area and will receive SMS alerts
- **Inactive**: Resident is not currently receiving alerts
- **Evacuated**: Resident has been evacuated due to flood conditions

## Viewing Alerts

### Active Alerts

The dashboard displays currently active flood alerts with:
- Alert level (Alert, Warning, Danger)
- Water level at time of alert
- Timestamp
- Alert message

### Alert History

View historical alerts:
- Filter by time range
- View alert trends
- Export alert data

### Alert Statistics

Access statistics including:
- Total alerts
- Alerts by level
- Active alert count

## Generating Reports

### Report Types

The system supports the following report types:

- **Daily Report**: 24-hour summary
- **Weekly Report**: 7-day summary
- **Monthly Report**: 30-day summary
- **Annual Report**: Yearly summary

### Generating a Report

1. Navigate to the Reports section
2. Click "Generate Report"
3. Select:
   - Report type
   - File format (PDF, Excel, CSV)
4. Click "Generate"
5. Wait for the report to be generated
6. Click "Download" to save the report

### Report Contents

Reports include:
- Water level summary
- Alert history
- SMS notification statistics
- Resident information
- System performance metrics

## Analytics and Statistics

### Water Level Trends

View water level trends over time with interactive charts:
- Line charts for trend analysis
- Area charts for volume visualization
- Customizable time ranges

### Alert History

Analyze alert patterns:
- Bar charts showing alert frequency
- Color-coded by severity
- Time-based analysis

### SMS Statistics

Monitor SMS delivery:
- Pie chart showing delivery status
- Success rate tracking
- Failed message analysis

### Prediction Accuracy

View AI model performance:
- Average confidence score
- Severity distribution
- Total predictions made

### Resident Distribution

View resident distribution:
- Bar chart by Purok/Zone
- Population density analysis
- SMS coverage statistics

## SMS Notifications

### Viewing SMS Logs

The SMS Logs section shows:
- All sent SMS messages
- Delivery status
- Recipient information
- Timestamp
- Alert level (if applicable)

### Delivery Status

SMS messages can have the following statuses:
- **Pending**: Message queued for delivery
- **Sent**: Message sent to gateway
- **Delivered**: Message successfully delivered
- **Failed**: Message delivery failed

### SMS Statistics

View statistics including:
- Total messages sent
- Messages by status
- Failed message count
- Delivery rate

### Troubleshooting SMS Issues

If SMS messages are failing:
1. Check GSM module status in System Status
2. Verify recipient mobile numbers are correct
3. Check SMS rate limits
4. Review error messages in SMS Logs

## System Settings

### Flood Thresholds

Configure water level thresholds:
- **Normal Threshold**: Level below which conditions are normal
- **Alert Threshold**: Level that triggers alert status
- **Warning Threshold**: Level that triggers warning status
- **Danger Threshold**: Level that triggers danger status

To modify thresholds:
1. Navigate to Settings
2. Enter new threshold values
3. Click "Save Thresholds"
4. Confirm changes

### System Settings

Configure system parameters:
- **Enable SMS Notifications**: Toggle SMS alerts on/off
- **Enable AI Prediction**: Toggle AI predictions on/off
- **Reading Interval**: Set sensor reading frequency
- **Sync Interval**: Set Firebase sync frequency
- **Max SMS Per Hour**: Set SMS rate limit

### System Information

View system information:
- System name
- Version number
- Location
- Last update time

## Troubleshooting

### Common Issues

#### Dashboard Not Loading

**Possible Causes:**
- Internet connection issues
- Server downtime
- Browser compatibility issues

**Solutions:**
- Check your internet connection
- Try a different browser
- Contact your administrator

#### Water Level Not Updating

**Possible Causes:**
- Sensor offline
- GSM module disconnected
- Firebase sync issues

**Solutions:**
- Check System Status in Dashboard
- Verify hardware connections
- Contact technical support

#### SMS Not Delivered

**Possible Causes:**
- Invalid mobile number
- GSM module issues
- Rate limit exceeded

**Solutions:**
- Verify mobile number format (+63XXXXXXXXXX)
- Check SMS Logs for error messages
- Wait for rate limit to reset

#### Cannot Log In

**Possible Causes:**
- Incorrect username/password
- Account locked
- System maintenance

**Solutions:**
- Verify your credentials
- Contact administrator to reset password
- Check for system maintenance notices

### Getting Help

For technical support:
1. Check this user manual first
2. Review error messages in the system
3. Contact your system administrator
4. Submit a support ticket with:
   - Your username
   - Description of the issue
   - Steps to reproduce
   - Screenshot if applicable

### Best Practices

- **Regular Monitoring**: Check the dashboard regularly, especially during rainy season
- **Keep Information Updated**: Ensure resident information is always current
- **Test Alerts**: Periodically test SMS notifications to ensure they're working
- **Review Reports**: Generate and review reports regularly for trend analysis
- **Backup Data**: Regularly backup important data and reports
- **Security**: Keep your password secure and change it regularly

### Emergency Procedures

In case of actual flood:

1. **Monitor Dashboard**: Keep the dashboard open for real-time updates
2. **Check Alerts**: Pay attention to all system alerts
3. **Verify SMS**: Ensure residents are receiving SMS notifications
4. **Coordinate**: Work with local authorities for evacuation
5. **Document**: Keep records of all actions taken
6. **Report**: Generate after-action reports once the situation is resolved

## Appendix

### Glossary

- **API**: Application Programming Interface
- **GSM**: Global System for Mobile Communications
- **IoT**: Internet of Things
- **Purok**: A subdivision of a barangay (village/ward)
- **SMS**: Short Message Service

### Contact Information

- **System Administrator**: [Contact details]
- **Technical Support**: [Contact details]
- **Emergency Services**: [Contact details]

### Version History

- **v1.0.0** (2026-07-13): Initial release
