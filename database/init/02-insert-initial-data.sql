-- Insert initial data for Enhanced User Management System
-- This script populates the database with default roles, permissions, and a sample admin user

-- Insert default roles
INSERT INTO roles (name, description) VALUES
('ADMIN', 'System administrator with full access'),
('MANAGER', 'Manager with limited administrative access'),
('USER', 'Regular user with basic access')
ON CONFLICT (name) DO NOTHING;

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

-- Create a default admin user (password: Admin123!)
-- Note: This is a bcrypt hash of "Admin123!"
INSERT INTO users (email, password_hash, first_name, last_name, status) VALUES
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'System', 'Administrator', 'ACTIVE');

-- Assign ADMIN role to the admin user
INSERT INTO user_roles (user_id, role_id, assigned_by)
SELECT u.id, r.id, u.id
FROM users u, roles r
WHERE u.email = 'admin@example.com' AND r.name = 'ADMIN';

-- Create some test users for development/testing
INSERT INTO users (email, password_hash, first_name, last_name, phone_number, status) VALUES
('testuser1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User1', '1234567890', 'ACTIVE'),
('testuser2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User2', '0987654321', 'ACTIVE'),
('testuser3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User3', '1122334455', 'INACTIVE');

-- Assign USER role to test users
INSERT INTO user_roles (user_id, role_id, assigned_by)
SELECT u.id, r.id, 1
FROM users u, roles r
WHERE u.email LIKE 'testuser%' AND r.name = 'USER';

-- Create a test manager
INSERT INTO users (email, password_hash, first_name, last_name, phone_number, status) VALUES
('manager@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'Manager', '5555555555', 'ACTIVE');

-- Assign MANAGER role to the test manager
INSERT INTO user_roles (user_id, role_id, assigned_by)
SELECT u.id, r.id, 1
FROM users u, roles r
WHERE u.email = 'manager@example.com' AND r.name = 'MANAGER';

-- Verify data insertion
SELECT 'Roles created:' as info, COUNT(*) as count FROM roles
UNION ALL
SELECT 'Permissions created:' as info, COUNT(*) as count FROM permissions
UNION ALL
SELECT 'Role-Permission assignments created:' as info, COUNT(*) as count FROM role_permissions
UNION ALL
SELECT 'Users created:' as info, COUNT(*) as count FROM users
UNION ALL
SELECT 'User-Role assignments created:' as info, COUNT(*) as count FROM user_roles;

-- Create database views for easier access to common queries
DROP VIEW IF EXISTS user_roles_view;
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

DROP VIEW IF EXISTS user_permissions_view;
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

-- Create stored procedures for common operations
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

-- Create audit triggers for tracking changes
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

CREATE TRIGGER users_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_users_trigger();

-- Record this data version
INSERT INTO schema_migrations (version) VALUES ('002_initial_data')
ON CONFLICT (version) DO NOTHING;