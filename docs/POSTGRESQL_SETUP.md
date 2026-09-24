# PostgreSQL Setup Guide for AI Flood Detection System

## Prerequisites

- Windows operating system
- Administrator privileges (for installation)

## Installation Options

### Option 1: Official PostgreSQL Installer (Recommended)

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the latest stable version (recommended: PostgreSQL 15 or 16)

2. **Run the Installer**
   - Double-click the downloaded installer
   - Follow the installation wizard with these settings:
     - **Installation Directory**: Keep default (e.g., `C:\Program Files\PostgreSQL\16`)
     - **Data Directory**: Keep default
     - **Password**: Set a strong password for the `postgres` user (remember this!)
     - **Port**: Keep default `5432`
     - **Locale**: Keep default
     - **Components**: Install all components including pgAdmin

3. **Verify Installation**
   - Open Command Prompt or PowerShell
   - Run: `psql --version`
   - You should see the PostgreSQL version number

### Option 2: Using Chocolatey

If you have Chocolatey package manager installed:

```powershell
choco install postgresql -y
```

### Option 3: Using Docker

If you have Docker installed:

```powershell
docker run --name flood_detection_db ^
  -e POSTGRES_PASSWORD=your_password ^
  -e POSTGRES_DB=flood_detection_db ^
  -p 5432:5432 ^
  -d postgres:15
```

## Database Setup

### 1. Create the Database

Using pgAdmin (GUI):
1. Open pgAdmin (installed with PostgreSQL)
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Enter database name: `flood_detection_db`
5. Click "Save"

Using Command Line:
```bash
# Open SQL Shell (psql) from Start Menu
# Login with your postgres password
CREATE DATABASE flood_detection_db;
\q
```

### 2. Create a Dedicated User (Optional but Recommended)

```sql
-- In SQL Shell (psql)
CREATE USER flood_detection_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE flood_detection_db TO flood_detection_user;
\q
```

## Django Configuration

### 1. Update .env File

Edit `backend/Django/.env` with your PostgreSQL credentials:

```env
# Database (PostgreSQL)
DB_NAME=flood_detection_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

If you created a dedicated user:
```env
DB_NAME=flood_detection_db
DB_USER=flood_detection_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Install PostgreSQL Adapter

```bash
cd backend/Django
.\venv\Scripts\Activate.ps1
pip install psycopg2-binary
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

## Troubleshooting

### Connection Issues

**Error**: `connection to server at "localhost" (::1), port 5432 failed`

**Solutions**:
1. Ensure PostgreSQL service is running:
   - Open Services (`services.msc`)
   - Find "postgresql-x64-16" (version may vary)
   - Ensure it's running

2. Check firewall settings
3. Verify password in .env file matches PostgreSQL password

### psql Command Not Found

**Solution**: Add PostgreSQL bin directory to PATH:
- Default path: `C:\Program Files\PostgreSQL\16\bin`
- Add to System Environment Variables → Path

### Permission Denied

**Solution**: Run Command Prompt as Administrator

## Testing the Connection

Test your Django database connection:

```bash
cd backend/Django
.\venv\Scripts\Activate.ps1
python manage.py dbshell
```

If successful, you'll enter the PostgreSQL shell. Type `\q` to exit.

## Production Considerations

For production deployment:

1. **Use strong passwords**
2. **Create dedicated database users** (not postgres)
3. **Enable SSL connections**
4. **Configure connection pooling**
5. **Set up regular backups**
6. **Monitor database performance**

## Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Django PostgreSQL Documentation: https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes
- pgAdmin Documentation: https://www.pgadmin.org/docs/

## Quick Reference

**Default PostgreSQL Settings**:
- Port: 5432
- Superuser: postgres
- Default Database: postgres
- Config File: `C:\Program Files\PostgreSQL\16\data\postgresql.conf`

**Useful Commands**:
```bash
# Start PostgreSQL service
net start postgresql-x64-16

# Stop PostgreSQL service  
net stop postgresql-x64-16

# Check PostgreSQL status
sc query postgresql-x64-16
```
