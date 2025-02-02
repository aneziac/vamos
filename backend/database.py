import sqlite3
from typing import Optional
from uuid import UUID

from task import Task


def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def update_task(task: Task):
    """Update task in the database."""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO tasks (id, status)
        VALUES (?, ?)
    ''', (str(task.id), str(task.status)))
    conn.commit()
    conn.close()


def get_task(task_id: UUID) -> Optional[Task]:
    """Retrieve task from the database."""
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (str(task_id),))
    row = cursor.fetchone()
    conn.close()

    if row:
        return Task(**row)
    else:
        return None
