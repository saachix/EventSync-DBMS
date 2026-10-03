USE eventflow_db;

-- =========================================================
-- BASIC RETRIEVAL
-- =========================================================

-- 1. Display all events
SELECT *
FROM Event;


-- 2. Display currently open events
SELECT
    event_id,
    event_name,
    event_date,
    registration_fee
FROM Event
WHERE status = 'Open';


-- 3. Display paid events
SELECT
    event_name,
    registration_fee
FROM Event
WHERE registration_fee > 0;


-- 4. Sort events by date
SELECT
    event_name,
    event_date
FROM Event
ORDER BY event_date ASC;


-- =========================================================
-- JOINS
-- =========================================================

-- 5. Events with their categories
SELECT
    e.event_name,
    c.category_name,
    e.event_date,
    e.max_capacity
FROM Event e
INNER JOIN Category c
    ON e.category_id = c.category_id;


-- 6. Events with their coordinators
SELECT
    e.event_name,
    c.coordinator_name,
    c.email
FROM Event e
INNER JOIN Coordinator c
    ON e.coordinator_id = c.coordinator_id;


-- 7. Events with category and coordinator
SELECT
    e.event_name,
    c.category_name,
    co.coordinator_name,
    e.event_date
FROM Event e
JOIN Category c
    ON e.category_id = c.category_id
JOIN Coordinator co
    ON e.coordinator_id = co.coordinator_id;


-- 8. Sessions with their venues
SELECT
    s.session_title,
    e.event_name,
    v.venue_name,
    s.session_date,
    s.start_time,
    s.end_time,
    s.expected_attendance
FROM Session s
JOIN Event e
    ON s.event_id = e.event_id
JOIN Venue v
    ON s.venue_id = v.venue_id;


-- 9. Sessions with their speakers
SELECT
    s.session_title,
    sp.speaker_name,
    ss.speaker_role
FROM Session s
JOIN Session_Speaker ss
    ON s.session_id = ss.session_id
JOIN Speaker sp
    ON ss.speaker_id = sp.speaker_id;


-- =========================================================
-- AGGREGATE FUNCTIONS
-- =========================================================

-- 10. Count registrations for each event
SELECT
    e.event_name,
    COUNT(r.registration_id) AS total_registrations
FROM Event e
LEFT JOIN Registration r
    ON e.event_id = r.event_id
GROUP BY e.event_id, e.event_name;


-- 11. Count participants for each event
SELECT
    e.event_name,
    COUNT(DISTINCT r.participant_id) AS participant_count
FROM Event e
JOIN Registration r
    ON e.event_id = r.event_id
GROUP BY e.event_id, e.event_name;


-- 12. Total payment collected per event
SELECT
    e.event_name,
    SUM(p.amount) AS total_revenue
FROM Event e
JOIN Registration r
    ON e.event_id = r.event_id
JOIN Payment p
    ON r.registration_id = p.registration_id
WHERE p.payment_status = 'Paid'
GROUP BY e.event_id, e.event_name;


-- 13. Average feedback rating per event
SELECT
    e.event_name,
    AVG(f.rating) AS average_rating
FROM Event e
JOIN Registration r
    ON e.event_id = r.event_id
JOIN Feedback f
    ON r.registration_id = f.registration_id
GROUP BY e.event_id, e.event_name;


-- =========================================================
-- GROUP BY / HAVING
-- =========================================================

-- 14. Events with more than two registrations
SELECT
    e.event_name,
    COUNT(r.registration_id) AS total_registrations
FROM Event e
JOIN Registration r
    ON e.event_id = r.event_id
GROUP BY e.event_id, e.event_name
HAVING COUNT(r.registration_id) > 2;


-- =========================================================
-- SUBQUERIES
-- =========================================================

-- 15. Events with registration fee above the average
SELECT
    event_name,
    registration_fee
FROM Event
WHERE registration_fee > (
    SELECT AVG(registration_fee)
    FROM Event
);


-- 16. Participants registered for the AI Innovation Workshop
SELECT
    participant_name,
    email
FROM Participant
WHERE participant_id IN (
    SELECT participant_id
    FROM Registration
    WHERE event_id = (
        SELECT event_id
        FROM Event
        WHERE event_name = 'AI Innovation Workshop'
    )
);


-- =========================================================
-- REGISTRATION / CAPACITY REPORTS
-- =========================================================

-- 17. Registration summary
SELECT
    e.event_name,
    e.max_capacity,
    COUNT(r.registration_id) AS registered,
    e.max_capacity - COUNT(r.registration_id) AS seats_remaining
FROM Event e
LEFT JOIN Registration r
    ON e.event_id = r.event_id
GROUP BY
    e.event_id,
    e.event_name,
    e.max_capacity;


-- 18. Find available venues with sufficient capacity
SELECT
    venue_id,
    venue_name,
    capacity
FROM Venue
WHERE capacity >= 80
AND availability_status = 'Available'
ORDER BY capacity ASC;


-- =========================================================
-- ATTENDANCE REPORTS
-- =========================================================

-- 19. Participants who attended at least one session
SELECT DISTINCT
    p.participant_name,
    p.email
FROM Participant p
JOIN Registration r
    ON p.participant_id = r.participant_id
JOIN Attendance a
    ON r.registration_id = a.registration_id
WHERE a.attendance_status = 'Present';


-- 20. Attendance summary
SELECT
    e.event_name,
    p.participant_name,
    COUNT(a.attendance_id) AS total_sessions,
    SUM(
        CASE
            WHEN a.attendance_status = 'Present'
            THEN 1
            ELSE 0
        END
    ) AS sessions_attended
FROM Registration r
JOIN Participant p
    ON r.participant_id = p.participant_id
JOIN Event e
    ON r.event_id = e.event_id
JOIN Attendance a
    ON r.registration_id = a.registration_id
GROUP BY
    r.registration_id,
    e.event_name,
    p.participant_name;


-- =========================================================
-- WAITLIST REPORT
-- =========================================================

-- 21. Display waiting participants
SELECT
    e.event_name,
    p.participant_name,
    w.position,
    w.status
FROM Waitlist w
JOIN Event e
    ON w.event_id = e.event_id
JOIN Participant p
    ON w.participant_id = p.participant_id
WHERE w.status = 'Waiting'
ORDER BY
    e.event_id,
    w.position;


-- =========================================================
-- VENUE VALIDATION
-- =========================================================

-- 22. Check for sessions exceeding venue capacity
SELECT
    s.session_title,
    v.venue_name,
    s.expected_attendance,
    v.capacity
FROM Session s
JOIN Venue v
    ON s.venue_id = v.venue_id
WHERE s.expected_attendance > v.capacity;


-- =========================================================
-- VENUE SCHEDULE REPORT
-- =========================================================

-- 23. Complete venue schedule
SELECT
    v.venue_name,
    s.session_date,
    s.start_time,
    s.end_time,
    e.event_name,
    s.session_title
FROM Venue v
JOIN Session s
    ON v.venue_id = s.venue_id
JOIN Event e
    ON s.event_id = e.event_id
ORDER BY
    v.venue_name,
    s.session_date,
    s.start_time;


-- =========================================================
-- PAYMENT REPORT
-- =========================================================

-- 24. Payment report
SELECT
    p.payment_id,
    participant.participant_name,
    e.event_name,
    p.amount,
    p.payment_method,
    p.payment_status
FROM Payment p
JOIN Registration r
    ON p.registration_id = r.registration_id
JOIN Participant participant
    ON r.participant_id = participant.participant_id
JOIN Event e
    ON r.event_id = e.event_id;


-- =========================================================
-- CERTIFICATE ELIGIBILITY
-- Project-defined threshold: 75% attendance
-- =========================================================

-- 25. Participants meeting the 75% attendance threshold
SELECT
    r.registration_id,
    p.participant_name,
    e.event_name,
    COUNT(a.attendance_id) AS total_sessions,

    SUM(
        CASE
            WHEN a.attendance_status = 'Present'
            THEN 1
            ELSE 0
        END
    ) AS sessions_attended,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN a.attendance_status = 'Present'
                THEN 1
                ELSE 0
            END
        ) / COUNT(a.attendance_id),
        2
    ) AS attendance_percentage

FROM Registration r
JOIN Participant p
    ON r.participant_id = p.participant_id
JOIN Event e
    ON r.event_id = e.event_id
JOIN Attendance a
    ON r.registration_id = a.registration_id

GROUP BY
    r.registration_id,
    p.participant_name,
    e.event_name

HAVING
    100.0 *
    SUM(
        CASE
            WHEN a.attendance_status = 'Present'
            THEN 1
            ELSE 0
        END
    ) / COUNT(a.attendance_id) >= 75;


-- =========================================================
-- VALIDATION QUERIES
-- =========================================================

-- 26. Check for duplicate registrations
SELECT
    event_id,
    participant_id,
    COUNT(*) AS registration_count
FROM Registration
GROUP BY event_id, participant_id
HAVING COUNT(*) > 1;


-- 27. Check for invalid venue capacity
SELECT
    s.session_id,
    s.session_title,
    v.venue_name,
    s.expected_attendance,
    v.capacity
FROM Session s
JOIN Venue v
    ON s.venue_id = v.venue_id
WHERE s.expected_attendance > v.capacity;


-- =========================================================
-- VIEWS
-- =========================================================

-- 28. Event registration summary view
CREATE OR REPLACE VIEW Event_Registration_Summary AS
SELECT
    e.event_id,
    e.event_name,
    e.max_capacity,
    COUNT(r.registration_id) AS total_registrations,
    e.max_capacity - COUNT(r.registration_id) AS seats_remaining
FROM Event e
LEFT JOIN Registration r
    ON e.event_id = r.event_id
GROUP BY
    e.event_id,
    e.event_name,
    e.max_capacity;


-- 29. Venue schedule view
CREATE OR REPLACE VIEW Venue_Schedule AS
SELECT
    v.venue_name,
    s.session_date,
    s.start_time,
    s.end_time,
    e.event_name,
    s.session_title
FROM Venue v
JOIN Session s
    ON v.venue_id = s.venue_id
JOIN Event e
    ON s.event_id = e.event_id;


-- 30. Attendance summary view
CREATE OR REPLACE VIEW Attendance_Summary AS
SELECT
    e.event_name,
    p.participant_name,
    COUNT(a.attendance_id) AS total_sessions,
    SUM(
        CASE
            WHEN a.attendance_status = 'Present'
            THEN 1
            ELSE 0
        END
    ) AS sessions_attended
FROM Registration r
JOIN Participant p
    ON r.participant_id = p.participant_id
JOIN Event e
    ON r.event_id = e.event_id
JOIN Attendance a
    ON r.registration_id = a.registration_id
GROUP BY
    r.registration_id,
    e.event_name,
    p.participant_name;


-- 31. Payment summary view
CREATE OR REPLACE VIEW Payment_Summary AS
SELECT
    e.event_name,
    COUNT(p.payment_id) AS payment_count,
    SUM(p.amount) AS total_amount
FROM Event e
JOIN Registration r
    ON e.event_id = r.event_id
JOIN Payment p
    ON r.registration_id = p.registration_id
WHERE p.payment_status = 'Paid'
GROUP BY
    e.event_id,
    e.event_name;


-- 32. Feedback report view
CREATE OR REPLACE VIEW Event_Feedback_Report AS
SELECT
    e.event_name,
    COUNT(f.feedback_id) AS feedback_count,
    ROUND(AVG(f.rating), 2) AS average_rating
FROM Event e
JOIN Registration r
    ON e.event_id = r.event_id
JOIN Feedback f
    ON r.registration_id = f.registration_id
GROUP BY
    e.event_id,
    e.event_name;


-- 33. Display the registration summary view
SELECT *
FROM Event_Registration_Summary;


-- 34. Display the venue schedule view
SELECT *
FROM Venue_Schedule;


-- 35. Display the attendance summary view
SELECT *
FROM Attendance_Summary;


-- 36. Display the payment summary view
SELECT *
FROM Payment_Summary;


-- 37. Display the feedback report view
SELECT *
FROM Event_Feedback_Report;
