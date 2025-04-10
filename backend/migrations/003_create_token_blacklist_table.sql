-- Migration to create the token_blacklist table

CREATE TABLE IF NOT EXISTS token_blacklist (
    jti VARCHAR(255) PRIMARY KEY, -- JWT ID, using VARCHAR for flexibility, could be UUID
    expires_at TIMESTAMPTZ NOT NULL -- Store the original expiry time of the token
);

-- Optional: Index on expires_at for efficient cleanup of old tokens
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires_at ON token_blacklist (expires_at);

-- Add index on token_blacklist.jti for faster token blacklist checks
CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist (jti);