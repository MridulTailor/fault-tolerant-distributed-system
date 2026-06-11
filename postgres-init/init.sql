CREATE TABLE IF NOT EXISTS sessions_history (
    id VARCHAR(36) PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);
