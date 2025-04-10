-- Migration to create the roles table

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Migration to insert default roles if they don't exist

INSERT INTO roles (name) VALUES ('Admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('Viewer') ON CONFLICT (name) DO NOTHING;