# SOAP API Reference

## Table of Contents
1. [Overview](#overview)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management Endpoints](#user-management-endpoints)
4. [Role Management Endpoints](#role-management-endpoints)
5. [Permission Management Endpoints](#permission-management-endpoints)
6. [Password Management Endpoints](#password-management-endpoints)
7. [Audit Endpoints](#audit-endpoints)
8. [Data Types Reference](#data-types-reference)
9. [Error Codes Reference](#error-codes-reference)

## Overview

This API reference provides detailed parameter descriptions, data types, validation rules, and examples for all SOAP API endpoints in the Enhanced User Management System.

### Base URLs
- **Development**: `http://localhost:8000/soap`
- **Production**: `https://api.example.com/soap`
- **WSDL**: `http://localhost:8000/wsdl`

### Common Headers
```
Content-Type: text/xml; charset=utf-8
SOAPAction: http://example.com/usermanagement/{OperationName}
```

### Authentication
Most endpoints require a JWT token obtained through the `AuthenticateUser` operation. Include the token in the request body as specified in each operation.

---

## Authentication Endpoints

### 1. RegisterUser

Registers a new user in the system.

**Operation**: `RegisterUser`

**SOAP Action**: `http://example.com/usermanagement/RegisterUser`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| email | String | Yes | User's email address | Must be valid email format, unique |
| password | String | Yes | User's password | Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char |
| firstName | String | Yes | User's first name | Max 100 characters, letters only |
| lastName | String | Yes | User's last name | Max 100 characters, letters only |
| phoneNumber | String | No | User's phone number | Max 20 characters, international format |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| userId | Integer | Unique identifier for the newly created user |
| email | String | Email address of the registered user |
| success | Boolean | Registration success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:RegisterUserRequest>
    <tns:email>john.doe@example.com</tns:email>
    <tns:password>SecurePass123!</tns:password>
    <tns:firstName>John</tns:firstName>
    <tns:lastName>Doe</tns:lastName>
    <tns:phoneNumber>1234567890</tns:phoneNumber>
</tns:RegisterUserRequest>
```

#### Example Response
```xml
<tns:RegisterUserResponse>
    <tns:userId>123</tns:userId>
    <tns:email>john.doe@example.com</tns:email>
    <tns:success>true</tns:success>
    <tns:message>User registered successfully</tns:message>
    <tns:timestamp>2024-01-01T12:00:00Z</tns:timestamp>
</tns:RegisterUserResponse>
```

---

### 2. AuthenticateUser

Authenticates a user and returns a JWT token.

**Operation**: `AuthenticateUser`

**SOAP Action**: `http://example.com/usermanagement/AuthenticateUser`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| email | String | Yes | User's email address | Must be valid email format |
| password | String | Yes | User's password | Must match stored password |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| token | String | JWT authentication token (expires in 1 hour) |
| userId | Integer | User's unique identifier |
| roles | ArrayOfString | List of user's role names |
| expiresIn | Integer | Token expiration time in seconds |
| success | Boolean | Authentication success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:AuthenticateUserRequest>
    <tns:email>john.doe@example.com</tns:email>
    <tns:password>SecurePass123!</tns:password>
</tns:AuthenticateUserRequest>
```

#### Example Response
```xml
<tns:AuthenticateUserResponse>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>123</tns:userId>
    <tns:roles>
        <tns:string>USER</tns:string>
    </tns:roles>
    <tns:expiresIn>3600</tns:expiresIn>
    <tns:success>true</tns:success>
    <tns:message>Authentication successful</tns:message>
    <tns:timestamp>2024-01-01T12:05:00Z</tns:timestamp>
</tns:AuthenticateUserResponse>
```

---

### 3. LogoutUser

Logs out a user and invalidates their token.

**Operation**: `LogoutUser`

**SOAP Action**: `http://example.com/usermanagement/LogoutUser`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Logout success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:LogoutUserRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
</tns:LogoutUserRequest>
```

#### Example Response
```xml
<tns:LogoutUserResponse>
    <tns:success>true</tns:success>
    <tns:message>Logout successful</tns:message>
    <tns:timestamp>2024-01-01T12:10:00Z</tns:timestamp>
</tns:LogoutUserResponse>
```

---

## User Management Endpoints

### 4. GetUserProfile

Retrieves user profile information.

**Operation**: `GetUserProfile`

**SOAP Action**: `http://example.com/usermanagement/GetUserProfile`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| userId | Integer | No | Target user ID | If not provided, returns current user's profile |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| user | User | User profile object (see User data type) |
| success | Boolean | Operation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:GetUserProfileRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>123</tns:userId>
</tns:GetUserProfileRequest>
```

#### Example Response
```xml
<tns:GetUserProfileResponse>
    <tns:user>
        <tns:id>123</tns:id>
        <tns:email>john.doe@example.com</tns:email>
        <tns:firstName>John</tns:firstName>
        <tns:lastName>Doe</tns:lastName>
        <tns:phoneNumber>1234567890</tns:phoneNumber>
        <tns:profilePictureUrl>https://example.com/profile.jpg</tns:profilePictureUrl>
        <tns:status>ACTIVE</tns:status>
        <tns:createdAt>2024-01-01T10:00:00Z</tns:createdAt>
        <tns:updatedAt>2024-01-01T11:00:00Z</tns:updatedAt>
        <tns:lastLogin>2024-01-01T12:00:00Z</tns:lastLogin>
    </tns:user>
    <tns:success>true</tns:success>
    <tns:message>Profile retrieved successfully</tns:message>
    <tns:timestamp>2024-01-01T12:15:00Z</tns:timestamp>
</tns:GetUserProfileResponse>
```

---

### 5. UpdateUserProfile

Updates user profile information.

**Operation**: `UpdateUserProfile`

**SOAP Action**: `http://example.com/usermanagement/UpdateUserProfile`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| userId | Integer | No | Target user ID | If not provided, updates current user's profile |
| firstName | String | No | New first name | Max 100 characters, letters only |
| lastName | String | No | New last name | Max 100 characters, letters only |
| phoneNumber | String | No | New phone number | Max 20 characters, international format |
| profilePictureUrl | String | No | New profile picture URL | Valid URL format |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| user | User | Updated user profile object |
| success | Boolean | Update success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:UpdateUserProfileRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>123</tns:userId>
    <tns:firstName>Johnathan</tns:firstName>
    <tns:lastName>Smith</tns:lastName>
    <tns:phoneNumber>9876543210</tns:phoneNumber>
</tns:UpdateUserProfileRequest>
```

#### Example Response
```xml
<tns:UpdateUserProfileResponse>
    <tns:user>
        <tns:id>123</tns:id>
        <tns:email>john.doe@example.com</tns:email>
        <tns:firstName>Johnathan</tns:firstName>
        <tns:lastName>Smith</tns:lastName>
        <tns:phoneNumber>9876543210</tns:phoneNumber>
        <tns:status>ACTIVE</tns:status>
        <tns:createdAt>2024-01-01T10:00:00Z</tns:createdAt>
        <tns:updatedAt>2024-01-01T12:20:00Z</tns:updatedAt>
    </tns:user>
    <tns:success>true</tns:success>
    <tns:message>Profile updated successfully</tns:message>
    <tns:timestamp>2024-01-01T12:20:00Z</tns:timestamp>
</tns:UpdateUserProfileResponse>
```

---

### 6. GetAllUsers

Retrieves all users with pagination support.

**Operation**: `GetAllUsers`

**SOAP Action**: `http://example.com/usermanagement/GetAllUsers`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| page | Integer | No | Page number (default: 1) | Must be >= 1 |
| pageSize | Integer | No | Items per page (default: 20) | Range: 1-100 |
| status | String | No | Filter by user status | Values: ACTIVE, INACTIVE, SUSPENDED |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| users | ArrayOfUser | Array of user objects |
| totalCount | Integer | Total number of users matching criteria |
| page | Integer | Current page number |
| pageSize | Integer | Number of items per page |
| success | Boolean | Operation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:GetAllUsersRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:page>1</tns:page>
    <tns:pageSize>10</tns:pageSize>
    <tns:status>ACTIVE</tns:status>
</tns:GetAllUsersRequest>
```

#### Example Response
```xml
<tns:GetAllUsersResponse>
    <tns:users>
        <tns:user>
            <tns:id>123</tns:id>
            <tns:email>john.doe@example.com</tns:email>
            <tns:firstName>John</tns:firstName>
            <tns:lastName>Doe</tns:lastName>
            <tns:status>ACTIVE</tns:status>
        </tns:user>
        <tns:user>
            <tns:id>124</tns:id>
            <tns:email>jane.smith@example.com</tns:email>
            <tns:firstName>Jane</tns:firstName>
            <tns:lastName>Smith</tns:lastName>
            <tns:status>ACTIVE</tns:status>
        </tns:user>
    </tns:users>
    <tns:totalCount>25</tns:totalCount>
    <tns:page>1</tns:page>
    <tns:pageSize>10</tns:pageSize>
    <tns:success>true</tns:success>
    <tns:message>Users retrieved successfully</tns:message>
    <tns:timestamp>2024-01-01T12:25:00Z</tns:timestamp>
</tns:GetAllUsersResponse>
```

---

### 7. DeactivateUser

Deactivates a user account.

**Operation**: `DeactivateUser`

**SOAP Action**: `http://example.com/usermanagement/DeactivateUser`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| userId | Integer | Yes | Target user ID to deactivate | Must be valid user ID |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Deactivation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:DeactivateUserRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>124</tns:userId>
</tns:DeactivateUserRequest>
```

#### Example Response
```xml
<tns:DeactivateUserResponse>
    <tns:success>true</tns:success>
    <tns:message>User deactivated successfully</tns:message>
    <tns:timestamp>2024-01-01T12:30:00Z</tns:timestamp>
</tns:DeactivateUserResponse>
```

---

## Role Management Endpoints

### 8. CreateRole

Creates a new role in the system.

**Operation**: `CreateRole`

**SOAP Action**: `http://example.com/usermanagement/CreateRole`

**Required Permission**: `ROLE_CREATE`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| name | String | Yes | Role name | Max 50 characters, unique, uppercase |
| description | String | No | Role description | Max 500 characters |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| role | Role | Created role object |
| success | Boolean | Creation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:CreateRoleRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:name>MANAGER</tns:name>
    <tns:description>Manager with limited administrative access</tns:description>
</tns:CreateRoleRequest>
```

#### Example Response
```xml
<tns:CreateRoleResponse>
    <tns:role>
        <tns:id>5</tns:id>
        <tns:name>MANAGER</tns:name>
        <tns:description>Manager with limited administrative access</tns:description>
        <tns:createdAt>2024-01-01T12:35:00Z</tns:createdAt>
        <tns:updatedAt>2024-01-01T12:35:00Z</tns:updatedAt>
    </tns:role>
    <tns:success>true</tns:success>
    <tns:message>Role created successfully</tns:message>
    <tns:timestamp>2024-01-01T12:35:00Z</tns:timestamp>
</tns:CreateRoleResponse>
```

---

### 9. AssignRole

Assigns a role to a user.

**Operation**: `AssignRole`

**SOAP Action**: `http://example.com/usermanagement/AssignRole`

**Required Permission**: `ROLE_ASSIGN`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| userId | Integer | Yes | Target user ID | Must be valid user ID |
| roleId | Integer | Yes | Role ID to assign | Must be valid role ID |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Assignment success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:AssignRoleRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>123</tns:userId>
    <tns:roleId>5</tns:roleId>
</tns:AssignRoleRequest>
```

#### Example Response
```xml
<tns:AssignRoleResponse>
    <tns:success>true</tns:success>
    <tns:message>Role assigned successfully</tns:message>
    <tns:timestamp>2024-01-01T12:40:00Z</tns:timestamp>
</tns:AssignRoleResponse>
```

---

### 10. GetUserRoles

Retrieves roles assigned to a user.

**Operation**: `GetUserRoles`

**SOAP Action**: `http://example.com/usermanagement/GetUserRoles`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| userId | Integer | No | Target user ID | If not provided, returns current user's roles |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| roles | ArrayOfRole | Array of role objects |
| success | Boolean | Operation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:GetUserRolesRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>123</tns:userId>
</tns:GetUserRolesRequest>
```

#### Example Response
```xml
<tns:GetUserRolesResponse>
    <tns:roles>
        <tns:role>
            <tns:id>1</tns:id>
            <tns:name>USER</tns:name>
            <tns:description>Regular user with basic access</tns:description>
            <tns:createdAt>2024-01-01T09:00:00Z</tns:createdAt>
            <tns:updatedAt>2024-01-01T09:00:00Z</tns:updatedAt>
        </tns:role>
        <tns:role>
            <tns:id>5</tns:id>
            <tns:name>MANAGER</tns:name>
            <tns:description>Manager with limited administrative access</tns:description>
            <tns:createdAt>2024-01-01T12:35:00Z</tns:createdAt>
            <tns:updatedAt>2024-01-01T12:35:00Z</tns:updatedAt>
        </tns:role>
    </tns:roles>
    <tns:success>true</tns:success>
    <tns:message>User roles retrieved successfully</tns:message>
    <tns:timestamp>2024-01-01T12:45:00Z</tns:timestamp>
</tns:GetUserRolesResponse>
```

---

## Permission Management Endpoints

### 11. CreatePermission

Creates a new permission in the system.

**Operation**: `CreatePermission`

**SOAP Action**: `http://example.com/usermanagement/CreatePermission`

**Required Permission**: `PERMISSION_CREATE`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| name | String | Yes | Permission name | Max 100 characters, unique |
| description | String | No | Permission description | Max 500 characters |
| module | String | Yes | Module name | Values: USER, PROFILE, ROLE, AUDIT |
| action | String | Yes | Action name | Values: CREATE, READ, UPDATE, DELETE, LIST, ASSIGN |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| permission | Permission | Created permission object |
| success | Boolean | Creation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:CreatePermissionRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:name>USER_APPROVE</tns:name>
    <tns:description>Approve user registrations</tns:description>
    <tns:module>USER</tns:module>
    <tns:action>APPROVE</tns:action>
</tns:CreatePermissionRequest>
```

#### Example Response
```xml
<tns:CreatePermissionResponse>
    <tns:permission>
        <tns:id>25</tns:id>
        <tns:name>USER_APPROVE</tns:name>
        <tns:description>Approve user registrations</tns:description>
        <tns:module>USER</tns:module>
        <tns:action>APPROVE</tns:action>
        <tns:createdAt>2024-01-01T12:50:00Z</tns:createdAt>
    </tns:permission>
    <tns:success>true</tns:success>
    <tns:message>Permission created successfully</tns:message>
    <tns:timestamp>2024-01-01T12:50:00Z</tns:timestamp>
</tns:CreatePermissionResponse>
```

---

### 12. AssignPermissionToRole

Assigns a permission to a role.

**Operation**: `AssignPermissionToRole`

**SOAP Action**: `http://example.com/usermanagement/AssignPermissionToRole`

**Required Permission**: `PERMISSION_ASSIGN`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| roleId | Integer | Yes | Target role ID | Must be valid role ID |
| permissionId | Integer | Yes | Permission ID to assign | Must be valid permission ID |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Assignment success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:AssignPermissionToRoleRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:roleId>5</tns:roleId>
    <tns:permissionId>25</tns:permissionId>
</tns:AssignPermissionToRoleRequest>
```

#### Example Response
```xml
<tns:AssignPermissionToRoleResponse>
    <tns:success>true</tns:success>
    <tns:message>Permission assigned to role successfully</tns:message>
    <tns:timestamp>2024-01-01T12:55:00Z</tns:timestamp>
</tns:AssignPermissionToRoleResponse>
```

---

## Password Management Endpoints

### 13. RequestPasswordReset

Requests a password reset for a user.

**Operation**: `RequestPasswordReset`

**SOAP Action**: `http://example.com/usermanagement/RequestPasswordReset`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| email | String | Yes | User's email address | Must be valid email format |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Request success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:RequestPasswordResetRequest>
    <tns:email>john.doe@example.com</tns:email>
</tns:RequestPasswordResetRequest>
```

#### Example Response
```xml
<tns:RequestPasswordResetResponse>
    <tns:success>true</tns:success>
    <tns:message>Password reset email sent</tns:message>
    <tns:timestamp>2024-01-01T13:00:00Z</tns:timestamp>
</tns:RequestPasswordResetResponse>
```

---

### 14. ResetPassword

Resets a user's password using a reset token.

**Operation**: `ResetPassword`

**SOAP Action**: `http://example.com/usermanagement/ResetPassword`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| resetToken | String | Yes | Password reset token | Must be valid and not expired |
| newPassword | String | Yes | New password | Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Reset success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:ResetPasswordRequest>
    <tns:resetToken>abc123def456...</tns:resetToken>
    <tns:newPassword>NewSecurePass456!</tns:newPassword>
</tns:ResetPasswordRequest>
```

#### Example Response
```xml
<tns:ResetPasswordResponse>
    <tns:success>true</tns:success>
    <tns:message>Password reset successfully</tns:message>
    <tns:timestamp>2024-01-01T13:05:00Z</tns:timestamp>
</tns:ResetPasswordResponse>
```

---

### 15. ChangePassword

Changes a user's password (requires current password).

**Operation**: `ChangePassword`

**SOAP Action**: `http://example.com/usermanagement/ChangePassword`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| currentPassword | String | Yes | Current password | Must match stored password |
| newPassword | String | Yes | New password | Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Change success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:ChangePasswordRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:currentPassword>SecurePass123!</tns:currentPassword>
    <tns:newPassword>NewSecurePass456!</tns:newPassword>
</tns:ChangePasswordRequest>
```

#### Example Response
```xml
<tns:ChangePasswordResponse>
    <tns:success>true</tns:success>
    <tns:message>Password changed successfully</tns:message>
    <tns:timestamp>2024-01-01T13:10:00Z</tns:timestamp>
</tns:ChangePasswordResponse>
```

---

## Audit Endpoints

### 16. GetAuditLogs

Retrieves audit logs with filtering options.

**Operation**: `GetAuditLogs`

**SOAP Action**: `http://example.com/usermanagement/GetAuditLogs`

**Required Permission**: `AUDIT_READ`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| startDate | DateTime | No | Start date for filtering | ISO 8601 format |
| endDate | DateTime | No | End date for filtering | ISO 8601 format |
| userId | Integer | No | Filter by specific user ID | Must be valid user ID |
| action | String | No | Filter by action type | See audit actions list |
| resourceType | String | No | Filter by resource type | Values: USER, ROLE, PERMISSION |
| page | Integer | No | Page number (default: 1) | Must be >= 1 |
| pageSize | Integer | No | Items per page (default: 20) | Range: 1-100 |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| auditLogs | ArrayOfAuditLog | Array of audit log objects |
| totalCount | Integer | Total number of logs matching criteria |
| page | Integer | Current page number |
| pageSize | Integer | Number of items per page |
| success | Boolean | Operation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:GetAuditLogsRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:startDate>2024-01-01T00:00:00Z</tns:startDate>
    <tns:endDate>2024-01-01T23:59:59Z</tns:endDate>
    <tns:action>USER_LOGIN_SUCCESS</tns:action>
    <tns:page>1</tns:page>
    <tns:pageSize>10</tns:pageSize>
</tns:GetAuditLogsRequest>
```

#### Example Response
```xml
<tns:GetAuditLogsResponse>
    <tns:auditLogs>
        <tns:auditLog>
            <tns:id>1001</tns:id>
            <tns:userId>123</tns:userId>
            <tns:action>USER_LOGIN_SUCCESS</tns:action>
            <tns:resourceType>USER</tns:resourceType>
            <tns:resourceId>123</tns:resourceId>
            <tns:ipAddress>192.168.1.100</tns:ipAddress>
            <tns:userAgent>Mozilla/5.0...</tns:userAgent>
            <tns:createdAt>2024-01-01T12:00:00Z</tns:createdAt>
        </tns:auditLog>
        <tns:auditLog>
            <tns:id>1002</tns:id>
            <tns:userId>124</tns:userId>
            <tns:action>USER_LOGIN_SUCCESS</tns:action>
            <tns:resourceType>USER</tns:resourceType>
            <tns:resourceId>124</tns:resourceId>
            <tns:ipAddress>192.168.1.101</tns:ipAddress>
            <tns:userAgent>Mozilla/5.0...</tns:userAgent>
            <tns:createdAt>2024-01-01T12:05:00Z</tns:createdAt>
        </tns:auditLog>
    </tns:auditLogs>
    <tns:totalCount>15</tns:totalCount>
    <tns:page>1</tns:page>
    <tns:pageSize>10</tns:pageSize>
    <tns:success>true</tns:success>
    <tns:message>Audit logs retrieved successfully</tns:message>
    <tns:timestamp>2024-01-01T13:15:00Z</tns:timestamp>
</tns:GetAuditLogsResponse>
```

---

### 17. GetUserAuditLogs

Retrieves audit logs for a specific user.

**Operation**: `GetUserAuditLogs`

**SOAP Action**: `http://example.com/usermanagement/GetUserAuditLogs`

#### Request Parameters

| Parameter | Type | Required | Description | Validation Rules |
|-----------|------|----------|-------------|------------------|
| token | String | Yes | Valid JWT authentication token | Must be valid and not expired |
| userId | Integer | No | Target user ID | If not provided, returns current user's logs |
| startDate | DateTime | No | Start date for filtering | ISO 8601 format |
| endDate | DateTime | No | End date for filtering | ISO 8601 format |
| page | Integer | No | Page number (default: 1) | Must be >= 1 |
| pageSize | Integer | No | Items per page (default: 20) | Range: 1-100 |

#### Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| auditLogs | ArrayOfAuditLog | Array of audit log objects |
| totalCount | Integer | Total number of logs matching criteria |
| page | Integer | Current page number |
| pageSize | Integer | Number of items per page |
| success | Boolean | Operation success status |
| message | String | Success or error message |
| timestamp | DateTime | Response timestamp in ISO 8601 format |

#### Example Request
```xml
<tns:GetUserAuditLogsRequest>
    <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
    <tns:userId>123</tns:userId>
    <tns:startDate>2024-01-01T00:00:00Z</tns:startDate>
    <tns:endDate>2024-01-01T23:59:59Z</tns:endDate>
    <tns:page>1</tns:page>
    <tns:pageSize>10</tns:pageSize>
</tns:GetUserAuditLogsRequest>
```

#### Example Response
```xml
<tns:GetUserAuditLogsResponse>
    <tns:auditLogs>
        <tns:auditLog>
            <tns:id>1001</tns:id>
            <tns:userId>123</tns:userId>
            <tns:action>USER_LOGIN_SUCCESS</tns:action>
            <tns:resourceType>USER</tns:resourceType>
            <tns:resourceId>123</tns:resourceId>
            <tns:ipAddress>192.168.1.100</tns:ipAddress>
            <tns:userAgent>Mozilla/5.0...</tns:userAgent>
            <tns:createdAt>2024-01-01T12:00:00Z</tns:createdAt>
        </tns:auditLog>
        <tns:auditLog>
            <tns:id>1003</tns:id>
            <tns:userId>123</tns:userId>
            <tns:action>USER_PROFILE_UPDATED</tns:action>
            <tns:resourceType>USER</tns:resourceType>
            <tns:resourceId>123</tns:resourceId>
            <tns:oldValues>{"firstName":"John"}</tns:oldValues>
            <tns:newValues>{"firstName":"Johnathan"}</tns:newValues>
            <tns:ipAddress>192.168.1.100</tns:ipAddress>
            <tns:userAgent>Mozilla/5.0...</tns:userAgent>
            <tns:createdAt>2024-01-01T12:20:00Z</tns:createdAt>
        </tns:auditLog>
    </tns:auditLogs>
    <tns:totalCount>5</tns:totalCount>
    <tns:page>1</tns:page>
    <tns:pageSize>10</tns:pageSize>
    <tns:success>true</tns:success>
    <tns:message>User audit logs retrieved successfully</tns:message>
    <tns:timestamp>2024-01-01T13:20:00Z</tns:timestamp>
</tns:GetUserAuditLogsResponse>
```

---

## Data Types Reference

### User

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Yes | Unique user identifier |
| email | String | Yes | User's email address |
| firstName | String | Yes | User's first name |
| lastName | String | Yes | User's last name |
| phoneNumber | String | No | User's phone number |
| profilePictureUrl | String | No | URL to user's profile picture |
| status | String | Yes | User status (ACTIVE, INACTIVE, SUSPENDED) |
| createdAt | DateTime | Yes | Account creation timestamp |
| updatedAt | DateTime | Yes | Last update timestamp |
| lastLogin | DateTime | No | Last login timestamp |

### Role

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Yes | Unique role identifier |
| name | String | Yes | Role name |
| description | String | No | Role description |
| createdAt | DateTime | Yes | Role creation timestamp |
| updatedAt | DateTime | Yes | Last update timestamp |

### Permission

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Yes | Unique permission identifier |
| name | String | Yes | Permission name |
| description | String | No | Permission description |
| module | String | Yes | Permission module (USER, PROFILE, ROLE, AUDIT) |
| action | String | Yes | Permission action (CREATE, READ, UPDATE, DELETE, LIST, ASSIGN) |
| createdAt | DateTime | Yes | Permission creation timestamp |

### AuditLog

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Yes | Unique audit log identifier |
| userId | Integer | No | User who performed the action |
| action | String | Yes | Action performed |
| resourceType | String | Yes | Type of resource affected |
| resourceId | Integer | No | ID of resource affected |
| oldValues | String | No | Previous values (JSON string) |
| newValues | String | No | New values (JSON string) |
| ipAddress | String | No | IP address of the request |
| userAgent | String | No | User agent of the request |
| createdAt | DateTime | Yes | Audit log creation timestamp |

---

## Error Codes Reference

### Authentication Errors

| Code | Message | Description | HTTP Status |
|------|---------|-------------|-------------|
| AUTH_001 | Invalid credentials | Email or password is incorrect | 401 |
| AUTH_002 | Token expired | Authentication token has expired | 401 |
| AUTH_003 | Insufficient permissions | User lacks required permission | 403 |

### User Errors

| Code | Message | Description | HTTP Status |
|------|---------|-------------|-------------|
| USER_001 | User not found | Specified user does not exist | 404 |
| USER_002 | User already exists | Email address already registered | 409 |
| USER_003 | Invalid user status | User status is not valid | 400 |

### Role Errors

| Code | Message | Description | HTTP Status |
|------|---------|-------------|-------------|
| ROLE_001 | Role not found | Specified role does not exist | 404 |
| ROLE_002 | Role already assigned | Role is already assigned to user | 409 |

### Permission Errors

| Code | Message | Description | HTTP Status |
|------|---------|-------------|-------------|
| PERM_001 | Permission not found | Specified permission does not exist | 404 |
| PERM_002 | Invalid permission assignment | Permission cannot be assigned to role | 400 |

### Validation Errors

| Code | Message | Description | HTTP Status |
|------|---------|-------------|-------------|
| VALID_001 | Invalid input format | Request data format is invalid | 400 |
| VALID_002 | Required field missing | Required field is not provided | 400 |

### System Errors

| Code | Message | Description | HTTP Status |
|------|---------|-------------|-------------|
| SYS_001 | Internal server error | Unexpected server error occurred | 500 |
| SYS_002 | Database connection error | Unable to connect to database | 500 |

---

## Rate Limiting

### Rate Limits by Endpoint

| Endpoint Category | Limit | Time Window |
|------------------|--------|-------------|
| Authentication | 5 requests | 1 minute per IP |
| User Management | 100 requests | 1 minute per user |
| Role Management | 50 requests | 1 minute per user |
| Permission Management | 50 requests | 1 minute per user |
| Password Management | 10 requests | 1 minute per IP |
| Audit Logs | 200 requests | 1 minute per user |

### Rate Limit Response Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Security Guidelines

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*)

### Token Security

- JWT tokens expire after 1 hour
- Use HTTPS in production environments
- Store tokens securely on client side
- Invalidate tokens on logout

### Input Validation

- All inputs are validated against XSS attacks
- SQL injection protection is implemented
- XML/XXE attack prevention is enabled
- Request size limits are enforced

---

## Testing Guidelines

### Robot Framework Testing

This API is designed for Robot Framework testing. See the [Robot Framework Testing Guide](Robot_Framework_Testing_Guide.md) for detailed testing examples and best practices.

### Test Data

Use the following test data for consistent testing:

```
Test Email: test@example.com
Test Password: SecurePass123!
Test User ID: 1
Test Role ID: 1
Test Permission ID: 1
```

### Error Testing

Test error scenarios using:

- Invalid credentials
- Expired tokens
- Missing required fields
- Invalid data formats
- Unauthorized access attempts

---

## Support

For technical support or questions about the API:

1. Check this documentation first
2. Review the error codes reference
3. Consult the troubleshooting guide
4. Contact the development team

---

*This API reference is part of the Enhanced User Management System documentation suite, designed specifically for Robot Framework testing and training purposes.*