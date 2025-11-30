# SOAP API Wallet System

A complete SOAP API service for a Wallet System built with Python, Flask, SQLAlchemy, and PostgreSQL, designed to run in a Docker environment with JWT-based authentication.

## Features

### Authentication
- **register_user(username, email, password)** - Creates a new user account
- **login_user(username, password)** - Authenticates user and returns JWT token
- **logout_user(token)** - Revokes user token

### Wallet Operations (Require Authentication)
- **register_wallet(username, email)** - Creates a new wallet and returns wallet_uid
- **top_up(wallet_uid, amount)** - Adds balance to wallet
- **payment(wallet_uid, amount)** - Deducts balance (raises SOAP Fault if insufficient balance)
- **get_balance(wallet_uid)** - Returns current wallet balance

## Tech Stack

- **Python 3.12** - Programming language
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0.23** - ORM
- **PostgreSQL 16** - Database
- **JWT (PyJWT 2.8.0)** - Authentication tokens
- **bcrypt 4.1.2** - Password hashing
- **Docker & Docker Compose** - Containerization

## Project Structure

```
soap-api/
├── src/
│   ├── model.py          # SQLAlchemy models (Wallet, Transaction)
│   ├── auth.py           # Authentication models and service
│   └── app.py            # Flask SOAP application with authentication
├── Dockerfile            # Python service container definition
├── docker-compose.yml    # Multi-container setup
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── test_auth.py         # Authentication test script
└── README.md            # This file
```

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone and navigate to the project directory**
   ```bash
   cd soap-api
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the WSDL**
   - Open your browser and go to: `http://localhost:8001/?wsdl`

The application will automatically:
- Start PostgreSQL database
- Wait for database to be ready
- Create database tables
- Start the SOAP service on port 8001

## Authentication System

The API uses JWT (JSON Web Tokens) for authentication. All wallet operations require a valid JWT token to be included in the SOAP header.

### Authentication Flow

1. **Register User** - Create a new user account
2. **Login** - Authenticate and receive JWT token
3. **Use Token** - Include token in SOAP header for protected operations
4. **Logout** - Revoke token when done

### JWT Token Configuration

- **Algorithm**: HS256
- **Expiration**: 24 hours
- **Secret Key**: Configurable via `JWT_SECRET_KEY` environment variable

## API Endpoints

### WSDL URL
```
http://localhost:8001/?wsdl
```

### Authentication Methods (No Auth Required)

#### 1. register_user
- **Parameters**: username (string), email (string), password (string)
- **Returns**: user_id (string), message (string)
- **Description**: Creates a new user account with hashed password

#### 2. login_user
- **Parameters**: username (string), password (string)
- **Returns**: token (string), user_id (string), username (string)
- **Description**: Authenticates user and returns JWT token

#### 3. logout_user
- **Parameters**: token (string)
- **Returns**: message (string)
- **Description**: Revokes the provided JWT token

### Wallet Methods (Require Authentication)

#### 4. register_wallet
- **Parameters**: username (string), email (string)
- **Returns**: wallet_uid (string)
- **Description**: Creates a new wallet for a user

#### 5. top_up
- **Parameters**: wallet_uid (string), amount (decimal)
- **Returns**: Success message with new balance
- **Description**: Adds funds to wallet

#### 6. payment
- **Parameters**: wallet_uid (string), amount (decimal)
- **Returns**: Success message with remaining balance
- **Description**: Deducts funds from wallet (raises SOAP Fault if insufficient balance)

#### 7. get_balance
- **Parameters**: wallet_uid (string)
- **Returns**: Current balance (decimal)
- **Description**: Retrieves current wallet balance

### Authentication Header

For protected operations, include the JWT token in the SOAP header:

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wallet="wallet.soap">
  <soap:Header>
    <wallet:token>your_jwt_token_here</wallet:token>
  </soap:Header>
  <soap:Body>
    <!-- Your method call here -->
  </soap:Body>
</soap:Envelope>
```

## Environment Variables

The application uses the following environment variables (configured in `.env`):

```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=wallet_db
DB_USER=postgres
DB_PASSWORD=postgres

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

## Database Schema

### Authentication Tables

#### Users Table
- `id` (UUID, Primary Key)
- `username` (String, Unique)
- `email` (String, Unique)
- `password_hash` (String) - bcrypt hashed password
- `is_active` (Boolean) - Account status
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### Token Blacklist Table
- `id` (UUID, Primary Key)
- `token` (String, Unique) - JWT token
- `expires_at` (DateTime) - Token expiration
- `created_at` (DateTime)

### Wallet Tables

#### Wallets Table
- `wallet_uid` (UUID, Primary Key)
- `username` (String, Unique)
- `email` (String, Unique)
- `balance` (Decimal)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### Transactions Table
- `id` (UUID, Primary Key)
- `wallet_uid` (UUID, Foreign Key)
- `amount` (Decimal)
- `transaction_type` (String: 'top_up' or 'payment')
- `description` (Text)
- `created_at` (DateTime)

## Testing the API

You can test the SOAP API using tools like:

1. **SOAP UI**
2. **Postman** (with SOAP support)
3. **Python requests** with SOAP envelope

### Testing Authentication

A comprehensive test script is provided to test the authentication system:

```bash
# Run the authentication test
python test_auth.py
```

This script will test the complete authentication flow:
- User registration
- User login and token generation
- Protected wallet operations with authentication
- Token revocation (logout)
- Invalid token handling

### Example Python Test Client

```python
import requests

# WSDL URL
wsdl_url = "http://localhost:8001/?wsdl"

# Example SOAP request for register_user
soap_envelope = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wallet="wallet.soap">
  <soap:Body>
    <register_user xmlns="wallet.soap">
      <username>testuser</username>
      <email>test@example.com</email>
      <password>securepassword123</password>
    </register_user>
  </soap:Body>
</soap:Envelope>"""

headers = {
    'Content-Type': 'text/xml; charset=utf-8',
    'SOAPAction': 'register_user'
}

response = requests.post("http://localhost:8001/", data=soap_envelope, headers=headers)
print(response.text)
```

## Development

### Running without Docker

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**
   - Ensure PostgreSQL is running
   - Create database `wallet_db`
   - Update `.env` with your database credentials

3. **Run the application**
   ```bash
   cd src
   python app.py
   ```

### Stopping the Services

```bash
docker-compose down
```

### Viewing Logs

```bash
docker-compose logs -f wallet-api
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it wallet_postgres psql -U postgres -d wallet_db

# List tables
\dt

# Query wallets
SELECT * FROM wallets;

# Query transactions
SELECT * FROM transactions;
```

## Error Handling

The service provides comprehensive error handling:

- **Client Faults**: Invalid parameters, insufficient balance, duplicate users
- **Server Faults**: Database errors, internal server errors
- **Database Connection**: Automatic retry mechanism with health checks

## Health Checks

- **Application**: Health check via WSDL endpoint
- **Database**: PostgreSQL health check with retry logic
- **Container**: Docker health checks for both services

## License

This project is for demonstration purposes.
