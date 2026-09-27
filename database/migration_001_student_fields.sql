-- Migration: adds qualifications, experience, and interests fields to
-- the students table. Run this against your EXISTING database — it's
-- not needed for a fresh install using schema.sql, which already
-- includes these columns.
--
-- Run with:
--   Get-Content database\migration_001_student_fields.sql | mysql -u root -p internship_portal

USE internship_portal;

ALTER TABLE students
    ADD COLUMN qualifications TEXT AFTER skills,
    ADD COLUMN experience TEXT AFTER qualifications,
    ADD COLUMN interests TEXT AFTER experience;
