# Quick Start Guide for SOAP API

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
4. [Basic Authentication Flow](#basic-authentication-flow)
5. [Common Use Cases](#common-use-cases)
6. [Testing with Postman](#testing-with-postman)
7. [Robot Framework Integration](#robot-framework-integration)
8. [Next Steps](#next-steps)

## Introduction

This quick start guide will help you get up and running with the Enhanced User Management System SOAP API in minutes. The API provides comprehensive user management, role-based access control, and audit logging capabilities designed specifically for Robot Framework testing and training.

### What You'll Learn
- How to set up your development environment
- Basic authentication and user management flows
- How to make your first API calls
- Testing strategies with Postman and Robot Framework

## Prerequisites

### Development Environment

Before you begin, ensure you have:

1. **Python 3.8+** installed
2. **Postman** (recommended for API testing)
3. **Robot Framework** (for automated testing)
4. **A code editor** (VS Code, PyCharm, etc.)

### API Access

You'll need:
- API endpoint URL: `http://localhost:8000/soap` (development)
- WSDL URL: `http://localhost:8000/wsdl`
- Valid credentials (or create a test account)

### Required Libraries

Install the necessary Python libraries:

```bash
pip install requests zeep robotframework
```

For Robot Framework SOAP testing:
```bash
pip install robotframework-requests robotframework-jsonlibrary
```

## Getting Started

### 1. Start the API Server

If running locally, start the SOAP API server:

```bash
# Navigate to project directory
cd soap-api

# Start the server
python src/main.py

# Or using Docker
docker-compose up -d
```

The server will be available at `http://localhost:8000`

### 2. Verify API Access

Check that the API is running by accessing the WSDL:

```bash
curl http://localhost:8000/wsdl
```

You should see the complete WSDL specification in XML format.

### 3. Set Up Postman

1. Import the provided Postman collection:
   - Open Postman
   - Click "Import"
   - Select the `SOAP_API_Postman_Collection.json` file
   - Configure environment variables:
     - `baseUrl`: `http://localhost:8000`
     - `testEmail`: Your test email address

## Basic Authentication Flow

### Step 1: Register a User

Create a new user account using the `RegisterUser` operation:

**SOAP Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:RegisterUserRequest>
            <tns:email>developer@example.com</tns:email>
            <tns:password>SecurePass123!</tns:password>
            <tns:firstName>Developer</tns:firstName>
            <tns:lastName>User</tns:lastName>
            <tns:phoneNumber>1234567890</tns:phoneNumber>
        </tns:RegisterUserRequest>
    </soap:Body>
</soap:Envelope>
```

**Using Python with Zeep:**
```python
from zeep import Client

# Create SOAP client
client = Client('http://localhost:8000/wsdl')

# Register user
result = client.service.RegisterUser(
    email='developer@example.com',
    password='SecurePass123!',
    firstName='Developer',
    lastName='User',
    phoneNumber='1234567890'
)

print(f"User registered with ID: {result['userId']}")
```

### Step 2: Authenticate User

Login to get an authentication token:

**SOAP Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:AuthenticateUserRequest>
            <tns:email>developer@example.com</tns:email>
            <tns:password>SecurePass123!</tns:password>
        </tns:AuthenticateUserRequest>
    </soap:Body>
</soap:Envelope>
```

**Using Python with Zeep:**
```python
# Authenticate user
auth_result = client.service.AuthenticateUser(
    email='developer@example.com',
    password='SecurePass123!'
)

# Store token for subsequent requests
auth_token = auth_result['token']
user_id = auth_result['userId']

print(f"Authenticated user {user_id} with token: {auth_token[:20]}...")
```

### Step 3: Get User Profile

Use the token to access protected resources:

**SOAP Request:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:GetUserProfileRequest>
            <tns:token>YOUR_AUTH_TOKEN_HERE</tns:token>
        </tns:GetUserProfileRequest>
    </soap:Body>
</soap:Envelope>
```

**Using Python with Zeep:**
```python
# Get user profile
profile = client.service.GetUserProfile(
    token=auth_token
)

print(f"User profile: {profile['user']['firstName']} {profile['user']['lastName']}")
```

## Common Use Cases

### Use Case 1: User Management

```python
from zeep import Client

class UserManager:
    def __init__(self, wsdl_url):
        self.client = Client(wsdl_url)
        self.auth_token = None
    
    def login(self, email, password):
        """Authenticate user and store token"""
        result = self.client.service.AuthenticateUser(
            email=email, password=password
        )
        if result['success']:
            self.auth_token = result['token']
            return True
        return False
    
    def create_user(self, user_data):
        """Create a new user"""
        return self.client.service.RegisterUser(**user_data)
    
    def get_user_profile(self, user_id=None):
        """Get user profile"""
        return self.client.service.GetUserProfile(
            token=self.auth_token,
            userId=user_id
        )
    
    def update_profile(self, updates):
        """Update user profile"""
        return self.client.service.UpdateUserProfile(
            token=self.auth_token,
            **updates
        )

# Usage
manager = UserManager('http://localhost:8000/wsdl')
if manager.login('admin@example.com', 'AdminPass123!'):
    profile = manager.get_user_profile()
    print(f"Logged in user: {profile['user']['firstName']}")
```

### Use Case 2: Role Management

```python
class RoleManager:
    def __init__(self, client, auth_token):
        self.client = client
        self.auth_token = auth_token
    
    def create_role(self, name, description=None):
        """Create a new role"""
        return self.client.service.CreateRole(
            token=self.auth_token,
            name=name,
            description=description
        )
    
    def assign_role(self, user_id, role_id):
        """Assign role to user"""
        return self.client.service.AssignRole(
            token=self.auth_token,
            userId=user_id,
            roleId=role_id
        )
    
    def get_user_roles(self, user_id=None):
        """Get user's roles"""
        return self.client.service.GetUserRoles(
            token=self.auth_token,
            userId=user_id
        )

# Usage
role_manager = RoleManager(client, auth_token)
new_role = role_manager.create_role('MANAGER', 'Manager role')
role_manager.assign_role(user_id=123, role_id=new_role['role']['id'])
```

### Use Case 3: Audit Logging

```python
class AuditManager:
    def __init__(self, client, auth_token):
        self.client = client
        self.auth_token = auth_token
    
    def get_audit_logs(self, start_date=None, end_date=None, action=None):
        """Get audit logs with filtering"""
        return self.client.service.GetAuditLogs(
            token=self.auth_token,
            startDate=start_date,
            endDate=end_date,
            action=action,
            page=1,
            pageSize=50
        )
    
    def get_user_activity(self, user_id, days=7):
        """Get user activity for last N days"""
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        return self.client.service.GetUserAuditLogs(
            token=self.auth_token,
            userId=user_id,
            startDate=start_date.isoformat() + 'Z',
            endDate=end_date.isoformat() + 'Z'
        )

# Usage
audit_manager = AuditManager(client, auth_token)
logs = audit_manager.get_audit_logs(action='USER_LOGIN_SUCCESS')
user_activity = audit_manager.get_user_activity(user_id=123, days=30)
```

## Testing with Postman

### 1. Import Collection

1. Download `SOAP_API_Postman_Collection.json`
2. Open Postman
3. Click "Import" → "Choose Files"
4. Select the collection file
5. Configure environment variables:
   - `baseUrl`: `http://localhost:8000`
   - `testEmail`: Your test email
   - `targetUserId`: A valid user ID for testing

### 2. Run Authentication Flow

1. **Register User**: Send a request to create a test user
2. **Authenticate User**: Login to get an auth token
3. **Get Profile**: Use the token to access user profile

### 3. Test Error Scenarios

1. **Invalid Login**: Try wrong password
2. **Expired Token**: Use an old token
3. **Missing Fields**: Send requests without required parameters
4. **Unauthorized Access**: Try admin operations without permissions

### 4. Use Postman Tests

The collection includes automated tests that:
- Verify response status codes
- Check for required response fields
- Store authentication tokens
- Validate error responses

## Robot Framework Integration

### 1. Basic Test Structure

Create a test file `user_management_tests.robot`:

```robotframework
*** Settings ***
Library    RequestsLibrary
Library    XML
Library    Collections
Resource    soap_keywords.robot

*** Variables ***
${SOAP_ENDPOINT}    http://localhost:8000/soap
${WSDL_URL}         http://localhost:8000/wsdl
${TEST_EMAIL}        test@example.com
${TEST_PASSWORD}     SecurePass123!

*** Test Cases ***
User Registration Should Succeed
    [Documentation]    Test successful user registration
    [Tags]    registration    positive
    
    ${user_data}=    Create Dictionary
    ...    email=${TEST_EMAIL}
    ...    password=${TEST_PASSWORD}
    ...    firstName=Test
    ...    lastName=User
    
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    
    Should Be Equal As Strings    ${response['success']}    true
    Should Contain    ${response['email']}    ${TEST_EMAIL}
    Should Be True    ${response['userId']} > 0

User Authentication Should Succeed
    [Documentation]    Test successful user authentication
    [Tags]    authentication    positive
    
    ${auth_data}=    Create Dictionary
    ...    email=${TEST_EMAIL}
    ...    password=${TEST_PASSWORD}
    
    ${response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    
    Should Be Equal As Strings    ${response['success']}    true
    Should Not Be Empty    ${response['token']}
    Set Suite Variable    ${AUTH_TOKEN}    ${response['token']}

Get User Profile Should Succeed
    [Documentation]    Test getting user profile with valid token
    [Tags]    profile    positive
    [Setup]    Get Authentication Token
    
    ${profile_data}=    Create Dictionary
    ...    token=${AUTH_TOKEN}
    
    ${response}=    Call SOAP Method    GetUserProfile    ${profile_data}
    
    Should Be Equal As Strings    ${response['success']}    true
    Should Contain    ${response['user']['email']}    ${TEST_EMAIL}

*** Keywords ***
Get Authentication Token
    ${auth_data}=    Create Dictionary
    ...    email=${TEST_EMAIL}
    ...    password=${TEST_PASSWORD}
    
    ${response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    Set Suite Variable    ${AUTH_TOKEN}    ${response['token']}
```

### 2. SOAP Keywords Library

Create `soap_keywords.robot`:

```robotframework
*** Settings ***
Library    RequestsLibrary
Library    XML
Library    String

*** Keywords ***
Call SOAP Method
    [Arguments]    ${method_name}    ${data}
    [Documentation]    Call SOAP method with given data
    
    ${soap_request}=    Build SOAP Request    ${method_name}    ${data}
    
    ${headers}=    Create Dictionary
    ...    Content-Type=text/xml; charset=utf-8
    ...    SOAPAction=http://example.com/usermanagement/${method_name}
    
    ${response}=    POST
    ...    ${SOAP_ENDPOINT}
    ...    data=${soap_request}
    ...    headers=${headers}
    
    ${response_xml}=    Parse XML    ${response.text}
    ${response_data}=    Extract SOAP Response    ${response_xml}    ${method_name}
    
    [Return]    ${response_data}

Build SOAP Request
    [Arguments]    ${method_name}    ${data}
    [Documentation]    Build SOAP request XML
    
    ${xml}=    Catenate
    ...    <?xml version="1.0" encoding="UTF-8"?>
    ...    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
    ...                   xmlns:tns="http://example.com/usermanagement">
    ...        <soap:Header/>
    ...        <soap:Body>
    ...            <tns:${method_name}Request>
    
    FOR    ${key}    IN    @{data.keys()}
        ${value}=    Get From Dictionary    ${data}    ${key}
        ${xml}=    Catenate    ${xml}
        ...                <tns:${key}>${value}</tns:${key}>
    END
    
    ${xml}=    Catenate    ${xml}
    ...            </tns:${method_name}Request>
    ...        </soap:Body>
    ...    </soap:Envelope>
    
    [Return]    ${xml}

Extract SOAP Response
    [Arguments]    ${xml}    ${method_name}
    [Documentation]    Extract data from SOAP response
    
    ${response_xpath}=    Set Variable    //tns:${method_name}Response
    ${response_node}=    Get Element    ${xml}    ${response_xpath}
    
    ${result}=    Create Dictionary
    FOR    ${child}    IN    @{response_node.getchildren()}
        ${tag}=    Get Element Tag    ${child}
        ${text}=    Get Element Text    ${child}
        Set To Dictionary    ${result}    ${tag}    ${text}
    END
    
    [Return]    ${result}
```

### 3. Running Tests

Execute the tests:

```bash
# Run all tests
robot user_management_tests.robot

# Run specific tags
robot --include registration user_management_tests.robot
robot --include authentication user_management_tests.robot

# Generate detailed report
robot --loglevel DEBUG user_management_tests.robot
```

## Next Steps

### Explore Advanced Features

1. **Role-Based Access Control**: Implement permission-based access
2. **Audit Logging**: Monitor and track all API activities
3. **Password Management**: Implement password reset flows
4. **Error Handling**: Build robust error handling mechanisms

### Integration Examples

1. **Web Application Integration**: Integrate with web frameworks
2. **Mobile App Backend**: Use as backend for mobile applications
3. **Microservices Architecture**: Use as user service in microservices
4. **API Gateway Integration**: Route through API gateway

### Production Considerations

1. **Security**: Implement HTTPS, rate limiting, and input validation
2. **Performance**: Add caching, connection pooling, and monitoring
3. **Scalability**: Design for horizontal scaling
4. **Monitoring**: Implement logging, metrics, and alerting

### Additional Resources

- [Complete API Documentation](SOAP_API_Documentation.md)
- [API Reference Guide](SOAP_API_Reference.md)
- [Robot Framework Testing Guide](Robot_Framework_Testing_Guide.md)
- [Troubleshooting Guide](Troubleshooting_Guide.md)
- [WSDL Specification](WSDL_Specification.md)

## Support

If you encounter issues:

1. Check the [Troubleshooting Guide](Troubleshooting_Guide.md)
2. Review error codes in the [API Reference](SOAP_API_Reference.md)
3. Verify your request format against examples
4. Test with the provided Postman collection

---

*This quick start guide is part of the Enhanced User Management System documentation suite, designed specifically for Robot Framework testing and training purposes.*