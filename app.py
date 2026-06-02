import getpass
import sys
from typing import Optional
import models
import utils


def require_admin(user: dict) -> bool:
    return user.get('role') == 'admin'


def prompt_login() -> Optional[dict]:
    print('=== Library Management Login ===')
    username = input('Username: ').strip()
    password = getpass.getpass('Password: ').strip()
    user = models.UserManager.find_user(username)
    if user and user['password_hash'] == utils.hash_password(password):
        print(f'Welcome, {user["username"]}! Role: {user["role"]}')
        return user
    print('Invalid credentials. Use admin/admin123 on first run, or verify your app user credentials.')
    return None


def seed_admin():
    admin_username = 'admin'
    admin_password = 'admin123'
    if not models.UserManager.find_user(admin_username):
        try:
            models.UserManager.create_user(admin_username, admin_password, role='admin')
            print(f'Created default admin user: {admin_username} with password: {admin_password}')
        except Exception as exc:
            print(f'Admin seed failed: {exc}')


def show_menu(user: dict):
    print('\n=== Library System Menu ===')
    print('1. Add book')
    print('2. Update book')
    print('3. Delete book')
    print('4. Search books')
    print('5. Add borrower')
    print('6. Update borrower')
    print('7. Delete borrower')
    print('8. Borrow book')
    print('9. Return book')
    print('10. Active transactions')
    print('11. Book availability report')
    print('12. Borrower activity report')
    print('13. Fines collected report')
    print('0. Exit')


def read_int(prompt: str) -> int:
    return utils.parse_int(input(prompt).strip(), default=0)


def add_book():
    title = input('Title: ').strip()
    author = input('Author: ').strip()
    isbn = input('ISBN: ').strip()
    genre = input('Genre: ').strip()
    quantity = read_int('Quantity: ')
    if not title or not author or quantity < 1:
        print('Title, author, and quantity are required.')
        return
    models.BookManager.add_book(title, author, isbn, genre, quantity)
    print('Book added successfully.')


def update_book():
    book_id = read_int('Book ID: ')
    book = models.BookManager.get_book(book_id)
    if not book:
        print('Book not found.')
        return
    title = input(f'Title [{book["title"]}]: ').strip() or book['title']
    author = input(f'Author [{book["author"]}]: ').strip() or book['author']
    isbn = input(f'ISBN [{book["isbn"]}]: ').strip() or book['isbn']
    genre = input(f'Genre [{book["genre"]}]: ').strip() or book['genre']
    quantity = read_int(f'Quantity [{book["total_quantity"]}]: ') or book['total_quantity']
    try:
        models.BookManager.update_book(book_id, title, author, isbn, genre, quantity)
        print('Book updated successfully.')
    except Exception as exc:
        print(f'Update failed: {exc}')


def delete_book():
    book_id = read_int('Book ID: ')
    models.BookManager.delete_book(book_id)
    print('Book deleted successfully.')


def search_books():
    term = input('Search term (title, author, genre): ').strip()
    results = models.BookManager.search_books(term)
    if not results:
        print('No books found.')
        return
    print('\nSearch results:')
    for book in results:
        print(f"ID: {book['id']} | Title: {book['title']} | Author: {book['author']} | Genre: {book['genre']} | Available: {book['available_quantity']}/{book['total_quantity']}")


def add_borrower():
    membership_id = input('Membership ID: ').strip()
    name = input('Name: ').strip()
    contact = input('Contact: ').strip()
    email = input('Email: ').strip()
    if not membership_id or not name:
        print('Membership ID and name are required.')
        return
    models.BorrowerManager.add_borrower(membership_id, name, contact, email)
    print('Borrower added successfully.')


def update_borrower():
    borrower_id = read_int('Borrower ID: ')
    name = input('Name: ').strip()
    contact = input('Contact: ').strip()
    email = input('Email: ').strip()
    if not name:
        print('Name is required.')
        return
    models.BorrowerManager.update_borrower(borrower_id, name, contact, email)
    print('Borrower updated successfully.')


def delete_borrower():
    borrower_id = read_int('Borrower ID: ')
    models.BorrowerManager.delete_borrower(borrower_id)
    print('Borrower deleted successfully.')


def borrow_book():
    membership_id = input('Borrower membership ID: ').strip()
    borrower = models.BorrowerManager.find_borrower_by_membership(membership_id)
    if not borrower:
        print('Borrower not found.')
        return
    book_id = read_int('Book ID: ')
    try:
        models.TransactionManager.borrow_book(borrower['id'], book_id)
        print('Book borrowed successfully.')
    except Exception as exc:
        print(f'Borrow failed: {exc}')


def return_book():
    transaction_id = read_int('Transaction ID: ')
    try:
        models.TransactionManager.return_book(transaction_id)
        print('Book returned successfully.')
    except Exception as exc:
        print(f'Return failed: {exc}')


def active_transactions():
    transactions = models.TransactionManager.list_active_transactions()
    if not transactions:
        print('No active transactions.')
        return
    for txn in transactions:
        print(f"ID: {txn['id']} | Title: {txn['title']} | Borrower: {txn['name']} | Borrowed: {txn['borrow_date']} | Due: {txn['due_date']} | Status: {txn['status']} | Fine: {txn['fine_amount']}")


def book_availability_report():
    rows = models.ReportManager.book_availability()
    for row in rows:
        print(f"Title: {row['title']} | Author: {row['author']} | Genre: {row['genre']} | Available: {row['available_quantity']}/{row['total_quantity']}")


def borrower_activity_report():
    rows = models.ReportManager.borrower_activity()
    for row in rows:
        print(f"Membership: {row['membership_id']} | Name: {row['name']} | Borrowed count: {row['borrow_count']}")


def fines_collected_report():
    rows = models.ReportManager.fines_collected()
    for row in rows:
        print(f"Fine ID: {row['id']} | Transaction ID: {row['transaction_id']} | Amount: {row['amount']} | Paid: {row['paid']} | Assessed: {row['assessed_at']}")


def main():
    seed_admin()
    user = prompt_login()
    if not user:
        sys.exit(1)
    while True:
        show_menu(user)
        choice = input('Enter option: ').strip()
        if choice == '1':
            add_book()
        elif choice == '2':
            update_book()
        elif choice == '3':
            delete_book()
        elif choice == '4':
            search_books()
        elif choice == '5':
            add_borrower()
        elif choice == '6':
            update_borrower()
        elif choice == '7':
            delete_borrower()
        elif choice == '8':
            borrow_book()
        elif choice == '9':
            return_book()
        elif choice == '10':
            active_transactions()
        elif choice == '11':
            book_availability_report()
        elif choice == '12':
            borrower_activity_report()
        elif choice == '13':
            fines_collected_report()
        elif choice == '0':
            print('Goodbye.')
            break
        else:
            print('Invalid option.')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
