# Robot Framework Testing Guide for Enhanced User Management System

## Overview
This guide provides comprehensive instructions for testing the Enhanced User Management System SOAP API using Robot Framework. It includes test case examples, best practices, and implementation strategies.

## Prerequisites

### 1. Robot Framework Installation
```bash
# Install Robot Framework
pip install robotframework

# Install required libraries
pip install robotframework-requests
pip install robotframework-XML
pip install robotframework-databaselibrary
pip install robotframework-seleniumlibrary  # For web UI testing if needed
pip install psycopg2-binary  # PostgreSQL driver
```

### 2. Python Dependencies
```bash
# Additional libraries for SOAP testing
pip install zeep  # SOAP client library
pip install lxml  # XML processing
pip install python-dateutil  # Date handling
```

### 3. Test Environment Setup
- PostgreSQL database with test data
- SOAP API service running
- Test user accounts with various roles
- Network connectivity to API endpoints

## Project Structure

### Test Directory Organization
```
robot-tests/
├── resources/
│   ├── soap_keywords.robot
│   ├── database_keywords.robot
│   ├── test_data.robot
│   └── common_keywords.robot
├── testdata/
│   ├── valid_users.csv
│   ├── invalid_users.csv
│   └── test_permissions.json
├── results/
│   ├── reports/
│   ├── logs/
│   └── screenshots/
├── variables/
│   ├── config.py
│   └── test_variables.py
└── tests/
    ├── authentication/
    ├── user_management/
    ├── role_management/
    ├── permission_management/
    ├── password_management/
    ├── audit/
    ├── security/
    └── performance/
```

## Core Keywords and Libraries

### 1. SOAP Keywords (`resources/soap_keywords.robot`)
```robotframework
*** Settings ***
Library    Zeep
Library    Collections
Library    XML
Library    String
Library    DateTime
Resource   ../variables/config.py

*** Variables ***
${WSDL_URL}           ${SOAP_ENDPOINT}/wsdl
${SOAP_ENDPOINT}      http://localhost:8000/soap
${DEFAULT_TIMEOUT}    30

*** Keywords ***
Initialize SOAP Client
    [Documentation]    Initialize SOAP client with WSDL
    [Arguments]    ${wsdl_url}=${WSDL_URL}
    ${client}=    Zeep.Create Client    ${wsdl_url}
    Set Suite Variable    ${SOAP_CLIENT}    ${client}
    [Return]    ${client}

Call SOAP Method
    [Documentation]    Call a SOAP method and return response
    [Arguments]    ${method_name}    ${args}=${None}    ${timeout}=${DEFAULT_TIMEOUT}
    ${service}=    Set Variable    ${SOAP_CLIENT}.service
    ${operation}=    Get From Dictionary    ${service}    ${method_name}
    
    Run Keyword If    ${args} is not ${None}
    ...    ${response}=    Call Method    ${operation}    **${args}
    ...    ELSE    ${response}=    Call Method    ${operation}
    
    [Return]    ${response}

Validate SOAP Response
    [Documentation]    Validate SOAP response structure and success
    [Arguments]    ${response}    ${expected_success}=${True}
    Should Not Be None    ${response}
    Run Keyword If    ${expected_success}
    ...    Should Be True    ${response['success']}
    ...    ELSE    Should Not Be True    ${response['success']}

Extract Error Details
    [Documentation]    Extract error details from SOAP fault
    [Arguments]    ${response}
    ${error_code}=    Set Variable    ${response['faultcode']}
    ${error_message}=    Set Variable    ${response['faultstring']}
    [Return]    ${error_code}    ${error_message}

Create User Request Data
    [Documentation]    Create user registration request data
    [Arguments]    ${email}    ${password}    ${first_name}    ${last_name}    ${phone_number}=${None}
    ${user_data}=    Create Dictionary
    ...    email=${email}
    ...    password=${password}
    ...    firstName=${first_name}
    ...    lastName=${last_name}
    ...    phoneNumber=${phone_number}
    [Return]    ${user_data}

Create Auth Request Data
    [Documentation]    Create authentication request data
    [Arguments]    ${email}    ${password}
    ${auth_data}=    Create Dictionary
    ...    email=${email}
    ...    password=${password}
    [Return]    ${auth_data}

Get Token From Response
    [Documentation]    Extract authentication token from response
    [Arguments]    ${response}
    ${token}=    Set Variable    ${response['token']}
    Should Not Be Empty    ${token}
    [Return]    ${token}

Validate Token Format
    [Documentation]    Validate JWT token format
    [Arguments]    ${token}
    Should Not Be Empty    ${token}
    ${token_parts}=    Split String    ${token}    .
    Should Be Equal As Integers    ${len(${token_parts})}    3
```

### 2. Database Keywords (`resources/database_keywords.robot`)
```robotframework
*** Settings ***
Library    DatabaseLibrary
Library    psycopg2
Resource   ../variables/config.py

*** Variables ***
${DB_HOST}        localhost
${DB_PORT}        5432
${DB_NAME}        user_management_test
${DB_USER}        test_user
${DB_PASSWORD}    test_password

*** Keywords ***
Connect To Test Database
    [Documentation]    Connect to PostgreSQL test database
    Connect To Database Using Custom Params
    ...    psycopg2
    ...    host=${DB_HOST} port=${DB_PORT} dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD}

Disconnect From Database
    [Documentation]    Disconnect from database
    Disconnect From Database

Create Test User In Database
    [Documentation]    Create test user directly in database
    [Arguments]    ${email}    ${password_hash}    ${first_name}    ${last_name}    ${status}=ACTIVE
    ${query}=    Set Variable    INSERT INTO users (email, password_hash, first_name, last_name, status) VALUES (%s, %s, %s, %s, %s) RETURNING id
    ${result}=    Query    ${query}    ${email}    ${password_hash}    ${first_name}    ${last_name}    ${status}
    ${user_id}=    Set Variable    ${result[0][0]}
    [Return]    ${user_id}

Verify User Exists In Database
    [Documentation]    Verify user exists in database
    [Arguments]    ${email}
    ${query}=    Set Variable    SELECT id, email, status FROM users WHERE email = %s
    ${result}=    Query    ${query}    ${email}
    Should Not Be Empty    ${result}
    [Return]    ${result[0]}

Verify Audit Log Exists
    [Documentation]    Verify audit log entry exists
    [Arguments]    ${user_id}    ${action}    ${resource_type}
    ${query}=    Set Variable    SELECT id FROM audit_logs WHERE user_id = %s AND action = %s AND resource_type = %s
    ${result}=    Query    ${query}    ${user_id}    ${action}    ${resource_type}
    Should Not Be Empty    ${result}
    [Return]    ${result[0][0]}

Clean Up Test Data
    [Documentation]    Clean up test data from database
    [Arguments]    ${email}
    # Delete audit logs for user
    Execute SQL String    DELETE FROM audit_logs WHERE user_id IN (SELECT id FROM users WHERE email = %s)    ${email}
    # Delete user roles
    Execute SQL String    DELETE FROM user_roles WHERE user_id IN (SELECT id FROM users WHERE email = %s)    ${email}
    # Delete user
    Execute SQL String    DELETE FROM users WHERE email = %s    ${email}

Get User Roles From Database
    [Documentation]    Get user roles from database
    [Arguments]    ${user_id}
    ${query}=    Set Variable    SELECT r.name FROM roles r JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = %s
    ${result}=    Query    ${query}    ${user_id}
    ${roles}=    Create List
    FOR    ${row}    IN    @{result}
        Append To List    ${roles}    ${row[0]}
    END
    [Return]    ${roles}
```

### 3. Test Data Management (`resources/test_data.robot`)
```robotframework
*** Settings ***
Library    Collections
Library    String
Library    DateTime

*** Variables ***
@{VALID_EMAILS}        user1@example.com    user2@example.com    user3@example.com
@{INVALID_EMAILS}      invalid-email    @example.com    user@.com
@{WEAK_PASSWORDS}      123456    password    123    abcdef
@{STRONG_PASSWORDS}    SecurePass123!    StrongP@ss456    MyP@ssw0rd789

*** Keywords ***
Generate Unique Email
    [Documentation]    Generate unique email for testing
    ${timestamp}=    Get Current Date    result_format=%Y%m%d%H%M%S
    ${email}=    Set Variable    testuser${timestamp}@example.com
    [Return]    ${email}

Generate Strong Password
    [Documentation]    Generate strong password meeting requirements
    ${timestamp}=    Get Current Date    result_format=%s
    ${password}=    Set Variable    TestPass${timestamp}!
    [Return]    ${password}

Get Valid User Data
    [Documentation]    Get valid user data for testing
    ${email}=    Generate Unique Email
    ${password}=    Generate Strong Password
    ${user_data}=    Create Dictionary
    ...    email=${email}
    ...    password=${password}
    ...    firstName=Test
    ...    lastName=User
    ...    phoneNumber=1234567890
    [Return]    ${user_data}

Get Invalid User Data
    [Documentation]    Get invalid user data for negative testing
    [Arguments]    ${field_to_invalidate}=email
    ${user_data}=    Get Valid User Data
    
    Run Keyword If    '${field_to_invalidate}' == 'email'
    ...    Set To Dictionary    ${user_data}    email=invalid-email
    ...    ELSE IF    '${field_to_invalidate}' == 'password'
    ...    Set To Dictionary    ${user_data}    password=123
    ...    ELSE IF    '${field_to_invalidate}' == 'firstName'
    ...    Set To Dictionary    ${user_data}    firstName=
    ...    ELSE IF    '${field_to_invalidate}' == 'lastName'
    ...    Set To Dictionary    ${user_data}    lastName=
    
    [Return]    ${user_data}
```

## Test Cases

### 1. Authentication Tests (`tests/authentication/authentication_tests.robot`)
```robotframework
*** Settings ***
Suite Setup       Initialize SOAP Client
Suite Teardown    Disconnect From Database
Test Setup        Connect To Test Database
Test Teardown     Clean Up Test Data    ${TEST_EMAIL}
Resource          ../../resources/soap_keywords.robot
Resource          ../../resources/database_keywords.robot
Resource          ../../resources/test_data.robot
Resource          ../../variables/config.py

*** Variables ***
${TEST_EMAIL}      ${EMPTY}
${TEST_PASSWORD}   ${EMPTY}
${AUTH_TOKEN}      ${EMPTY}

*** Test Cases ***
Valid User Registration Should Succeed
    [Documentation]    Test successful user registration
    [Tags]    registration    positive    smoke
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${response}
    
    Should Be True    ${response['userId']} > 0
    Should Be Equal    ${response['email']}    ${TEST_EMAIL}
    
    # Verify user exists in database
    ${db_user}=    Verify User Exists In Database    ${TEST_EMAIL}
    Should Be Equal    ${db_user[1]}    ${TEST_EMAIL}
    Should Be Equal    ${db_user[2]}    ACTIVE

Duplicate User Registration Should Fail
    [Documentation]    Test that duplicate registration fails
    [Tags]    registration    negative
    # First registration
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    ${response1}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${response1}
    
    # Second registration with same email
    ${response2}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${response2}    expected_success=${False}
    Should Contain    ${response2['message']}    already exists

Invalid Email Registration Should Fail
    [Documentation]    Test registration with invalid email
    [Tags]    registration    negative    validation
    ${user_data}=    Get Invalid User Data    email
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${response}    expected_success=${False}
    Should Contain    ${response['message']}    email

Weak Password Registration Should Fail
    [Documentation]    Test registration with weak password
    [Tags]    registration    negative    validation
    ${user_data}=    Get Invalid User Data    password
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${response}    expected_success=${False}
    Should Contain    ${response['message']}    password

Valid User Authentication Should Succeed
    [Documentation]    Test successful user login
    [Tags]    authentication    positive    smoke
    # First register a user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${reg_response}
    
    # Then authenticate
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    Validate SOAP Response    ${auth_response}
    
    # Verify token
    ${token}=    Get Token From Response    ${auth_response}
    Set Suite Variable    ${AUTH_TOKEN}    ${token}
    Validate Token Format    ${token}
    
    # Verify roles
    Should Contain    ${auth_response['roles']}    USER

Invalid Credentials Authentication Should Fail
    [Documentation]    Test authentication with invalid credentials
    [Tags]    authentication    negative
    ${auth_data}=    Create Auth Request Data    nonexistent@example.com    wrongpassword
    ${response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    Validate SOAP Response    ${response}    expected_success=${False}
    Should Contain    ${response['message']}    Invalid credentials

User Logout Should Succeed
    [Documentation]    Test successful user logout
    [Tags]    authentication    positive
    # First login to get token
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${token}=    Get Token From Response    ${auth_response}
    
    # Then logout
    ${logout_data}=    Create Dictionary    token=${token}
    ${logout_response}=    Call SOAP Method    LogoutUser    ${logout_data}
    Validate SOAP Response    ${logout_response}
```

### 2. User Profile Tests (`tests/user_management/profile_tests.robot`)
```robotframework
*** Settings ***
Suite Setup       Initialize SOAP Client
Suite Teardown    Disconnect From Database
Test Setup        Connect To Test Database
Test Teardown     Clean Up Test Data    ${TEST_EMAIL}
Resource          ../../resources/soap_keywords.robot
Resource          ../../resources/database_keywords.robot
Resource          ../../resources/test_data.robot

*** Variables ***
${TEST_EMAIL}      ${EMPTY}
${TEST_PASSWORD}   ${EMPTY}
${AUTH_TOKEN}      ${EMPTY}
${USER_ID}         ${EMPTY}

*** Test Cases ***
Get Own User Profile Should Succeed
    [Documentation]    Test getting own user profile
    [Tags]    profile    positive    smoke
    # Register and authenticate user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    Set Suite Variable    ${USER_ID}    ${reg_response['userId']}
    
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${token}=    Get Token From Response    ${auth_response}
    Set Suite Variable    ${AUTH_TOKEN}    ${token}
    
    # Get profile
    ${profile_data}=    Create Dictionary    token=${token}
    ${profile_response}=    Call SOAP Method    GetUserProfile    ${profile_data}
    Validate SOAP Response    ${profile_response}
    
    # Verify profile data
    Should Be Equal    ${profile_response['user']['email']}    ${TEST_EMAIL}
    Should Be Equal    ${profile_response['user']['firstName']}    ${user_data['firstName']}
    Should Be Equal    ${profile_response['user']['lastName']}    ${user_data['lastName']}
    Should Be Equal    ${profile_response['user']['status']}    ACTIVE

Update Own User Profile Should Succeed
    [Documentation]    Test updating own user profile
    [Tags]    profile    positive
    # Register and authenticate user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${token}=    Get Token From Response    ${auth_response}
    
    # Update profile
    ${update_data}=    Create Dictionary
    ...    token=${token}
    ...    firstName=Updated
    ...    lastName=User
    ...    phoneNumber=9876543210
    ${update_response}=    Call SOAP Method    UpdateUserProfile    ${update_data}
    Validate SOAP Response    ${update_response}
    
    # Verify updated data
    Should Be Equal    ${update_response['user']['firstName']}    Updated
    Should Be Equal    ${update_response['user']['lastName']}    User
    Should Be Equal    ${update_response['user']['phoneNumber']}    9876543210

Get User Profile Without Token Should Fail
    [Documentation]    Test getting profile without authentication
    [Tags]    profile    negative    security
    ${profile_data}=    Create Dictionary
    ${response}=    Call SOAP Method    GetUserProfile    ${profile_data}
    Validate SOAP Response    ${response}    expected_success=${False}
    Should Contain    ${response['message']}    authentication

Update User Profile With Invalid Data Should Fail
    [Documentation]    Test profile update with invalid data
    [Tags]    profile    negative    validation
    # Register and authenticate user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${token}=    Get Token From Response    ${auth_response}
    
    # Try to update with invalid phone number
    ${update_data}=    Create Dictionary
    ...    token=${token}
    ...    phoneNumber=invalid-phone
    ${response}=    Call SOAP Method    UpdateUserProfile    ${update_data}
    Validate SOAP Response    ${response}    expected_success=${False}
```

### 3. Role Management Tests (`tests/role_management/role_tests.robot`)
```robotframework
*** Settings ***
Suite Setup       Initialize SOAP Client
Suite Teardown    Disconnect From Database
Test Setup        Connect To Test Database
Test Teardown     Clean Up Test Data    ${TEST_EMAIL}
Resource          ../../resources/soap_keywords.robot
Resource          ../../resources/database_keywords.robot
Resource          ../../resources/test_data.robot

*** Variables ***
${TEST_EMAIL}      ${EMPTY}
${TEST_PASSWORD}   ${EMPTY}
${ADMIN_TOKEN}     ${EMPTY}
${USER_TOKEN}      ${EMPTY}
${USER_ID}         ${EMPTY}

*** Test Cases ***
Admin Should Create New Role
    [Documentation]    Test admin creating new role
    [Tags]    role    admin    positive
    # Authenticate as admin
    ${auth_data}=    Create Auth Request Data    admin@example.com    Admin123!
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${admin_token}=    Get Token From Response    ${auth_response}
    Set Suite Variable    ${ADMIN_TOKEN}    ${admin_token}
    
    # Create new role
    ${role_data}=    Create Dictionary
    ...    token=${admin_token}
    ...    name=TEST_ROLE
    ...    description=Test role for testing
    ${role_response}=    Call SOAP Method    CreateRole    ${role_data}
    Validate SOAP Response    ${role_response}
    
    Should Be Equal    ${role_response['role']['name']}    TEST_ROLE
    Should Be Equal    ${role_response['role']['description']}    Test role for testing

Admin Should Assign Role To User
    [Documentation]    Test admin assigning role to user
    [Tags]    role    admin    positive
    # Authenticate as admin
    ${auth_data}=    Create Auth Request Data    admin@example.com    Admin123!
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${admin_token}=    Get Token From Response    ${auth_response}
    
    # Create test user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    Set Suite Variable    ${USER_ID}    ${reg_response['userId']}
    
    # Assign MANAGER role to user
    ${assign_data}=    Create Dictionary
    ...    token=${admin_token}
    ...    userId=${USER_ID}
    ...    roleId=2  # Assuming MANAGER role has ID 2
    ${assign_response}=    Call SOAP Method    AssignRole    ${assign_data}
    Validate SOAP Response    ${assign_response}
    
    # Verify role assignment in database
    ${user_roles}=    Get User Roles From Database    ${USER_ID}
    Should Contain    ${user_roles}    MANAGER

User Should View Their Roles
    [Documentation]    Test user viewing their assigned roles
    [Tags]    role    user    positive
    # Register and authenticate user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${user_token}=    Get Token From Response    ${auth_response}
    
    # Get user roles
    ${roles_data}=    Create Dictionary    token=${user_token}
    ${roles_response}=    Call SOAP Method    GetUserRoles    ${roles_data}
    Validate SOAP Response    ${roles_response}
    
    Should Contain    ${roles_response['roles']}    USER

User Should Not Create Role
    [Documentation]    Test that regular user cannot create roles
    [Tags]    role    user    negative    security
    # Register and authenticate as regular user
    ${user_data}=    Get Valid User Data
    Set Suite Variable    ${TEST_EMAIL}    ${user_data['email']}
    Set Suite Variable    ${TEST_PASSWORD}    ${user_data['password']}
    ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
    
    ${auth_data}=    Create Auth Request Data    ${TEST_EMAIL}    ${TEST_PASSWORD}
    ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    ${user_token}=    Get Token From Response    ${auth_response}
    
    # Try to create role
    ${role_data}=    Create Dictionary
    ...    token=${user_token}
    ...    name=UNAUTHORIZED_ROLE
    ...    description=This should fail
    ${response}=    Call SOAP Method    CreateRole    ${role_data}
    Validate SOAP Response    ${response}    expected_success=${False}
    Should Contain    ${response['message']}    permission
```

## Data-Driven Testing

### 1. CSV Data File (`testdata/valid_users.csv`)
```csv
email,password,firstName,lastName,phoneNumber,expected_result
test1@example.com,SecurePass123!,John,Doe,1234567890,success
test2@example.com,StrongP@ss456,Jane,Smith,0987654321,success
test3@example.com,MyP@ssw0rd789,Bob,Johnson,1122334455,success
```

### 2. Data-Driven Test Example (`tests/authentication/data_driven_registration.robot`)
```robotframework
*** Settings ***
Suite Setup       Initialize SOAP Client
Suite Teardown    Disconnect From Database
Test Setup        Connect To Test Database
Test Teardown     Clean Up Test Data    ${email}
Resource          ../../resources/soap_keywords.robot
Resource          ../../resources/database_keywords.robot
Resource          ../../resources/test_data.robot
Test Template     Register User With Data

*** Test Cases ***    email    password    firstName    lastName    phoneNumber    expected_result
Valid User 1    test1@example.com    SecurePass123!    John    Doe    1234567890    success
Valid User 2    test2@example.com    StrongP@ss456    Jane    Smith    0987654321    success
Valid User 3    test3@example.com    MyP@ssw0rd789    Bob    Johnson    1122334455    success

*** Keywords ***
Register User With Data
    [Arguments]    ${email}    ${password}    ${firstName}    ${lastName}    ${phoneNumber}    ${expected_result}
    
    # Generate unique email by appending timestamp
    ${timestamp}=    Get Current Date    result_format=%s
    ${unique_email}=    Set Variable    ${timestamp}_${email}
    
    ${user_data}=    Create User Request Data    ${unique_email}    ${password}    ${firstName}    ${lastName}    ${phoneNumber}
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    
    Run Keyword If    '${expected_result}' == 'success'
    ...    Validate SOAP Response    ${response}
    ...    ELSE
    ...    Validate SOAP Response    ${response}    expected_success=${False}
```

## Performance Testing

### Load Test Example (`tests/performance/load_test.robot`)
```robotframework
*** Settings ***
Suite Setup       Initialize SOAP Client
Resource          ../../resources/soap_keywords.robot
Resource          ../../resources/test_data.robot
Library           DateTime

*** Variables ***
${CONCURRENT_USERS}    10
${ITERATIONS_PER_USER}    5
${MAX_RESPONSE_TIME}    2.0

*** Test Cases ***
Authentication Load Test
    [Documentation]    Test authentication performance under load
    [Tags]    performance    load    authentication
    ${start_time}=    Get Current Date
    
    # Create multiple threads for concurrent users
    FOR    ${user_index}    IN RANGE    ${CONCURRENT_USERS}
        Run Keyword In Parallel    Simulate User Authentication    ${user_index}
    END
    
    ${end_time}=    Get Current Date
    ${total_duration}=    Subtract Date From Date    ${end_time}    ${start_time}
    Log    Total test duration: ${total_duration} seconds
    Should Be True    ${total_duration} < ${CONCURRENT_USERS} * ${ITERATIONS_PER_USER} * ${MAX_RESPONSE_TIME}

*** Keywords ***
Simulate User Authentication
    [Arguments]    ${user_index}
    
    FOR    ${iteration}    IN RANGE    ${ITERATIONS_PER_USER}
        ${user_data}=    Get Valid User Data
        ${reg_response}=    Call SOAP Method    RegisterUser    ${user_data}
        
        ${auth_data}=    Create Auth Request Data    ${user_data['email']}    ${user_data['password']}
        ${start_time}=    Get Current Date
        ${auth_response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
        ${end_time}=    Get Current Date
        
        ${response_time}=    Subtract Date From Date    ${end_time}    ${start_time}
        Should Be True    ${response_time} < ${MAX_RESPONSE_TIME}
        Validate SOAP Response    ${auth_response}
        
        Clean Up Test Data    ${user_data['email']}
    END
```

## Security Testing

### Security Test Example (`tests/security/security_tests.robot`)
```robotframework
*** Settings ***
Suite Setup       Initialize SOAP Client
Resource          ../../resources/soap_keywords.robot
Resource          ../../resources/test_data.robot

*** Test Cases ***
SQL Injection Attempt Should Fail
    [Documentation]    Test SQL injection protection
    [Tags]    security    sql-injection
    ${malicious_email}=    Set Variable    ' OR '1'='1
    ${user_data}=    Create User Request Data    ${malicious_email}    SecurePass123!    Test    User
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    Validate SOAP Response    ${response}    expected_success=${False}

XSS Attempt Should Fail
    [Documentation]    Test XSS protection
    [Tags]    security    xss
    ${malicious_name}=    Set Variable    <script>alert('xss')</script>
    ${user_data}=    Create User Request Data    test@example.com    SecurePass123!    ${malicious_name}    User
    ${response}=    Call SOAP Method    RegisterUser    ${user_data}
    # Should either succeed with sanitized data or fail validation
    Run Keyword If    ${response['success']}
    ...    Should Not Contain    ${response['message']}    <script>
    ...    ELSE
    ...    Should Contain    ${response['message']}    invalid

Brute Force Protection Should Work
    [Documentation]    Test rate limiting for authentication
    [Tags]    security    rate-limiting
    ${auth_data}=    Create Auth Request Data    test@example.com    wrongpassword
    
    # Try multiple failed attempts
    FOR    ${attempt}    IN RANGE    10
        ${response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
        Validate SOAP Response    ${response}    expected_success=${False}
    END
    
    # Should be rate limited now
    ${response}=    Call SOAP Method    AuthenticateUser    ${auth_data}
    Should Contain    ${response['message']}    rate limit
```

## Configuration and Variables

### Configuration File (`variables/config.py`)
```python
# SOAP API Configuration
SOAP_ENDPOINT = "http://localhost:8000/soap"
WSDL_URL = "http://localhost:8000/wsdl"

# Database Configuration
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "user_management_test"
DB_USER = "test_user"
DB_PASSWORD = "test_password"

# Test Configuration
DEFAULT_TIMEOUT = 30
MAX_RESPONSE_TIME = 2.0
CONCURRENT_USERS = 10
ITERATIONS_PER_USER = 5

# Test Users
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"

# Test Data
VALID_EMAIL_DOMAINS = ["example.com", "test.com"]
INVALID_EMAILS = ["invalid-email", "@example.com", "user@.com"]
WEAK_PASSWORDS = ["123456", "password", "123", "abcdef"]
STRONG_PASSWORDS = ["SecurePass123!", "StrongP@ss456", "MyP@ssw0rd789"]
```

## Running Tests

### Command Line Execution
```bash
# Run all tests
robot robot-tests/

# Run specific test suite
robot robot-tests/tests/authentication/

# Run tests with specific tags
robot --include smoke robot-tests/
robot --include regression --exclude slow robot-tests/

# Run with custom output directory
robot --outputdir results/$(date +%Y%m%d_%H%M%S) robot-tests/

# Generate detailed reports
robot --loglevel DEBUG robot-tests/

# Run with variables
robot --variable SOAP_ENDPOINT:http://localhost:8001/soap robot-tests/
```

### Continuous Integration
```yaml
# GitHub Actions example
name: Robot Framework Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run Robot Framework tests
      run: |
        robot --outputdir results --include smoke robot-tests/
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: robot-framework-results
        path: results/
```

## Best Practices

### 1. Test Organization
- Group related tests in logical suites
- Use descriptive test case names
- Tag tests for easy filtering (smoke, regression, security, etc.)
- Separate test data from test logic

### 2. Error Handling
- Use proper error handling keywords
- Validate responses consistently
- Include meaningful assertions
- Log detailed information for debugging

### 3. Data Management
- Use unique test data to avoid conflicts
- Clean up test data after each test
- Use data-driven testing for similar scenarios
- Parameterize tests with variables

### 4. Performance Considerations
- Implement proper wait strategies
- Use timeouts for network operations
- Monitor test execution times
- Optimize database operations

### 5. Maintenance
- Keep test code DRY (Don't Repeat Yourself)
- Use reusable keywords and libraries
- Regularly update test data
- Document complex test scenarios

This comprehensive Robot Framework testing guide provides everything needed to thoroughly test the Enhanced User Management System SOAP API, ensuring robust validation of all functionality, security, and performance requirements.