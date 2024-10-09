
-- Create schema
CREATE SCHEMA IF NOT EXISTS STORMDATA;

-- Create tables
CREATE TABLE IF NOT EXISTS STORMDATA.students (
    student_id SERIAL PRIMARY KEY,
    gender VARCHAR(10),
    age INTEGER
);

CREATE TABLE IF NOT EXISTS STORMDATA.academic_performance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES STORMDATA.students(student_id),  
    jamb_score DECIMAL,
    mock_exam_score DECIMAL
);

CREATE TABLE IF NOT EXISTS STORMDATA.attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES STORMDATA.students(student_id),  
    attendance_rate INTEGER
);

CREATE TABLE IF NOT EXISTS STORMDATA.health_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES STORMDATA.students(student_id),  
    physical_health TEXT,
    mental_health TEXT,
    sick_days INTEGER
);

CREATE TABLE IF NOT EXISTS STORMDATA.teacher_feedback (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES STORMDATA.students(student_id),  
    access_to_teachers BOOLEAN
);

CREATE TABLE IF NOT EXISTS STORMDATA.family_background (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES STORMDATA.students(student_id),  
    parent_education_level VARCHAR(100),
    parent_occupation VARCHAR(100),
    attention_to_children INTEGER
);

CREATE TABLE IF NOT EXISTS STORMDATA.classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS STORMDATA.student_classes (
    student_id INTEGER REFERENCES STORMDATA.students(student_id), 
    class_id INTEGER REFERENCES STORMDATA.classes(class_id),        
    PRIMARY KEY(student_id, class_id)
);

-- Optional: CREATE USER and GRANT privileges
-- CREATE USER analyst_user WITH PASSWORD 'password';
-- GRANT CONNECT ON DATABASE datafest TO analyst_user;
-- GRANT USAGE ON SCHEMA STORMDATA TO analyst_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA STORMDATA TO analyst_user;
