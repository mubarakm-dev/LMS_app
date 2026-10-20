USE lms_db;

--  Admin@1234 
INSERT INTO users (first_name, last_name, email, password_hash, role, is_verified)
VALUES ('System', 'Admin', 'admin@sqi.testing',
        '$2b$12$eD3egVFVJxd4bFsIgt.llesPYAVHryYNte.3lS/3e.ixZq7hb0HBK',
        'admin', TRUE);
