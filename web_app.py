import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import models
import utils

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-me-for-production')


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = models.UserManager.find_user(username)
        if user and user['password_hash'] == utils.hash_password(password):
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Use admin/admin123 on first run, or verify your app user credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    books = models.BookManager.search_books('')
    borrowers = models.BorrowerManager.list_borrowers()
    active_transactions = models.TransactionManager.list_active_transactions()
    return render_template(
        'dashboard.html',
        books=books,
        borrowers=borrowers,
        active_transactions=active_transactions,
        username=session.get('username'),
    )


@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        genre = request.form.get('genre', '').strip()
        quantity = utils.parse_int(request.form.get('quantity', ''), default=0)
        if not title or not author or quantity < 1:
            flash('Title, author, and quantity are required.', 'warning')
        else:
            try:
                models.BookManager.add_book(title, author, isbn, genre, quantity)
                flash('Book added successfully.', 'success')
                return redirect(url_for('books'))
            except Exception as exc:
                flash(f'Could not add book: {exc}', 'danger')
    term = request.args.get('q', '').strip()
    results = models.BookManager.search_books(term)
    return render_template('books.html', books=results, query=term)


@app.route('/borrowers', methods=['GET', 'POST'])
@login_required
def borrowers():
    if request.method == 'POST':
        membership_id = request.form.get('membership_id', '').strip()
        name = request.form.get('name', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        if not membership_id or not name:
            flash('Membership ID and name are required.', 'warning')
        else:
            try:
                models.BorrowerManager.add_borrower(membership_id, name, contact, email)
                flash('Borrower added successfully.', 'success')
                return redirect(url_for('borrowers'))
            except Exception as exc:
                flash(f'Could not add borrower: {exc}', 'danger')
    borrowers = models.BorrowerManager.list_borrowers()
    return render_template('borrowers.html', borrowers=borrowers)


@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'borrow':
            membership_id = request.form.get('membership_id', '').strip()
            book_id = utils.parse_int(request.form.get('book_id', ''), default=0)
            borrower = models.BorrowerManager.find_borrower_by_membership(membership_id)
            if not borrower:
                flash('Borrower not found.', 'warning')
            elif book_id < 1:
                flash('Valid book ID is required.', 'warning')
            else:
                try:
                    models.TransactionManager.borrow_book(borrower['id'], book_id)
                    flash('Book borrowed successfully.', 'success')
                    return redirect(url_for('transactions'))
                except Exception as exc:
                    flash(f'Could not borrow book: {exc}', 'danger')
        elif action == 'return':
            transaction_id = utils.parse_int(request.form.get('transaction_id', ''), default=0)
            if transaction_id < 1:
                flash('Valid transaction ID is required.', 'warning')
            else:
                try:
                    models.TransactionManager.return_book(transaction_id)
                    flash('Book returned successfully.', 'success')
                    return redirect(url_for('transactions'))
                except Exception as exc:
                    flash(f'Could not return book: {exc}', 'danger')
    active_transactions = models.TransactionManager.list_active_transactions()
    return render_template('transactions.html', transactions=active_transactions)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
