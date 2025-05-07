CREATE DATABASE IF NOT EXISTS Evaluation_data;
USE Evaluation_data;

CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT,
    answer TEXT,
    marks FLOAT
);

CREATE TABLE IF NOT EXISTS student_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT,
    student_answer TEXT,
    marks FLOAT
);


CREATE TABLE student_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    question_id INT,
    student_answer TEXT,
    marks FLOAT
);