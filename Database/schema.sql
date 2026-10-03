CREATE DATABASE IF NOT EXISTS eventflow_db;
USE eventflow_db;

CREATE TABLE Category (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE Coordinator (
    coordinator_id INT PRIMARY KEY AUTO_INCREMENT,
    coordinator_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15)
);

CREATE TABLE Event (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    event_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    coordinator_id INT NOT NULL,
    event_date DATE NOT NULL,
    description VARCHAR(500),
    max_capacity INT NOT NULL CHECK (max_capacity > 0),
    registration_fee DECIMAL(10,2) DEFAULT 0
        CHECK (registration_fee >= 0),
    status VARCHAR(30) DEFAULT 'Open',

    FOREIGN KEY (category_id)
        REFERENCES Category(category_id),

    FOREIGN KEY (coordinator_id)
        REFERENCES Coordinator(coordinator_id)
);

CREATE TABLE Venue (
    venue_id INT PRIMARY KEY AUTO_INCREMENT,
    venue_name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    capacity INT NOT NULL CHECK (capacity > 0),
    availability_status VARCHAR(30) DEFAULT 'Available'
);

CREATE TABLE Session (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    venue_id INT NOT NULL,
    session_title VARCHAR(150) NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    expected_attendance INT DEFAULT 0
        CHECK (expected_attendance >= 0),

    FOREIGN KEY (event_id)
        REFERENCES Event(event_id),

    FOREIGN KEY (venue_id)
        REFERENCES Venue(venue_id),

    CHECK (end_time > start_time)
);

CREATE TABLE Speaker (
    speaker_id INT PRIMARY KEY AUTO_INCREMENT,
    speaker_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    organization VARCHAR(150),
    specialization VARCHAR(150)
);

CREATE TABLE Session_Speaker (
    session_id INT,
    speaker_id INT,
    speaker_role VARCHAR(100),

    PRIMARY KEY (session_id, speaker_id),

    FOREIGN KEY (session_id)
        REFERENCES Session(session_id)
        ON DELETE CASCADE,

    FOREIGN KEY (speaker_id)
        REFERENCES Speaker(speaker_id)
        ON DELETE CASCADE
);

CREATE TABLE Participant (
    participant_id INT PRIMARY KEY AUTO_INCREMENT,
    participant_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    department VARCHAR(100),
    year_of_study INT CHECK (year_of_study > 0)
);

CREATE TABLE Registration (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    participant_id INT NOT NULL,
    registration_date DATE NOT NULL,
    registration_status VARCHAR(30) DEFAULT 'Confirmed',

    FOREIGN KEY (event_id)
        REFERENCES Event(event_id),

    FOREIGN KEY (participant_id)
        REFERENCES Participant(participant_id),

    UNIQUE (event_id, participant_id)
);

CREATE TABLE Waitlist (
    waitlist_id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    participant_id INT NOT NULL,
    waitlist_date DATE NOT NULL,
    position INT NOT NULL CHECK (position > 0),
    status VARCHAR(30) DEFAULT 'Waiting',

    FOREIGN KEY (event_id)
        REFERENCES Event(event_id),

    FOREIGN KEY (participant_id)
        REFERENCES Participant(participant_id),

    UNIQUE (event_id, participant_id)
);

CREATE TABLE Payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL
        CHECK (amount >= 0),
    payment_date DATE,
    payment_method VARCHAR(30),
    payment_status VARCHAR(30) DEFAULT 'Pending',

    FOREIGN KEY (registration_id)
        REFERENCES Registration(registration_id)
);

CREATE TABLE Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL,
    session_id INT NOT NULL,
    attendance_status VARCHAR(20) NOT NULL,
    check_in_time TIME,

    FOREIGN KEY (registration_id)
        REFERENCES Registration(registration_id),

    FOREIGN KEY (session_id)
        REFERENCES Session(session_id),

    UNIQUE (registration_id, session_id)
);

CREATE TABLE Certificate (
    certificate_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL,
    certificate_date DATE,
    certificate_type VARCHAR(50),
    certificate_status VARCHAR(30) DEFAULT 'Eligible',

    FOREIGN KEY (registration_id)
        REFERENCES Registration(registration_id),

    UNIQUE (registration_id)
);

CREATE TABLE Feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    registration_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comments VARCHAR(500),
    feedback_date DATE,

    FOREIGN KEY (registration_id)
        REFERENCES Registration(registration_id),

    UNIQUE (registration_id)
);
