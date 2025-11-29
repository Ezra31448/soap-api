-- Rollback for migration 003: Add user profile fields
-- Created at: 2024-01-01T00:00:00
-- This rollback removes the additional profile fields from the users table

-- Drop triggers
DROP TRIGGER IF EXISTS validate_password_update ON users;

-- Drop functions
DROP FUNCTION IF EXISTS validate_password_trigger();
DROP FUNCTION IF EXISTS validate_password_strength(TEXT);

-- Drop constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_email;
ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_website_url;
ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_twitter_handle;
ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_linkedin_url;

-- Drop indexes
DROP INDEX IF EXISTS idx_users_city;
DROP INDEX IF EXISTS idx_users_country;
DROP INDEX IF EXISTS idx_users_timezone;
DROP INDEX IF EXISTS idx_users_language;
DROP INDEX IF EXISTS idx_users_two_factor;
DROP INDEX IF EXISTS idx_users_last_password_change;

-- Drop columns (PostgreSQL doesn't support multiple columns in one ALTER TABLE)
ALTER TABLE users DROP COLUMN IF EXISTS bio;
ALTER TABLE users DROP COLUMN IF EXISTS date_of_birth;
ALTER TABLE users DROP COLUMN IF EXISTS address;
ALTER TABLE users DROP COLUMN IF EXISTS city;
ALTER TABLE users DROP COLUMN IF EXISTS country;
ALTER TABLE users DROP COLUMN IF EXISTS postal_code;
ALTER TABLE users DROP COLUMN IF EXISTS website;
ALTER TABLE users DROP COLUMN IF EXISTS linkedin_url;
ALTER TABLE users DROP COLUMN IF EXISTS twitter_handle;
ALTER TABLE users DROP COLUMN IF EXISTS timezone;
ALTER TABLE users DROP COLUMN IF EXISTS language;
ALTER TABLE users DROP COLUMN IF EXISTS email_notifications;
ALTER TABLE users DROP COLUMN IF EXISTS sms_notifications;
ALTER TABLE users DROP COLUMN IF EXISTS two_factor_enabled;
ALTER TABLE users DROP COLUMN IF EXISTS last_password_change;