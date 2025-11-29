# Database Schema Documentation

## Overview
This document contains the complete PostgreSQL database schema for the Enhanced User Management System SOAP API service.

## Table Creation Scripts

### 1. Users Table
```sql
-- Drop existing tables if they exist (for development purposes)
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    profile_picture_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    reset_token VARCHAR(255),
    reset_expires TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. Roles Table
```sql
-- Create roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for roles table
CREATE INDEX idx_roles_name ON roles(name);

-- Create trigger for updated_at timestamp
CREATE TRIGGER update_roles_updated_at 
    BEFORE UPDATE ON roles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3. Permissions Table
```sql
-- Create permissions table
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for permissions table
CREATE INDEX idx_permissions_module ON permissions(module);
CREATE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_permissions_action ON permissions(action);
```

### 4. User Roles Junction Table
```sql
-- Create user_roles junction table
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- Create indexes for user_roles table
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_assigned_at ON user_roles(assigned_at);
```

### 5. Role Permissions Junction Table
```sql
-- Create role_permissions junction table
CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER REFERENCES users(id),
    PRIMARY KEY (role_id, permission_id)
);

-- Create indexes for role_permissions table
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX idx_role_permissions_granted_at ON role_permissions(granted_at);
```

### 6. Audit Logs Table
```sql
-- Create audit_logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for audit_logs table
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
```

### 7. Sessions Table
```sql
-- Create sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Create indexes for sessions table
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
```

## Initial Data Setup

### Default Roles
```sql
-- Insert default roles
INSERT INTO roles (name, description) VALUES
('ADMIN', 'System administrator with full access'),
('MANAGER', 'Manager with limited administrative access'),
('USER', 'Regular user with basic access');

-- Verify roles insertion
SELECT * FROM roles;
```

### Default Permissions
```sql
-- Insert default permissions
INSERT INTO permissions (name, description, module, action) VALUES
-- User permissions
('USER_CREATE', 'Create new users', 'USER', 'CREATE'),
('USER_READ', 'View user information', 'USER', 'READ'),
('USER_UPDATE', 'Update user information', 'USER', 'UPDATE'),
('USER_DELETE', 'Delete users', 'USER', 'DELETE'),
('USER_LIST', 'List all users', 'USER', 'LIST'),

-- Profile permissions
('PROFILE_READ_OWN', 'View own profile', 'PROFILE', 'READ_OWN'),
('PROFILE_UPDATE_OWN', 'Update own profile', 'PROFILE', 'UPDATE_OWN'),
('PROFILE_READ_ALL', 'View any user profile', 'PROFILE', 'READ_ALL'),
('PROFILE_UPDATE_ALL', 'Update any user profile', 'PROFILE', 'UPDATE_ALL'),

-- Role permissions
('ROLE_CREATE', 'Create new roles', 'ROLE', 'CREATE'),
('ROLE_READ', 'View role information', 'ROLE', 'READ'),
('ROLE_UPDATE', 'Update role information', 'ROLE', 'UPDATE'),
('ROLE_DELETE', 'Delete roles', 'ROLE', 'DELETE'),
('ROLE_ASSIGN', 'Assign roles to users', 'ROLE', 'ASSIGN'),

-- Permission permissions
('PERMISSION_CREATE', 'Create new permissions', 'PERMISSION', 'CREATE'),
('PERMISSION_READ', 'View permission information', 'PERMISSION', 'READ'),
('PERMISSION_UPDATE', 'Update permission information', 'PERMISSION', 'UPDATE'),
('PERMISSION_DELETE', 'Delete permissions', 'PERMISSION', 'DELETE'),
('PERMISSION_ASSIGN', 'Assign permissions to roles', 'PERMISSION', 'ASSIGN'),

-- Audit permissions
('AUDIT_READ', 'View audit logs', 'AUDIT', 'READ'),
('AUDIT_EXPORT', 'Export audit logs', 'AUDIT', 'EXPORT');

-- Verify permissions insertion
SELECT * FROM permissions ORDER BY module, action;
```

### Role-Permission Assignments
```sql
-- Assign all permissions to ADMIN role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'ADMIN';

-- Assign limited permissions to MANAGER role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'MANAGER' AND p.module IN ('USER', 'PROFILE', 'AUDIT');

-- Assign basic permissions to USER role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'USER' AND p.name IN ('PROFILE_READ_OWN', 'PROFILE_UPDATE_OWN');

-- Verify role-permission assignments
SELECT 
    r.name as role_name,
    p.module,
    p.action,
    p.name as permission_name
FROM roles r
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
ORDER BY r.name, p.module, p.action;
```

### Sample Admin User
```sql
-- Create a default admin user (password: Admin123!)
-- Note: In production, use a secure password generation method
INSERT INTO users (email, password_hash, first_name, last_name, status) VALUES
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'System', 'Administrator', 'ACTIVE');

-- Assign ADMIN role to the admin user
INSERT INTO user_roles (user_id, role_id, assigned_by)
SELECT u.id, r.id, u.id
FROM users u, roles r
WHERE u.email = 'admin@example.com' AND r.name = 'ADMIN';

-- Verify admin user creation
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.status,
    r.name as role_name
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE u.email = 'admin@example.com';
```

## Database Views

### User Roles View
```sql
-- Create view for user roles
CREATE VIEW user_roles_view AS
SELECT 
    u.id as user_id,
    u.email,
    u.first_name,
    u.last_name,
    u.status,
    r.id as role_id,
    r.name as role_name,
    r.description as role_description,
    ur.assigned_at,
    ua.email as assigned_by_email
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
LEFT JOIN users ua ON ur.assigned_by = ua.id;
```

### User Permissions View
```sql
-- Create view for user permissions
CREATE VIEW user_permissions_view AS
SELECT DISTINCT
    u.id as user_id,
    u.email,
    p.id as permission_id,
    p.name as permission_name,
    p.module,
    p.action,
    p.description as permission_description,
    r.name as role_name
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id;
```

### Audit Summary View
```sql
-- Create view for audit summary
CREATE VIEW audit_summary_view AS
SELECT 
    DATE(created_at) as audit_date,
    resource_type,
    action,
    COUNT(*) as action_count,
    COUNT(DISTINCT user_id) as unique_users
FROM audit_logs
GROUP BY DATE(created_at), resource_type, action
ORDER BY audit_date DESC, resource_type, action;
```

## Stored Procedures

### Get User Permissions Procedure
```sql
-- Create procedure to get user permissions
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id INTEGER)
RETURNS TABLE (
    permission_id INTEGER,
    permission_name VARCHAR(100),
    module VARCHAR(50),
    action VARCHAR(50),
    role_name VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        p.id,
        p.name,
        p.module,
        p.action,
        r.name
    FROM permissions p
    JOIN role_permissions rp ON p.id = rp.permission_id
    JOIN roles r ON rp.role_id = r.id
    JOIN user_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = p_user_id
    ORDER BY p.module, p.action;
END;
$$ LANGUAGE plpgsql;
```

### Check User Permission Procedure
```sql
-- Create procedure to check if user has specific permission
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id INTEGER,
    p_module VARCHAR(50),
    p_action VARCHAR(50)
)
RETURNS BOOLEAN AS $$
DECLARE
    permission_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO permission_count
    FROM user_permissions_view
    WHERE user_id = p_user_id 
    AND module = p_module 
    AND action = p_action;
    
    RETURN permission_count > 0;
END;
$$ LANGUAGE plpgsql;
```

### Log Audit Event Procedure
```sql
-- Create procedure to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_user_id INTEGER,
    p_action VARCHAR(100),
    p_resource_type VARCHAR(50),
    p_resource_id INTEGER DEFAULT NULL,
    p_old_values TEXT DEFAULT NULL,
    p_new_values TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    audit_id INTEGER;
BEGIN
    INSERT INTO audit_logs (
        user_id, action, resource_type, resource_id, 
        old_values, new_values, ip_address, user_agent
    ) VALUES (
        p_user_id, p_action, p_resource_type, p_resource_id,
        p_old_values, p_new_values, p_ip_address, p_user_agent
    ) RETURNING id INTO audit_id;
    
    RETURN audit_id;
END;
$$ LANGUAGE plpgsql;
```

## Database Triggers

### Audit Trigger for Users Table
```sql
-- Create audit trigger for users table
CREATE OR REPLACE FUNCTION audit_users_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM log_audit_event(
            NEW.id,
            'USER_CREATED',
            'USER',
            NEW.id,
            NULL,
            ROW_TO_JSON(NEW)::text,
            inet_client_addr(),
            current_setting('application_name', true)
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM log_audit_event(
            NEW.id,
            'USER_UPDATED',
            'USER',
            NEW.id,
            ROW_TO_JSON(OLD)::text,
            ROW_TO_JSON(NEW)::text,
            inet_client_addr(),
            current_setting('application_name', true)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM log_audit_event(
            OLD.id,
            'USER_DELETED',
            'USER',
            OLD.id,
            ROW_TO_JSON(OLD)::text,
            NULL,
            inet_client_addr(),
            current_setting('application_name', true)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on users table
CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_users_trigger();
```

### Audit Trigger for Roles Table
```sql
-- Create audit trigger for roles table
CREATE OR REPLACE FUNCTION audit_roles_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM log_audit_event(
            current_setting('current_user_id', true)::INTEGER,
            'ROLE_CREATED',
            'ROLE',
            NEW.id,
            NULL,
            ROW_TO_JSON(NEW)::text,
            inet_client_addr(),
            current_setting('application_name', true)
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM log_audit_event(
            current_setting('current_user_id', true)::INTEGER,
            'ROLE_UPDATED',
            'ROLE',
            NEW.id,
            ROW_TO_JSON(OLD)::text,
            ROW_TO_JSON(NEW)::text,
            inet_client_addr(),
            current_setting('application_name', true)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM log_audit_event(
            current_setting('current_user_id', true)::INTEGER,
            'ROLE_DELETED',
            'ROLE',
            OLD.id,
            ROW_TO_JSON(OLD)::text,
            NULL,
            inet_client_addr(),
            current_setting('application_name', true)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on roles table
CREATE TRIGGER roles_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON roles
    FOR EACH ROW EXECUTE FUNCTION audit_roles_trigger();
```

## Performance Optimization

### Partitioning for Audit Logs
```sql
-- Create partitioned audit_logs table for better performance
-- This is optional for large-scale deployments

-- Create partitioned table
CREATE TABLE audit_logs_partitioned (
    LIKE audit_logs INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audit_logs_2024_02 PARTITION OF audit_logs_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Add more partitions as needed
```

### Database Maintenance
```sql
-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up old audit logs (older than 1 year)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_logs WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 year';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

## Security Considerations

### Row Level Security (Optional)
```sql
-- Enable row level security for users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to see their own profile
CREATE POLICY users_own_profile ON users
    FOR SELECT USING (id = current_setting('current_user_id', true)::INTEGER);

-- Create policy to allow admins to see all users
CREATE POLICY users_admin_access ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM user_permissions_view
            WHERE user_id = current_setting('current_user_id', true)::INTEGER
            AND module = 'USER' AND action = 'READ'
        )
    );
```

## Backup and Recovery

### Backup Script Template
```bash
#!/bin/bash
# Database backup script template
DB_NAME="user_management_db"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Full database backup
pg_dump -U $DB_USER -h localhost -d $DB_NAME -f $BACKUP_DIR/full_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/full_backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

## Testing Data

### Test Users Generation
```sql
-- Generate test users for development/testing
INSERT INTO users (email, password_hash, first_name, last_name, phone_number, status) VALUES
('testuser1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User1', '1234567890', 'ACTIVE'),
('testuser2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User2', '0987654321', 'ACTIVE'),
('testuser3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User3', '1122334455', 'INACTIVE');

-- Assign USER role to test users
INSERT INTO user_roles (user_id, role_id, assigned_by)
SELECT u.id, r.id, 1
FROM users u, roles r
WHERE u.email LIKE 'testuser%' AND r.name = 'USER';
```

## Migration Scripts

### Version Control
```sql
-- Create migrations table to track schema changes
CREATE TABLE schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example migration record
INSERT INTO schema_migrations (version) VALUES ('001_initial_schema');
```

This database schema provides a solid foundation for the Enhanced User Management System with comprehensive audit capabilities, security features, and performance optimizations.