## Easy SQL: Python Database Helper

**Easy SQL** is a Python package that simplifies database interactions with SQLite and MySQL databases. It provides a user-friendly interface for:

- **Database Management:** Create, connect to, and manage tables within both SQLite and MySQL databases.
- **CRUD Operations:** Perform Create, Read, Update, and Delete operations on database tables.
- **Security and Data Integrity:**
    - Prevent SQL injection attacks through parameterized queries.
    - Avoid duplicate entries by checking for them and using unique column constraints.

**## Usage**

### 1. Import the Package

```python
import easy_sql as es  # Convenient alias for easy_sql
```

### 2. Connect to the Database**

**SQLite:**

```python
# Create an instance of SqliteDB with the database filename
sqlite_db = es.SqliteDB('employees.db')
```

**MySQL:**

```python
# Provide connection details for MysqlDB
mysql_db = es.MysqlDB(host='localhost', user='your_username', password='your_password', database='your_database_name')
```

**## 3. SQLite-Specific Features**

**- Creating a Database**

The `SqliteDB` constructor automatically creates the database file if it doesn't exist.

**- Creating Tables**

```python
# Define columns (column_name, data_type, constraints)
columns = [
    ('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT'),
    ('name', 'TEXT', 'NOT NULL'),
    ('email', 'TEXT', 'UNIQUE NOT NULL'),
]

# Create the table using SqliteDB
sqlite_db.create_table('employees', columns)
```

**## 4. Shared Features (SQLite & MySQL)**

**- Checking for Duplicates**

```python
# Check for existing records based on specified unique columns
data = {'email': 'john@example.com', 'name': 'John Doe'}
is_duplicate = sqlite_db.is_duplicate('employees', data, ['email'])  # Or mysql_db.is_duplicate(...)
```

**- Inserting Data**

```python
# Insert a row with duplicate prevention (optional)
data = {'name': 'Jane Doe', 'email': 'jane@example.com'}
sqlite_db.insert('employees', data, unique_columns=['email'])  # Or mysql_db.insert(...)
```

**- Updating Data**

```python
# Update data based on a condition (using parameterized queries)
data = {'salary': 80000}
condition = 'id = ?'
params = (1,)  # Example parameter for the condition

sqlite_db.update('employees', data, condition, params)  # Or mysql_db.update(...)
```

**- Deleting Data**

```python
# Delete rows based on a condition (using parameterized queries)
condition = 'email = ?'
params = ('old_email@example.com',)

sqlite_db.delete('employees', condition, params)  # Or mysql_db.delete(...)
```

**- Selecting Data**

```python
# Retrieve all rows (or specific columns) with an optional condition
rows = sqlite_db.select('employees')  # Or mysql_db.select(...)
# Optionally, select specific columns and filter with a condition
specific_columns = ['name', 'email']
condition = 'salary > ?'
params = (50000,)
filtered_rows = sqlite_db.select('employees', specific_columns, condition, params)  # Or mysql_db.select(...)
```

**- Getting All Tables**

```python
# List all tables in the database
tables = sqlite_db.get_tables()  # Or mysql_db.get_tables(...)
```

**- Deleting a Table**

```python

sqlite_db.delete_table('old_table_name')  # Or mysql_db.delete_table(...)

```

