# Enhanced User Management System - SOAP API

A comprehensive SOAP API service for user management with role-based access control, audit logging, and authentication features.

## Features

- **User Management**: Registration, authentication, profile management
- **Role-Based Access Control (RBAC)**: Flexible permission system
- **Audit Logging**: Comprehensive activity tracking
- **Password Management**: Secure password handling with reset functionality
- **Session Management**: Secure token-based authentication
- **SOAP API**: Full SOAP protocol support with WSDL
- **Health Checks**: Monitoring and status endpoints
- **Docker Support**: Containerized deployment

## Technology Stack

- **Backend**: Python 3.11 with FastAPI
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Cache**: Redis for session management
- **Authentication**: JWT tokens with bcrypt password hashing
- **SOAP**: Spyne library for SOAP protocol implementation
- **Containerization**: Docker and Docker Compose

## Project Structure

```
soap-api/
├── src/                          # Source code
│   ├── api/                    # API endpoints
│   │   ├── health.py          # Health check endpoints
│   │   └── soap.py            # SOAP API implementation
│   ├── config/                  # Configuration
│   │   └── settings.py         # Application settings
│   ├── database/                 # Database related
│   │   ├── connection.py       # Database connection management
│   │   └── redis.py           # Redis connection management
│   ├── models/                   # Data models
│   │   ├── user.py            # User model
│   │   ├── role.py            # Role model
│   │   ├── permission.py      # Permission model
│   │   ├── user_role.py       # User-Role junction
│   │   ├── role_permission.py  # Role-Permission junction
│   │   ├── audit_log.py       # Audit log model
│   │   └── session.py         # Session model
│   ├── services/                 # Business logic
│   │   ├── auth_service.py    # Authentication service
│   │   ├── user_service.py    # User management service
│   │   ├── role_service.py    # Role management service
│   │   └── audit_service.py   # Audit service
│   └── utils/                    # Utilities
│       ├── logging.py         # Logging configuration
│       └── exceptions.py      # Custom exceptions
├── database/                       # Database scripts
│   └── init/                 # Initialization scripts
│       ├── 01-init-database.sql   # Schema creation
│       └── 02-insert-initial-data.sql # Initial data
├── tests/                         # Test files
├── docs/                          # Documentation
├── scripts/                       # Utility scripts
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile                     # Docker image configuration
├── requirements.txt               # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)
- Redis 7+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd soap-api
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - SOAP API: http://localhost:8000/soap
   - WSDL: http://localhost:8000/wsdl
   - Health Check: http://localhost:8000/health
   - API Documentation: http://localhost:8000/docs
   - pgAdmin (optional): http://localhost:5050

### Local Development

1. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb user_management_db
   
   # Run initialization scripts
   psql -d user_management_db -f database/init/01-init-database.sql
   psql -d user_management_db -f database/init/02-insert-initial-data.sql
   ```

4. **Set up Redis**
   ```bash
   # Start Redis server
   redis-server
   ```

5. **Run the application**
   ```bash
   python -m src.main
   ```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=user_management_db
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Application
APP_ENV=development
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_EXPIRATION_HOURS=24
BCRYPT_ROUNDS=12
```

### Database Configuration

The application uses PostgreSQL with the following schema:

- **users**: User accounts and profiles
- **roles**: User roles (ADMIN, MANAGER, USER)
- **permissions**: Granular permissions
- **user_roles**: User-role assignments
- **role_permissions**: Role-permission assignments
- **audit_logs**: Activity logging
- **sessions**: Authentication sessions

See `Database_Schema_Documentation.md` for detailed schema information.

## API Documentation

### SOAP Endpoints

The service provides the following SOAP operations:

#### Authentication
- `RegisterUser`: Register a new user
- `AuthenticateUser`: Authenticate user and get token
- `LogoutUser`: Invalidate user session

#### User Management
- `GetUserProfile`: Get user profile information
- `UpdateUserProfile`: Update user profile
- `GetAllUsers`: List all users (admin only)
- `DeactivateUser`: Deactivate user account

#### Role Management
- `CreateRole`: Create a new role
- `AssignRole`: Assign role to user
- `GetUserRoles`: Get user's roles

#### Audit
- `GetAuditLogs`: Get audit log entries

See `WSDL_Specification.md` for detailed SOAP API documentation.

### Health Check Endpoints

- `GET /health`: Overall health status
- `GET /health/ready`: Readiness probe
- `GET /health/live`: Liveness probe
- `GET /health/detailed`: Detailed system information

## Default Users

After initial setup, the following default users are available:

| Email | Password | Role | Description |
|--------|----------|------|-------------|
| admin@example.com | Admin123! | ADMIN | System administrator |
| manager@example.com | Admin123! | MANAGER | Test manager |
| testuser1@example.com | Admin123! | USER | Test user 1 |
| testuser2@example.com | Admin123! | USER | Test user 2 |
| testuser3@example.com | Admin123! | USER | Test user 3 |

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py
```

### Code Quality

```bash
# Format code
black src/

# Check linting
flake8 src/

# Sort imports
isort src/

# Type checking
mypy src/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Production Deployment

1. **Configure production environment**
   ```bash
   # Set production variables
   export APP_ENV=production
   export APP_DEBUG=false
   export JWT_SECRET_KEY=your-production-secret-key
   
   # Configure database and Redis connections
   export DB_HOST=your-production-db-host
   export REDIS_HOST=your-production-redis-host
   ```

2. **Build and deploy**
   ```bash
   # Build Docker image
   docker build -t soap-api:latest .
   
   # Deploy with Docker Compose
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Configure reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /soap {
           proxy_pass http://soap-api:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Monitoring

- **Health Checks**: Configure monitoring tools to check `/health` endpoint
- **Logs**: Application logs are structured JSON for easy parsing
- **Metrics**: Consider integrating Prometheus metrics
- **Alerts**: Set up alerts for service downtime

## Security

### Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: bcrypt with configurable rounds
- **Role-Based Access**: Granular permission system
- **Session Management**: Secure session storage in Redis
- **Rate Limiting**: Configurable rate limits per endpoint

### Data Protection

- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Input encoding and validation
- **HTTPS**: TLS encryption in production

### Audit & Compliance

- **Comprehensive Logging**: All actions are audited
- **Data Access Tracking**: Who accessed what and when
- **Change History**: Before/after values for updates
- **Security Events**: Failed logins, unauthorized access

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database connection parameters
   - Verify database is running
   - Check network connectivity

2. **Redis Connection Failed**
   - Verify Redis is running
   - Check Redis connection parameters
   - Test Redis with `redis-cli ping`

3. **Authentication Failures**
   - Check JWT secret key configuration
   - Verify password hashing configuration
   - Check user account status

4. **SOAP Request Failures**
   - Verify WSDL is accessible
   - Check SOAP action format
   - Review request headers

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export APP_DEBUG=true
```

Check application logs:
```bash
docker-compose logs -f soap-api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` directory
- Review the SOAP API specification in `WSDL_Specification.md`