-- SQL Migration to add authentication support
-- Run this against your database to add password_hash column

-- Add password_hash column to users table
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT NULL;

-- Optional: Create an index on username for faster lookups during login
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Note: Existing users will have NULL password_hash
-- They won't be able to login until a password is set
-- Use the /auth/set-password endpoint to set passwords for existing users
