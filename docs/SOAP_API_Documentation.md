# SOAP API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [User Management](#user-management)
4. [Role Management](#role-management)
5. [Permission Management](#permission-management)
6. [Password Management](#password-management)
7. [Audit Logs](#audit-logs)
8. [Error Handling](#error-handling)
9. [Data Types](#data-types)

## Overview

The Enhanced User Management System provides a comprehensive SOAP API for user authentication, authorization, profile management, role-based access control, and audit logging. This API is designed specifically for Robot Framework testing and training purposes.

### Base URL
- **Development**: `http://localhost:8000/soap`
- **Production**: `https://api.example.com/soap`
- **WSDL**: `http://localhost:8000/wsdl`

### Authentication
Most endpoints require a valid authentication token obtained through the `AuthenticateUser` operation. Include the token in the request body as specified in each operation.

---

## Authentication

### 1. RegisterUser

Registers a new user in the system.

**Endpoint**: `RegisterUser`

**Request Parameters**:
- `email` (String, Required): User's email address
- `password` (String, Required): User's password (must meet complexity requirements)
- `firstName` (String, Required): User's first name
- `lastName` (String, Required): User's last name
- `phoneNumber` (String, Optional): User's phone number

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:RegisterUserRequest>
            <tns:email>john.doe@example.com</tns:email>
            <tns:password>SecurePass123!</tns:password>
            <tns:firstName>John</tns:firstName>
            <tns:lastName>Doe</tns:lastName>
            <tns:phoneNumber>1234567890</tns:phoneNumber>
        </tns:RegisterUserRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:RegisterUserResponse>
            <tns:userId>123</tns:userId>
            <tns:email>john.doe@example.com</tns:email>
            <tns:success>true</tns:success>
            <tns:message>User registered successfully</tns:message>
            <tns:timestamp>2024-01-01T12:00:00Z</tns:timestamp>
        </tns:RegisterUserResponse>
    </soap:Body>
</soap:Envelope>
```

---

### 2. AuthenticateUser

Authenticates a user and returns a JWT token.

**Endpoint**: `AuthenticateUser`

**Request Parameters**:
- `email` (String, Required): User's email address
- `password` (String, Required): User's password

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:AuthenticateUserRequest>
            <tns:email>john.doe@example.com</tns:email>
            <tns:password>SecurePass123!</tns:password>
        </tns:AuthenticateUserRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 3. LogoutUser

Logs out a user and invalidates their token.

**Endpoint**: `LogoutUser`

**Request Parameters**:
- `token` (String, Required): Valid authentication token

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:LogoutUserRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
        </tns:LogoutUserRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:LogoutUserResponse>
            <tns:success>true</tns:success>
            <tns:message>Logout successful</tns:message>
            <tns:timestamp>2024-01-01T12:10:00Z</tns:timestamp>
        </tns:LogoutUserResponse>
    </soap:Body>
</soap:Envelope>
```

---

## User Management

### 4. GetUserProfile

Retrieves user profile information.

**Endpoint**: `GetUserProfile`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `userId` (Integer, Optional): Target user ID (if not provided, returns current user's profile)

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:GetUserProfileRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:userId>123</tns:userId>
        </tns:GetUserProfileRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 5. UpdateUserProfile

Updates user profile information.

**Endpoint**: `UpdateUserProfile`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `userId` (Integer, Optional): Target user ID (if not provided, updates current user's profile)
- `firstName` (String, Optional): New first name
- `lastName` (String, Optional): New last name
- `phoneNumber` (String, Optional): New phone number
- `profilePictureUrl` (String, Optional): New profile picture URL

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:UpdateUserProfileRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:userId>123</tns:userId>
            <tns:firstName>Johnathan</tns:firstName>
            <tns:lastName>Smith</tns:lastName>
            <tns:phoneNumber>9876543210</tns:phoneNumber>
        </tns:UpdateUserProfileRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 6. GetAllUsers

Retrieves all users with pagination support.

**Endpoint**: `GetAllUsers`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `page` (Integer, Optional): Page number (default: 1)
- `pageSize` (Integer, Optional): Items per page (default: 20, max: 100)
- `status` (String, Optional): Filter by user status (ACTIVE, INACTIVE, SUSPENDED)

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:GetAllUsersRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:page>1</tns:page>
            <tns:pageSize>10</tns:pageSize>
            <tns:status>ACTIVE</tns:status>
        </tns:GetAllUsersRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 7. DeactivateUser

Deactivates a user account.

**Endpoint**: `DeactivateUser`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `userId` (Integer, Required): Target user ID to deactivate

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:DeactivateUserRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:userId>124</tns:userId>
        </tns:DeactivateUserRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:DeactivateUserResponse>
            <tns:success>true</tns:success>
            <tns:message>User deactivated successfully</tns:message>
            <tns:timestamp>2024-01-01T12:30:00Z</tns:timestamp>
        </tns:DeactivateUserResponse>
    </soap:Body>
</soap:Envelope>
```

---

## Role Management

### 8. CreateRole

Creates a new role in the system.

**Endpoint**: `CreateRole`

**Request Parameters**:
- `token` (String, Required): Valid authentication token with ROLE_CREATE permission
- `name` (String, Required): Role name
- `description` (String, Optional): Role description

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:CreateRoleRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:name>MANAGER</tns:name>
            <tns:description>Manager with limited administrative access</tns:description>
        </tns:CreateRoleRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 9. AssignRole

Assigns a role to a user.

**Endpoint**: `AssignRole`

**Request Parameters**:
- `token` (String, Required): Valid authentication token with ROLE_ASSIGN permission
- `userId` (Integer, Required): Target user ID
- `roleId` (Integer, Required): Role ID to assign

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:AssignRoleRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:userId>123</tns:userId>
            <tns:roleId>5</tns:roleId>
        </tns:AssignRoleRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:AssignRoleResponse>
            <tns:success>true</tns:success>
            <tns:message>Role assigned successfully</tns:message>
            <tns:timestamp>2024-01-01T12:40:00Z</tns:timestamp>
        </tns:AssignRoleResponse>
    </soap:Body>
</soap:Envelope>
```

---

### 10. GetUserRoles

Retrieves roles assigned to a user.

**Endpoint**: `GetUserRoles`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `userId` (Integer, Optional): Target user ID (if not provided, returns current user's roles)

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:GetUserRolesRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:userId>123</tns:userId>
        </tns:GetUserRolesRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

## Permission Management

### 11. CreatePermission

Creates a new permission in the system.

**Endpoint**: `CreatePermission`

**Request Parameters**:
- `token` (String, Required): Valid authentication token with PERMISSION_CREATE permission
- `name` (String, Required): Permission name
- `description` (String, Optional): Permission description
- `module` (String, Required): Module name (USER, PROFILE, ROLE, AUDIT)
- `action` (String, Required): Action name (CREATE, READ, UPDATE, DELETE, LIST, ASSIGN)

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:CreatePermissionRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:name>USER_APPROVE</tns:name>
            <tns:description>Approve user registrations</tns:description>
            <tns:module>USER</tns:module>
            <tns:action>APPROVE</tns:action>
        </tns:CreatePermissionRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 12. AssignPermissionToRole

Assigns a permission to a role.

**Endpoint**: `AssignPermissionToRole`

**Request Parameters**:
- `token` (String, Required): Valid authentication token with PERMISSION_ASSIGN permission
- `roleId` (Integer, Required): Target role ID
- `permissionId` (Integer, Required): Permission ID to assign

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:AssignPermissionToRoleRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:roleId>5</tns:roleId>
            <tns:permissionId>25</tns:permissionId>
        </tns:AssignPermissionToRoleRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:AssignPermissionToRoleResponse>
            <tns:success>true</tns:success>
            <tns:message>Permission assigned to role successfully</tns:message>
            <tns:timestamp>2024-01-01T12:55:00Z</tns:timestamp>
        </tns:AssignPermissionToRoleResponse>
    </soap:Body>
</soap:Envelope>
```

---

## Password Management

### 13. RequestPasswordReset

Requests a password reset for a user.

**Endpoint**: `RequestPasswordReset`

**Request Parameters**:
- `email` (String, Required): User's email address

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:RequestPasswordResetRequest>
            <tns:email>john.doe@example.com</tns:email>
        </tns:RequestPasswordResetRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:RequestPasswordResetResponse>
            <tns:success>true</tns:success>
            <tns:message>Password reset email sent</tns:message>
            <tns:timestamp>2024-01-01T13:00:00Z</tns:timestamp>
        </tns:RequestPasswordResetResponse>
    </soap:Body>
</soap:Envelope>
```

---

### 14. ResetPassword

Resets a user's password using a reset token.

**Endpoint**: `ResetPassword`

**Request Parameters**:
- `resetToken` (String, Required): Password reset token received via email
- `newPassword` (String, Required): New password

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:ResetPasswordRequest>
            <tns:resetToken>abc123def456...</tns:resetToken>
            <tns:newPassword>NewSecurePass456!</tns:newPassword>
        </tns:ResetPasswordRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:ResetPasswordResponse>
            <tns:success>true</tns:success>
            <tns:message>Password reset successfully</tns:message>
            <tns:timestamp>2024-01-01T13:05:00Z</tns:timestamp>
        </tns:ResetPasswordResponse>
    </soap:Body>
</soap:Envelope>
```

---

### 15. ChangePassword

Changes a user's password (requires current password).

**Endpoint**: `ChangePassword`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `currentPassword` (String, Required): Current password
- `newPassword` (String, Required): New password

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:ChangePasswordRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:currentPassword>SecurePass123!</tns:currentPassword>
            <tns:newPassword>NewSecurePass456!</tns:newPassword>
        </tns:ChangePasswordRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:ChangePasswordResponse>
            <tns:success>true</tns:success>
            <tns:message>Password changed successfully</tns:message>
            <tns:timestamp>2024-01-01T13:10:00Z</tns:timestamp>
        </tns:ChangePasswordResponse>
    </soap:Body>
</soap:Envelope>
```

---

## Audit Logs

### 16. GetAuditLogs

Retrieves audit logs with filtering options.

**Endpoint**: `GetAuditLogs`

**Request Parameters**:
- `token` (String, Required): Valid authentication token with AUDIT_READ permission
- `startDate` (DateTime, Optional): Start date for filtering
- `endDate` (DateTime, Optional): End date for filtering
- `userId` (Integer, Optional): Filter by specific user ID
- `action` (String, Optional): Filter by action type
- `resourceType` (String, Optional): Filter by resource type
- `page` (Integer, Optional): Page number (default: 1)
- `pageSize` (Integer, Optional): Items per page (default: 20, max: 100)

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:GetAuditLogsRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:startDate>2024-01-01T00:00:00Z</tns:startDate>
            <tns:endDate>2024-01-01T23:59:59Z</tns:endDate>
            <tns:action>USER_LOGIN_SUCCESS</tns:action>
            <tns:page>1</tns:page>
            <tns:pageSize>10</tns:pageSize>
        </tns:GetAuditLogsRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

### 17. GetUserAuditLogs

Retrieves audit logs for a specific user.

**Endpoint**: `GetUserAuditLogs`

**Request Parameters**:
- `token` (String, Required): Valid authentication token
- `userId` (Integer, Optional): Target user ID (if not provided, returns current user's logs)
- `startDate` (DateTime, Optional): Start date for filtering
- `endDate` (DateTime, Optional): End date for filtering
- `page` (Integer, Optional): Page number (default: 1)
- `pageSize` (Integer, Optional): Items per page (default: 20, max: 100)

**Request Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
        <tns:GetUserAuditLogsRequest>
            <tns:token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</tns:token>
            <tns:userId>123</tns:userId>
            <tns:startDate>2024-01-01T00:00:00Z</tns:startDate>
            <tns:endDate>2024-01-01T23:59:59Z</tns:endDate>
            <tns:page>1</tns:page>
            <tns:pageSize>10</tns:pageSize>
        </tns:GetUserAuditLogsRequest>
    </soap:Body>
</soap:Envelope>
```

**Response Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://example.com/usermanagement">
    <soap:Header/>
    <soap:Body>
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
    </soap:Body>
</soap:Envelope>
```

---

## Error Handling

### Error Response Format

All errors are returned in the SOAP Fault format with detailed error information:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header/>
    <soap:Body>
        <soap:Fault>
            <faultcode>soap:Client</faultcode>
            <faultstring>Invalid input parameters</faultstring>
            <detail>
                <tns:ErrorResponse xmlns:tns="http://example.com/usermanagement">
                    <tns:code>VALID_001</tns:code>
                    <tns:message>Email address is required</tns:message>
                    <tns:details>Field 'email' cannot be empty</tns:details>
                    <tns:timestamp>2024-01-01T12:00:00Z</tns:timestamp>
                </tns:ErrorResponse>
            </detail>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>
```

### Common Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| AUTH_001 | Invalid credentials | 401 |
| AUTH_002 | Token expired | 401 |
| AUTH_003 | Insufficient permissions | 403 |
| USER_001 | User not found | 404 |
| USER_002 | User already exists | 409 |
| USER_003 | Invalid user status | 400 |
| ROLE_001 | Role not found | 404 |
| ROLE_002 | Role already assigned | 409 |
| PERM_001 | Permission not found | 404 |
| PERM_002 | Invalid permission assignment | 400 |
| VALID_001 | Invalid input format | 400 |
| VALID_002 | Required field missing | 400 |
| SYS_001 | Internal server error | 500 |
| SYS_002 | Database connection error | 500 |

---

## Data Types

### Common Data Types

#### User
```xml
<tns:User>
    <tns:id>Integer</tns:id>
    <tns:email>String</tns:email>
    <tns:firstName>String</tns:firstName>
    <tns:lastName>String</tns:lastName>
    <tns:phoneNumber>String (Optional)</tns:phoneNumber>
    <tns:profilePictureUrl>String (Optional)</tns:profilePictureUrl>
    <tns:status>String</tns:status>
    <tns:createdAt>DateTime</tns:createdAt>
    <tns:updatedAt>DateTime</tns:updatedAt>
    <tns:lastLogin>DateTime (Optional)</tns:lastLogin>
</tns:User>
```

#### Role
```xml
<tns:Role>
    <tns:id>Integer</tns:id>
    <tns:name>String</tns:name>
    <tns:description>String (Optional)</tns:description>
    <tns:createdAt>DateTime</tns:createdAt>
    <tns:updatedAt>DateTime</tns:updatedAt>
</tns:Role>
```

#### Permission
```xml
<tns:Permission>
    <tns:id>Integer</tns:id>
    <tns:name>String</tns:name>
    <tns:description>String (Optional)</tns:description>
    <tns:module>String</tns:module>
    <tns:action>String</tns:action>
    <tns:createdAt>DateTime</tns:createdAt>
</tns:Permission>
```

#### AuditLog
```xml
<tns:AuditLog>
    <tns:id>Integer</tns:id>
    <tns:userId>Integer (Optional)</tns:userId>
    <tns:action>String</tns:action>
    <tns:resourceType>String</tns:resourceType>
    <tns:resourceId>Integer (Optional)</tns:resourceId>
    <tns:oldValues>String (Optional)</tns:oldValues>
    <tns:newValues>String (Optional)</tns:newValues>
    <tns:ipAddress>String (Optional)</tns:ipAddress>
    <tns:userAgent>String (Optional)</tns:userAgent>
    <tns:createdAt>DateTime</tns:createdAt>
</tns:AuditLog>
```

### Data Format Standards

- **DateTime**: ISO 8601 format (UTC) - `2024-01-01T12:00:00Z`
- **Boolean**: `true` or `false`
- **String**: UTF-8 encoded
- **Integer**: 32-bit signed integers
- **Optional Fields**: Marked with `minOccurs="0"` in WSDL

---

## Security Considerations

### Authentication
- Use JWT tokens for authentication
- Tokens expire after 1 hour by default
- Include token in request body for protected endpoints

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Rate Limiting
- Authentication endpoints: 5 requests per minute per IP
- Other endpoints: 100 requests per minute per authenticated user

### HTTPS
- Always use HTTPS in production environments
- TLS 1.3 recommended for optimal security

---

## Testing with Robot Framework

This API is specifically designed for Robot Framework testing. See the [Robot Framework Testing Guide](Robot_Framework_Testing_Guide.md) for detailed testing examples and best practices.