# Library Management System

A Python command-line Library Management System with MySQL database connectivity.

## Features
- Book management: add, update, delete books
- Borrower management: add, update, delete borrowers
- Borrow and return books with due date tracking
- Search books by title, author, or genre
- Fine calculation for late returns
- User authentication for admin access
- Reporting for available books, borrower activity, and fines

## Setup
1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a MySQL database and run `db_schema.sql`.
4. Update `db.py` with your MySQL credentials, or use environment variables: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
   - Default DB config in `db.py` uses `root` / `p455word` and database `library_management`.
5. Run the app:
   ```bash
   python app.py
   ```

6. Run the web UI:
   ```bash
   python web_app.py
   ```

## Default app login
- username: `admin`
- password: `admin123`

## Database
- `books` stores book details
- `borrowers` stores borrower profiles
- `transactions` stores borrow/return events
- `users` stores system users and hashed passwords
- `fines` stores fine amounts for late returns
