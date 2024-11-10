import sqlite3
from sqlite3 import Error

# 1. Funkcja do tworzenia połączenia z bazą danych:
def create_connection(db_file):
    """ Tworzy połączenie z bazą danych SQLite """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Połączono z bazą: {db_file}, wersja SQLite: {sqlite3.version}")
        return conn
    except Error as e:
        print(e)
    return conn

# 2. Funkcja do wykonania zapytania SQL:
def execute_sql(conn, sql):
    """ Wykonuje zapytanie SQL """
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

# 3. Tworzenie tabel "projects" i "tasks":
create_projects_sql = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    nazwa TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT
);
"""

create_tasks_sql = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    nazwa TEXT NOT NULL,
    opis TEXT,
    status TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
"""

# 4. Funkcje do dodawania danych do tabel:
def add_project(conn, project):
    """ Dodaje nowy projekt do tabeli 'projects' """
    sql = '''INSERT INTO projects(nazwa, start_date, end_date) VALUES(?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def add_task(conn, task):
    """ Dodaje nowe zadanie do tabeli 'tasks' """
    sql = '''INSERT INTO tasks(project_id, nazwa, opis, status, start_date, end_date) VALUES(?, ?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    return cur.lastrowid

# 5. Funkcje do pobierania danych:
def select_all(conn, table):
    """ Pobiera wszystkie wiersze z danej tabeli """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    return cur.fetchall()

def select_where(conn, table, **query):
    """ Pobiera dane z tabeli na podstawie zadanych kryteriów """
    cur = conn.cursor()
    qs = []
    values = ()
    for k, v in query.items():
        qs.append(f"{k}=?")
        values += (v,)
    q = " AND ".join(qs)
    cur.execute(f"SELECT * FROM {table} WHERE {q}", values)
    return cur.fetchall()

# 6. Funkcja do aktualizacji danych:
def update_task(conn, task_id, **kwargs):
    """ Aktualizuje zadanie na podstawie id """
    cur = conn.cursor()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = tuple(kwargs.values()) + (task_id,)
    sql = f"UPDATE tasks SET {fields} WHERE id=?"
    cur.execute(sql, values)
    conn.commit()

# 7. Funkcja do usuwania danych:
def delete_where(conn, table, **query):
    """ Usuwa dane z tabeli na podstawie zadanych kryteriów """
    cur = conn.cursor()
    qs = []
    values = ()
    for k, v in query.items():
        qs.append(f"{k}=?")
        values += (v,)
    q = " AND ".join(qs)
    sql = f"DELETE FROM {table} WHERE {q}"
    cur.execute(sql, values)
    conn.commit()

# 8. Główna część programu:
if __name__ == "__main__":
    db_file = "database.db"
    conn = create_connection(db_file)

    if conn is not None:
        # Tworzenie tabel
        execute_sql(conn, create_projects_sql)
        execute_sql(conn, create_tasks_sql)

        # Dodawanie przykładowego projektu
        project = ("Powtórka z angielskiego", "2020-05-11 00:00:00", "2020-05-13 00:00:00")
        project_id = add_project(conn, project)

        # Dodawanie przykładowego zadania
        task = (project_id, "Czasowniki regularne", "Zapamiętaj czasowniki ze strony 30", "started", "2020-05-11 12:00:00", "2020-05-11 15:00:00")
        task_id = add_task(conn, task)

        # Pobieranie wszystkich projektów
        print("Projekty:", select_all(conn, "projects"))

        # Pobieranie wszystkich zadań
        print("Zadania:", select_all(conn, "tasks"))

        # Aktualizacja zadania
        update_task(conn, task_id, status="ended", end_date="2020-05-11 15:30:00")

        # Pobieranie zadania po statusie
        print("Zadania ze statusem 'ended':", select_where(conn, "tasks", status="ended"))

        # Usuwanie zadania
        delete_where(conn, "tasks", id=task_id)

        # Sprawdzenie, czy zadanie zostało usunięte
        print("Wszystkie zadania po usunięciu:", select_all(conn, "tasks"))

        conn.close()
