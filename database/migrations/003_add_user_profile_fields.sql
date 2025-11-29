-- Migration 003: Add user profile fields
-- Created at: 2024-01-01T00:00:00
-- This migration adds additional profile fields to the users table

-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20),
ADD COLUMN IF NOT EXISTS website VARCHAR(255),
ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(255),
ADD COLUMN IF NOT EXISTS twitter_handle VARCHAR(50),
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC',
ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS email_notifications BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS sms_notifications BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS last_password_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add indexes for new fields
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
CREATE INDEX IF NOT EXISTS idx_users_country ON users(country);
CREATE INDEX IF NOT EXISTS idx_users_timezone ON users(timezone);
CREATE INDEX IF NOT EXISTS idx_users_language ON users(language);
CREATE INDEX IF NOT EXISTS idx_users_two_factor ON users(two_factor_enabled);
CREATE INDEX IF NOT EXISTS idx_users_last_password_change ON users(last_password_change);

-- Add constraint for valid email format
ALTER TABLE users 
ADD CONSTRAINT valid_email 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Add constraint for valid URL format (if provided)
ALTER TABLE users 
ADD CONSTRAINT valid_website_url 
CHECK (website IS NULL OR website ~* '^https?://[^\s/$.?#].[^\s]*$');

-- Add constraint for valid Twitter handle (if provided)
ALTER TABLE users 
ADD CONSTRAINT valid_twitter_handle 
CHECK (twitter_handle IS NULL OR twitter_handle ~* '^@[A-Za-z0-9_]{1,15}$');

-- Add constraint for valid LinkedIn URL (if provided)
ALTER TABLE users 
ADD CONSTRAINT valid_linkedin_url 
CHECK (linkedin_url IS NULL OR linkedin_url ~* '^https?://(www\.)?linkedin\.com/in/[A-Za-z0-9-]{3,100}/?$');

-- Create function to validate password strength
CREATE OR REPLACE FUNCTION validate_password_strength(password TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Password must be at least 8 characters
    IF LENGTH(password) < 8 THEN
        RETURN FALSE;
    END IF;
    
    -- Password must contain at least one uppercase letter
    IF password !~ '[A-Z]' THEN
        RETURN FALSE;
    END IF;
    
    -- Password must contain at least one lowercase letter
    IF password !~ '[a-z]' THEN
        RETURN FALSE;
    END IF;
    
    -- Password must contain at least one digit
    IF password !~ '[0-9]' THEN
        RETURN FALSE;
    END IF;
    
    -- Password must contain at least one special character
    IF password !~ '[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]' THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to validate password on update
CREATE OR REPLACE FUNCTION validate_password_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Only validate if password is being changed
    IF OLD.password_hash IS DISTINCT FROM NEW.password_hash THEN
        -- Note: This is a simplified check since we're dealing with hashed passwords
        -- In a real implementation, you would validate the plain text password
        -- before hashing it in the application layer
        NEW.last_password_change = CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update last_password_change
DROP TRIGGER IF EXISTS validate_password_update ON users;
CREATE TRIGGER validate_password_update
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION validate_password_trigger();

-- Record this migration
INSERT INTO schema_migrations (version) VALUES ('003_add_user_profile_fields')
ON CONFLICT (version) DO NOTHING;