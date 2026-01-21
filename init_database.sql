-- BP Chairperson App Database Initialization
-- Run this script in your MySQL database to create tables

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display_name VARCHAR(80) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    sobriety_days INT DEFAULT NULL,
    agreed_guidelines BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    gender VARCHAR(10) DEFAULT NULL
);

-- Create meetings table
CREATE TABLE IF NOT EXISTS meetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    zoom_link VARCHAR(500),
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    is_open BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    gender_restriction VARCHAR(10) DEFAULT NULL
);

-- Create chair_signups table
CREATE TABLE IF NOT EXISTS chair_signups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meeting_id INT UNIQUE NOT NULL,
    user_id INT NOT NULL,
    display_name_snapshot VARCHAR(80) NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create sponsors table (Sponsor Registry)
CREATE TABLE IF NOT EXISTS sponsors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    display_name VARCHAR(80) NOT NULL,
    sobriety_date DATE DEFAULT NULL,
    current_sponsees INT NOT NULL DEFAULT 0,
    max_sponsees INT NOT NULL DEFAULT 0,
    email VARCHAR(255) DEFAULT NULL,
    phone VARCHAR(50) DEFAULT NULL,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(event_date);
CREATE INDEX IF NOT EXISTS idx_meetings_date_time ON meetings(event_date, start_time);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_chair_signups_meeting ON chair_signups(meeting_id);
CREATE INDEX IF NOT EXISTS idx_chair_signups_user ON chair_signups(user_id);
CREATE INDEX IF NOT EXISTS idx_sponsors_active ON sponsors(is_active);
CREATE INDEX IF NOT EXISTS idx_sponsors_created ON sponsors(created_at);

-- Insert admin user (change password!)
INSERT IGNORE INTO users (display_name, email, password_hash, is_admin, agreed_guidelines)
VALUES ('Admin', 'admin@backporch.org', 'scrypt:32768:8:1$changethis$changethishashinproduction', TRUE, TRUE);

SELECT 'Database initialization complete!' as status;
