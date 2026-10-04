import mysql.connector
from mysql.connector import Error

def test_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='eventflow_db',
            user='root',
            password=''
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Event")
            events = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Participant")
            participants = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Registration")
            registrations = cursor.fetchone()[0]
            
            print(f"DB Connection: SUCCESS")
            print(f"Total Events: {events}")
            print(f"Total Participants: {participants}")
            print(f"Total Registrations: {registrations}")
            
            cursor.close()
            connection.close()
    except Error as e:
        print(f"DB Connection: FAILED\nError: {e}")

if __name__ == "__main__":
    test_db()
