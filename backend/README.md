# Campus Resource Hub - Backend API

Flask REST API backend for the Campus Resource Hub application.

## 📋 Project Structure

```
backend/
├── app.py                 # Flask application factory
├── config.py             # Configuration for different environments
├── extensions.py         # Flask extensions initialization
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── routes/              # API blueprints/endpoints
│   ├── __init__.py
│   └── health.py        # Health check endpoints
├── models/              # SQLAlchemy ORM models
│   └── __init__.py
├── services/            # Business logic layer
│   └── __init__.py
├── data_access/         # Repository pattern (CRUD operations)
│   └── __init__.py
├── static/              # Static files and uploads
│   └── uploads/
└── templates/           # Jinja2 templates (if needed)
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and update configuration as needed (especially `SECRET_KEY` for production).

6. **Initialize the database:**
   ```bash
   # Create database tables
   flask db init  # First time only
   flask db migrate -m "Initial migration"
   flask db upgrade
   
   # Or use the custom CLI command
   flask init-db
   ```

## 🏃 Running the Application

### Development Server

Set the Flask app environment variable and run:

```bash
export FLASK_APP=backend.app  # On Windows: set FLASK_APP=backend.app
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
flask run
```

Or simply:
```bash
python app.py
```

The API will be available at: `http://localhost:5000`

### Verify Installation

Test the health check endpoint:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "Campus Resource Hub API is running",
  "timestamp": "2025-11-11T23:00:00Z",
  "version": "1.0.0"
}
```

Test database health:
```bash
curl http://localhost:5000/api/health/db
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

With coverage report:
```bash
pytest --cov=backend --cov-report=html
```

Run code quality checks:
```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

## 📚 API Documentation

### Base URL
- **Development:** `http://localhost:5000/api`
- **Production:** `https://your-domain.com/api`

### Available Endpoints

#### Health Check
- `GET /api/health` - API health status
- `GET /api/health/db` - Database health status

#### Authentication (Coming Soon)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/logout` - User logout

#### Resources (Coming Soon)
- `GET /api/resources` - List all resources
- `GET /api/resources/<id>` - Get resource details
- `POST /api/resources` - Create new resource (auth required)
- `PUT /api/resources/<id>` - Update resource (auth required)
- `DELETE /api/resources/<id>` - Delete resource (auth required)

#### Bookings (Coming Soon)
- `GET /api/bookings` - List user's bookings
- `POST /api/bookings` - Create new booking
- `PUT /api/bookings/<id>/approve` - Approve booking (admin/owner)
- `PUT /api/bookings/<id>/cancel` - Cancel booking

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `SECRET_KEY` - Flask secret key (required in production)
- `DATABASE_URL` - Database connection string
- `FLASK_ENV` - Environment (development, testing, production)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)

### Database Configuration

**Development (SQLite):**
```
DATABASE_URL=sqlite:///dev.db
```

**Production (PostgreSQL):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/campus_resource_hub
```

## 🛡️ Security

This application implements several security best practices:

- ✅ **CSRF Protection** - Enabled via Flask-WTF
- ✅ **Password Hashing** - bcrypt with salt
- ✅ **Parameterized Queries** - SQLAlchemy ORM prevents SQL injection
- ✅ **Input Validation** - WTForms for server-side validation
- ✅ **CORS Configuration** - Controlled via environment variables
- ✅ **Session Security** - HTTP-only cookies, secure flags in production
- ✅ **File Upload Security** - Type and size restrictions

## 📦 Database Migrations

```bash
# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history
```

## 🐛 Troubleshooting

### Common Issues

**Import errors:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Database errors:**
```bash
# Reset database (CAUTION: Deletes all data)
rm dev.db
flask db upgrade
```

**Port already in use:**
```bash
# Use a different port
flask run --port 5001
```

## 📝 Development Workflow

1. Create a new branch for your feature
2. Make changes and write tests
3. Run code quality checks: `black .`, `ruff check .`, `mypy .`
4. Run tests: `pytest`
5. Commit changes
6. Create pull request

## 🤝 Contributing

This project follows these guidelines:

- **Code Style:** Black formatter, Ruff linter
- **Type Hints:** Use mypy for type checking
- **Testing:** pytest for all tests
- **Documentation:** Docstrings for all functions and classes
- **Security:** Follow OWASP guidelines
- **AI Usage:** Document all AI-assisted development in `.prompt/dev_notes.md`

## 📄 License

This project is part of the 2025 AiDD Capstone for Indiana University.

## 📞 Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**Status:** Phase 1 Complete ✅ - Flask backend scaffold is ready for feature implementation.
