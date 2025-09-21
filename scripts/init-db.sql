-- Initialize PostgreSQL database for Resume Relevance System

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database (if not exists, this will be handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS resume_relevance;

-- Create a dedicated user for the application (optional)
-- This can be done via environment variables in docker-compose
-- CREATE USER resume_app WITH PASSWORD 'secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE resume_relevance TO resume_app;

-- Create indexes for better performance (will be created by application migration)
-- These are examples of what the application will create

-- Performance indexes for text search
-- CREATE INDEX IF NOT EXISTS idx_candidates_resume_text_gin 
--     ON candidates USING gin(to_tsvector('english', resume_text));

-- CREATE INDEX IF NOT EXISTS idx_job_descriptions_description_gin 
--     ON job_descriptions USING gin(to_tsvector('english', description));

-- Indexes for common queries
-- CREATE INDEX IF NOT EXISTS idx_evaluations_relevance_score 
--     ON evaluations(relevance_score DESC);

-- CREATE INDEX IF NOT EXISTS idx_evaluations_created_at 
--     ON evaluations(created_at DESC);

-- CREATE INDEX IF NOT EXISTS idx_candidates_skills_gin 
--     ON candidates USING gin(skills);

-- CREATE INDEX IF NOT EXISTS idx_job_descriptions_required_skills_gin 
--     ON job_descriptions USING gin(required_skills);

-- Set up some initial configuration
ALTER DATABASE resume_relevance SET timezone TO 'UTC';

-- Log successful initialization
\echo 'Database initialization completed successfully'