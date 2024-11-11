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

# 3. Tworzenie tabel "authors" i "books":
create_authors_sql = """
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date TEXT
);
"""

create_books_sql = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    genre TEXT,
    publish_year INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors (id)
);
"""

# 4. Funkcje do dodawania danych do tabel:
def add_author(conn, author):
    """ Dodaje nowego autora do tabeli 'authors' """
    sql = '''INSERT INTO authors(first_name, last_name, birth_date) VALUES(?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, author)
    conn.commit()
    return cur.lastrowid

def add_book(conn, book):
    """ Dodaje nową książkę do tabeli 'books' """
    sql = '''INSERT INTO books(author_id, title, genre, publish_year) VALUES(?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, book)
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
def update_book(conn, book_id, **kwargs):
    """ Aktualizuje książkę na podstawie id """
    cur = conn.cursor()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = tuple(kwargs.values()) + (book_id,)
    sql = f"UPDATE books SET {fields} WHERE id=?"
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
    db_file = "library.db"
    conn = create_connection(db_file)

    if conn is not None:
        # Tworzenie tabel
        execute_sql(conn, create_authors_sql)
        execute_sql(conn, create_books_sql)

        # Dodawanie przykładowego autora
        author = ("J.K.", "Rowling", "1965-07-31")
        author_id = add_author(conn, author)

        # Dodawanie przykładowej książki
        book = (author_id, "Harry Potter and the Philosopher's Stone", "Fantasy", 1997)
        book_id = add_book(conn, book)

        # Pobieranie wszystkich autorów
        print("Autorzy:", select_all(conn, "authors"))

        # Pobieranie wszystkich książek
        print("Książki:", select_all(conn, "books"))

        # Aktualizacja książki
        update_book(conn, book_id, genre="Young Adult Fantasy")

        # Pobieranie książki po gatunku
        print("Książki o gatunku 'Young Adult Fantasy':", select_where(conn, "books", genre="Young Adult Fantasy"))

        # Usuwanie książki
        delete_where(conn, "books", id=book_id)

        # Sprawdzenie, czy książka została usunięta
        print("Wszystkie książki po usunięciu:", select_all(conn, "books"))

        conn.close()
