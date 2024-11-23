CREATE TABLE User (
    student_id CHAR(10) NOT NULL,
    password VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_admin BOOLEAN NOT NULL,
    email VARCHAR(50) NOT NULL,
    PRIMARY KEY (student_id)
);

CREATE TABLE Studyroom (
    idx INT AUTO_INCREMENT,
    student_id CHAR(10) NOT NULL,
    room_number INT NOT NULL,
    time DATETIME NOT NULL,
    PRIMARY KEY (idx),
    FOREIGN KEY (student_id) REFERENCES User(student_id)
);

CREATE TABLE Reservation (
    idx INT AUTO_INCREMENT,
    student_id CHAR(10) NOT NULL,
    room_number INT NOT NULL,
    time DATETIME NOT NULL,
    PRIMARY KEY (idx),
    FOREIGN KEY (student_id) REFERENCES User(student_id)
);

CREATE TABLE Seat (
    seat_number INT NOT NULL,
    student_id CHAR(10), 
    time DATETIME,
    is_reserved BOOLEAN NOT NULL, 
    count INT NOT NULL,
    PRIMARY KEY (seat_number),
    FOREIGN KEY (student_id) REFERENCES User(student_id)
);