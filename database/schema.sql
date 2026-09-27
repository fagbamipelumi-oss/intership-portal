-- Internship & Recruitment Portal — Database Schema
-- Run: mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS internship_portal
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE internship_portal;

-- ============================================================
-- Core identity table. Every user (student, employer, admin)
-- has exactly one row here; role-specific data lives in
-- students / employers.
-- ============================================================
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('student', 'employer', 'admin') NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL UNIQUE,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    course        VARCHAR(120),
    cgpa          DECIMAL(3,2),               -- e.g. 4.50 on a 5.0 scale
    skills        JSON,                       -- e.g. ["Python", "Django", "SQL"]
    qualifications TEXT,                       -- certifications, degrees, achievements
    experience    TEXT,                        -- prior work/internship experience
    interests     TEXT,                        -- career interests, e.g. "Web Development"
    bio           TEXT,
    cv_file_path  VARCHAR(255),
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE employers (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL UNIQUE,
    company_name  VARCHAR(150) NOT NULL,
    industry      VARCHAR(100),
    location      VARCHAR(150),
    description   TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE jobs (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    employer_id      INT NOT NULL,
    title            VARCHAR(150) NOT NULL,
    description      TEXT NOT NULL,
    required_skills  JSON,                    -- e.g. ["Python", "Django"]
    qualifications    TEXT,
    location         VARCHAR(150),
    job_type         ENUM('internship', 'full-time', 'part-time') DEFAULT 'internship',
    min_cgpa         DECIMAL(3,2) DEFAULT 0.00,
    status           ENUM('open', 'closed', 'flagged') DEFAULT 'open',
    deadline         DATE,
    posted_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES employers(id) ON DELETE CASCADE,
    INDEX idx_jobs_status (status),
    INDEX idx_jobs_type (job_type)
);

CREATE TABLE applications (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT NOT NULL,
    job_id       INT NOT NULL,
    status       ENUM('pending', 'reviewed', 'shortlisted', 'rejected') DEFAULT 'pending',
    applied_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (student_id, job_id) -- can't apply twice to the same job
);

CREATE TABLE messages (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    sender_id    INT NOT NULL,
    receiver_id  INT NOT NULL,
    subject      VARCHAR(150),
    message_body TEXT NOT NULL,
    is_read      BOOLEAN DEFAULT FALSE,
    sent_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- Supports the collaborative-filtering half of the recommender:
-- tracks implicit interest signals (views/applies) as a
-- student-job interaction matrix.
-- ============================================================
CREATE TABLE job_interactions (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT NOT NULL,
    job_id       INT NOT NULL,
    interaction  ENUM('viewed', 'applied', 'saved') NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_interactions_student (student_id)
);

-- Seed an admin account (change password on first login)
-- password below is a bcrypt hash of "changeme123" — replace before deployment
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@internshipportal.local',
        '$2b$12$KIXQb0Qy1234567890abcdEuJ6Z8Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z1Z', 'admin');
