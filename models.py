from typing import Optional, List, Dict
import datetime
import db
import utils


class UserManager:
    @staticmethod
    def find_user(username: str) -> Optional[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
                return cursor.fetchone()
        finally:
            connection.close()

    @staticmethod
    def create_user(username: str, password: str, role: str = 'admin') -> None:
        password_hash = utils.hash_password(password)
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)',
                    (username, password_hash, role),
                )
                connection.commit()
        finally:
            connection.close()


class BookManager:
    @staticmethod
    def add_book(title: str, author: str, isbn: str, genre: str, quantity: int) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO books (title, author, isbn, genre, total_quantity, available_quantity) VALUES (%s, %s, %s, %s, %s, %s)',
                    (title, author, isbn, genre, quantity, quantity),
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def update_book(book_id: int, title: str, author: str, isbn: str, genre: str, quantity: int) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT total_quantity, available_quantity FROM books WHERE id=%s', (book_id,))
                current = cursor.fetchone()
                if current is None:
                    raise ValueError('Book not found')
                old_total = current[0]
                old_available = current[1]
                delta = quantity - old_total
                new_available = old_available + delta
                if new_available < 0:
                    raise ValueError('Cannot reduce total quantity below borrowed count')
                cursor.execute(
                    'UPDATE books SET title=%s, author=%s, isbn=%s, genre=%s, total_quantity=%s, available_quantity=%s WHERE id=%s',
                    (title, author, isbn, genre, quantity, new_available, book_id),
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def delete_book(book_id: int) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM books WHERE id=%s', (book_id,))
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def search_books(term: str) -> List[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                if not term:
                    cursor.execute('SELECT * FROM books')
                else:
                    like_term = f'%{term}%'
                    cursor.execute(
                        'SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s',
                        (like_term, like_term, like_term),
                    )
                return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def get_book(book_id: int) -> Optional[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM books WHERE id=%s', (book_id,))
                return cursor.fetchone()
        finally:
            connection.close()


class BorrowerManager:
    @staticmethod
    def add_borrower(membership_id: str, name: str, contact: str, email: str) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO borrowers (membership_id, name, contact, email) VALUES (%s, %s, %s, %s)',
                    (membership_id, name, contact, email),
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def update_borrower(borrower_id: int, name: str, contact: str, email: str) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'UPDATE borrowers SET name=%s, contact=%s, email=%s WHERE id=%s',
                    (name, contact, email, borrower_id),
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def delete_borrower(borrower_id: int) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM borrowers WHERE id=%s', (borrower_id,))
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def find_borrower_by_membership(membership_id: str) -> Optional[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM borrowers WHERE membership_id=%s', (membership_id,))
                return cursor.fetchone()
        finally:
            connection.close()

    @staticmethod
    def list_borrowers() -> List[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM borrowers ORDER BY name')
                return cursor.fetchall()
        finally:
            connection.close()


class TransactionManager:
    @staticmethod
    def borrow_book(borrower_id: int, book_id: int) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT available_quantity FROM books WHERE id=%s', (book_id,))
                book = cursor.fetchone()
                if book is None or book[0] < 1:
                    raise ValueError('Book is unavailable')
                due_date = utils.calculate_due_date()
                cursor.execute(
                    'INSERT INTO transactions (borrower_id, book_id, borrow_date, due_date) VALUES (%s, %s, %s, %s)',
                    (borrower_id, book_id, datetime.date.today(), due_date),
                )
                cursor.execute(
                    'UPDATE books SET available_quantity = available_quantity - 1 WHERE id=%s',
                    (book_id,),
                )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def return_book(transaction_id: int) -> None:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM transactions WHERE id=%s', (transaction_id,))
                txn = cursor.fetchone()
                if txn is None or txn['status'] == 'returned':
                    raise ValueError('Invalid transaction')
                return_date = datetime.date.today()
                fine_amount = utils.calculate_fine(txn['due_date'], return_date)
                cursor.execute(
                    'UPDATE transactions SET return_date=%s, fine_amount=%s, status=%s WHERE id=%s',
                    (return_date, fine_amount, 'returned', transaction_id),
                )
                cursor.execute('UPDATE books SET available_quantity = available_quantity + 1 WHERE id=%s', (txn['book_id'],))
                if fine_amount > 0:
                    cursor.execute(
                        'INSERT INTO fines (transaction_id, amount) VALUES (%s, %s)',
                        (transaction_id, fine_amount),
                    )
                connection.commit()
        finally:
            connection.close()

    @staticmethod
    def list_active_transactions() -> List[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT t.id, b.title, bw.name, t.borrow_date, t.due_date, "
                    "CASE WHEN t.status='borrowed' AND t.due_date < CURDATE() THEN 'overdue' ELSE t.status END AS status, "
                    "t.fine_amount "
                    "FROM transactions t "
                    "JOIN books b ON t.book_id=b.id "
                    "JOIN borrowers bw ON t.borrower_id=bw.id "
                    "WHERE t.status = 'borrowed'"
                )
                return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def get_transaction(transaction_id: int) -> Optional[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT * FROM transactions WHERE id=%s', (transaction_id,))
                return cursor.fetchone()
        finally:
            connection.close()


class ReportManager:
    @staticmethod
    def book_availability() -> List[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT title, author, genre, available_quantity, total_quantity FROM books')
                return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def borrower_activity() -> List[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT b.membership_id, b.name, COUNT(t.id) AS borrow_count FROM borrowers b LEFT JOIN transactions t ON b.id=t.borrower_id GROUP BY b.id')
                return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def fines_collected() -> List[Dict]:
        connection = db.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT f.id, t.id AS transaction_id, f.amount, f.paid, f.assessed_at FROM fines f JOIN transactions t ON f.transaction_id=t.id')
                return cursor.fetchall()
        finally:
            connection.close()
