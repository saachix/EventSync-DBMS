USE eventflow_db;

-- 1. Categories
INSERT INTO Category
(category_name, description)
VALUES
('Workshop', 'Technical and practical workshops'),
('Seminar', 'Academic and professional seminars'),
('Cultural', 'Cultural and creative events'),
('Sports', 'Sports and recreational events');


-- 2. Coordinators
INSERT INTO Coordinator
(coordinator_name, email, phone)
VALUES
('Ananya Sharma', 'ananya@woxsen.edu.in', '9876543210'),
('Rahul Mehta', 'rahul@woxsen.edu.in', '9876543211'),
('Priya Nair', 'priya@woxsen.edu.in', '9876543212');


-- 3. Events
INSERT INTO Event
(event_name, category_id, coordinator_id, event_date,
 description, max_capacity, registration_fee, status)
VALUES
('AI Innovation Workshop', 1, 1, '2026-11-10',
 'Hands-on workshop on artificial intelligence',
 100, 200.00, 'Open'),

('Future Tech Seminar', 2, 2, '2026-11-15',
 'Seminar covering emerging technologies',
 200, 100.00, 'Open'),

('Cultural Fest 2026', 3, 3, '2026-12-05',
 'Annual university cultural festival',
 500, 0.00, 'Open');


-- 4. Venues
INSERT INTO Venue
(venue_name, location, capacity, availability_status)
VALUES
('Main Auditorium', 'Academic Block A', 300, 'Available'),
('Seminar Hall 1', 'Academic Block B', 150, 'Available'),
('Innovation Lab', 'Technology Block', 100, 'Available'),
('Open Amphitheatre', 'Central Campus', 500, 'Available');


-- 5. Speakers
INSERT INTO Speaker
(speaker_name, email, organization, specialization)
VALUES
('Dr. Arjun Rao', 'arjun@example.com',
 'Tech Research Institute', 'Artificial Intelligence'),

('Neha Kapoor', 'neha@example.com',
 'Innovate Labs', 'Machine Learning'),

('Vikram Singh', 'vikram@example.com',
 'FutureTech Solutions', 'Cloud Computing');


-- 6. Participants
INSERT INTO Participant
(participant_name, email, phone, department, year_of_study)
VALUES
('Aarav Patel', 'aarav@example.com', '9000000001',
 'Computer Science', 2),

('Meera Shah', 'meera@example.com', '9000000002',
 'Computer Science', 2),

('Rohan Gupta', 'rohan@example.com', '9000000003',
 'Information Technology', 3),

('Ishita Rao', 'ishita@example.com', '9000000004',
 'Electronics', 2),

('Kabir Joshi', 'kabir@example.com', '9000000005',
 'Computer Science', 4);


-- 7. Sessions
INSERT INTO Session
(event_id, venue_id, session_title, session_date,
 start_time, end_time, expected_attendance)
VALUES
(1, 3, 'Introduction to AI',
 '2026-11-10', '10:00:00', '11:30:00', 80),

(1, 3, 'Machine Learning Workshop',
 '2026-11-10', '12:00:00', '14:00:00', 80),

(2, 2, 'Emerging Technologies',
 '2026-11-15', '10:00:00', '12:00:00', 120),

(3, 4, 'Cultural Performances',
 '2026-12-05', '18:00:00', '21:00:00', 400);


-- 8. Session-Speaker assignments
INSERT INTO Session_Speaker
(session_id, speaker_id, speaker_role)
VALUES
(1, 1, 'Keynote Speaker'),
(1, 2, 'Guest Speaker'),
(2, 2, 'Workshop Instructor'),
(3, 3, 'Guest Speaker');


-- 9. Registrations
INSERT INTO Registration
(event_id, participant_id, registration_date, registration_status)
VALUES
(1, 1, '2026-10-20', 'Confirmed'),
(1, 2, '2026-10-21', 'Confirmed'),
(1, 3, '2026-10-21', 'Confirmed'),
(2, 1, '2026-10-22', 'Confirmed'),
(2, 4, '2026-10-23', 'Confirmed'),
(3, 5, '2026-11-01', 'Confirmed');


-- 10. Waitlist
INSERT INTO Waitlist
(event_id, participant_id, waitlist_date, position, status)
VALUES
(1, 4, '2026-10-25', 1, 'Waiting'),
(1, 5, '2026-10-26', 2, 'Waiting');


-- 11. Payments
INSERT INTO Payment
(registration_id, amount, payment_date,
 payment_method, payment_status)
VALUES
(1, 200.00, '2026-10-20', 'UPI', 'Paid'),
(2, 200.00, '2026-10-21', 'Card', 'Paid'),
(3, 200.00, '2026-10-21', 'UPI', 'Paid'),
(4, 100.00, '2026-10-22', 'UPI', 'Paid'),
(5, 100.00, '2026-10-23', 'Card', 'Paid'),
(6, 0.00, '2026-11-01', 'Free', 'Paid');


-- 12. Attendance
INSERT INTO Attendance
(registration_id, session_id, attendance_status, check_in_time)
VALUES
(1, 1, 'Present', '09:55:00'),
(1, 2, 'Present', '11:55:00'),
(2, 1, 'Present', '10:02:00'),
(2, 2, 'Absent', NULL),
(3, 1, 'Present', '09:58:00'),
(3, 2, 'Present', '12:01:00'),
(4, 3, 'Present', '09:50:00');


-- 13. Certificates
INSERT INTO Certificate
(registration_id, certificate_date,
 certificate_type, certificate_status)
VALUES
(1, '2026-11-10', 'Participation', 'Issued'),
(3, '2026-11-10', 'Participation', 'Issued');


-- 14. Feedback
INSERT INTO Feedback
(registration_id, rating, comments, feedback_date)
VALUES
(1, 5, 'Very informative workshop', '2026-11-10'),
(2, 4, 'Good session and practical examples', '2026-11-10'),
(4, 5, 'Excellent seminar', '2026-11-15');