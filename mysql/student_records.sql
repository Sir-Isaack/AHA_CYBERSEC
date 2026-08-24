USE student_records;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    email VARCHAR(100)
);

INSERT INTO students (name, age, email) VALUES
('John Kamau', 23, 'john.kama321@gmail.com'),
('Brian Smith', 22, 'brian.smith2556@gmail.com'),
('Carol Kimani', 19, 'carol.kim343@gmail.com');
