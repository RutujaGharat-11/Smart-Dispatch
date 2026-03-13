-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'USER',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- REQUESTS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    complaint_type TEXT NOT NULL,
    priority INTEGER NOT NULL,
    estimated_time INTEGER DEFAULT 1,
    description TEXT,
    location TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =========================
-- RESOURCES TABLE
-- =========================
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    status TEXT DEFAULT 'free',
    current_request_id INTEGER
);

-- =========================
-- ASSIGNMENTS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    algorithm_used TEXT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES requests(id),
    FOREIGN KEY (resource_id) REFERENCES resources(id)
);

-- =========================
-- LOGS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO resources (name, resource_type)
SELECT 'Garbage Truck A', 'Garbage'
WHERE NOT EXISTS (
    SELECT 1 FROM resources WHERE name = 'Garbage Truck A'
);

INSERT INTO resources (name, resource_type)
SELECT 'Water Tanker B', 'Water'
WHERE NOT EXISTS (
    SELECT 1 FROM resources WHERE name = 'Water Tanker B'
);

INSERT INTO resources (name, resource_type)
SELECT 'Ambulance C', 'Medical'
WHERE NOT EXISTS (
    SELECT 1 FROM resources WHERE name = 'Ambulance C'
);

INSERT INTO resources (name, resource_type)
SELECT 'Agriculture Officer D', 'Agriculture'
WHERE NOT EXISTS (
    SELECT 1 FROM resources WHERE name = 'Agriculture Officer D'
);