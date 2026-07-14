# Backend Structure

## Files Created:

1. **app.py** - Main Flask application
2. **config.py** - Configuration settings
3. **models.py** - Database models (School, User)
4. **routes.py** - API endpoints
5. **utils.py** - Utility functions
6. **requirements.txt** - Python dependencies

## Setup Instructions:

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database
Edit config.py with your database credentials:
```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_password'
DB_NAME = 'educore'
```

### 3. Create .env file
```
DEBUG=True
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=educore
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

### 4. Run Application
```bash
python app.py
```

## API Endpoints:

### Health Check
- `GET /api/health` - Check if API is running
- `GET /api/db-check` - Check database connection

### School Management
- `POST /api/school/create` - Create new school
- `GET /api/school/<school_id>` - Get school details
- `PUT /api/school/<school_id>` - Update school

### User Management
- `POST /api/user/create` - Create new user
- `GET /api/user/<user_id>` - Get user details

## Next Phase:
- Frontend development
- Login/Authentication
- Dashboard design
