-- MySQL initialization script for Computer Use Agent Database

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS computer_use_db;
USE computer_use_db;

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status ENUM('idle', 'running', 'completed', 'error') DEFAULT 'idle',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'tool', 'system') NOT NULL,
    content TEXT NOT NULL,
    message_type ENUM('text', 'tool_result', 'screenshot', 'error') DEFAULT 'text',
    tool_name VARCHAR(255) NULL,
    screenshot LONGTEXT NULL, -- base64 encoded image
    error TEXT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_role (role)
);

-- Create indexes for better performance
CREATE INDEX idx_messages_session_timestamp ON messages(session_id, timestamp);
CREATE INDEX idx_sessions_updated_at ON sessions(updated_at);

-- Insert some sample data for testing
INSERT INTO sessions (id, name, status) VALUES 
('test-session-1', 'Sample Session 1', 'idle'),
('test-session-2', 'Sample Session 2', 'completed');

INSERT INTO messages (session_id, role, content, message_type) VALUES 
('test-session-1', 'user', 'Hello, can you help me with a task?', 'text'),
('test-session-1', 'assistant', 'Of course! I\'m here to help. What would you like me to do?', 'text'),
('test-session-2', 'user', 'Search for weather information', 'text'),
('test-session-2', 'assistant', 'I\'ll search for weather information for you.', 'text'),
('test-session-2', 'tool', 'Weather data retrieved successfully', 'tool_result'); 