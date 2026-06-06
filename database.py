import sqlite3

DB_FILE="events.db"
def get_connection():
    conn=sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT    NOT NULL UNIQUE,
            total_seats    INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            event_date     TEXT    NOT NULL,
            created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name     TEXT    NOT NULL,
            event_id      INTEGER NOT NULL REFERENCES events(id),
            status        TEXT    NOT NULL DEFAULT 'active',
            registered_at TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_name, event_id)
        )
    """)

    conn.commit()
    conn.close()