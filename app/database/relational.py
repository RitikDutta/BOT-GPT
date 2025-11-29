# app/database/relational.py

import mysql.connector
from mysql.connector import Error

from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def get_server_connection():
    """
    connect to mysql server
    """
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_connection():
    """
    connect to database (db_name)
    """
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def ensure_database():
    """
    make sure database exists
    if not, create it
    """
    conn = None
    try:
        conn = get_server_connection()
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"ensured {DB_NAME} database")
    except Error as e:
        print(f"Error ensuring database: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()


def init_db_test():
    """
    create tables for test / local use
    tables:
      - sessions  (unique session_id and created time)
      - messages  (all messages mapped to session_id)
    """
    ensure_database()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("done")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    ON DELETE CASCADE
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database tables created")
    except Error as e:
        print(f"Error creating tables: {e}")


# simple alias so we can call init_db() from flask and keep name clean
def init_db():
    init_db_test()


def add_session(session_id: str):
    """
    add a new session_id
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO sessions (session_id) VALUES (%s)", (session_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[OK] Added session: {session_id}")
    except Error as e:
        print("[ERR] add_session:", e)


def list_sessions():
    """
    get all sessions
    returns list of (id, session_id, created_at)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, session_id, created_at FROM sessions")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print("[ERR] list_sessions:", e)
        return []


def add_message(session_id: str, role: str, content: str):
    """
    add one message for given session_id
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (session_id, role, content)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[OK] Added message to {session_id} ({role})")
    except Error as e:
        print("[ERR] add_message:", e)


def get_messages(session_id: str):
    """
    get all messages for a particular session_id
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role, content, created_at FROM messages WHERE session_id=%s ORDER BY id ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print("[ERR] get_messages:", e)
        return []


def delete_session(session_id: str):
    """
    delete complete session
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[OK] Deleted session: {session_id} (and all its messages)")
    except Error as e:
        print("[ERR] delete_session:", e)

def delete_from_message(session_id: str, message_id: int):
    """
    deleting a message in between will delete all message after that
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # check if this message exists for this session
        cursor.execute(
            "SELECT id FROM messages WHERE id = %s AND session_id = %s",
            (message_id, session_id),
        )
        row = cursor.fetchone()
        if not row:
            print(f"[WARN] no message with id={message_id} for session_id={session_id}")
            cursor.close()
            conn.close()
            return

        # delete from this message (and all after it)
        delete_sql = """
            DELETE FROM messages
            WHERE session_id = %s AND id >= %s
        """
        cursor.execute(delete_sql, (session_id, message_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[OK] deleted messages from id={message_id} onwards in session {session_id}")
    except Error as e:
        print("[ERR] delete_from_message:", e)
