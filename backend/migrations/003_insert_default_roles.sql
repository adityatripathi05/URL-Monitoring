-- Migration to insert default roles if they don't exist

INSERT INTO roles (name) VALUES ('Admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('Viewer') ON CONFLICT (name) DO NOTHING;
