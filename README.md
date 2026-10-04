# EventSync-DBMS

## Event Registration and Venue Scheduling System

EventSync is a Database Management System project designed to manage event registration and venue scheduling for institutions.

The system manages events, venues, sessions, speakers, participants, registrations, waitlists, payments, attendance, certificates, and feedback through a normalized relational database and a Python-based desktop application.

## Key Features

- Event and category management
- Venue and session scheduling
- Speaker assignment
- Participant management
- Event registration
- Waitlist management
- Attendance tracking
- Payment management
- Certificate eligibility and generation
- Feedback collection
- Search, validation, and reporting
- Database constraints and validation

## Database Design

The database is implemented in MySQL/MariaDB and follows **Third Normal Form (3NF)**.

The system contains 14 tables:

1. CATEGORY
2. COORDINATOR
3. EVENT
4. VENUE
5. SESSION
6. SPEAKER
7. SESSION_SPEAKER
8. PARTICIPANT
9. REGISTRATION
10. WAITLIST
11. PAYMENT
12. ATTENDANCE
13. CERTIFICATE
14. FEEDBACK

Primary keys, foreign keys, unique constraints, NOT NULL constraints, CHECK constraints, and default values are used to maintain data integrity.

## Technology Stack

- **Python**
- **Tkinter** – Graphical User Interface
- **MySQL / MariaDB** – Database
- **XAMPP** – Local database server
- **mysql-connector-python** – Python-MySQL connectivity
- **Git & GitHub** – Version control

## Application Modules

The Python application provides the following modules:

- Dashboard
- Events
- Participants
- Sessions
- Registration & Waitlist
- Attendance
- Payments
- Certificates

The application follows a GUI-based architecture where Tkinter provides the interface and `mysql-connector-python` connects the application to the `eventflow_db` database.

## Repository Structure

```text
EventSync-DBMS/
│
├── application/
│   ├── database/
│   ├── gui/
│   ├── main.py
│   ├── test_db.py
│   └── test_stage*.py
│
├── Database/
│
├── DBMS_Review1.pdf
├── DBMS_Review2.pdf
├── DBMS_Review3.pdf
├── README.md
└── .gitignore