import os
import sqlite3

class SqliteDB:
    """
    A class to handle SQLite database operations including creating a database, creating tables, 
    and performing CRUD operations with a focus on preventing SQL injection and duplicate entries.

    Methods:
    --------
    - create(db_name): Creates the SQLite database file.
    - table(table_name, columns, foreign_keys=None): Creates a table with specified columns and optional foreign key constraints.
    - insert(database, table_name, data, unique_columns=None): Inserts a row of data into the specified table, preventing duplicates.
    - update(database, table_name, data, condition): Updates rows in the table based on a condition.
    - delete(database, table_name, condition, params=()): Deletes rows from the table based on a condition.
    - select(database, table_name, columns='*', condition=None, params=()): Selects and retrieves data from the table.
    - is_duplicate(database, table_name, data, unique_columns): Checks if a record already exists based on specified unique columns.
    - get_tables: Returns the names of all tables in the database.
    - del_table: Deletes a specified table from the database.

    Example Usage:
    --------------
    # Initialize the SQLite instance
    db = SqliteDB('employees.db')
    """

    def __init__(self, db_name):
        """
        Initializes the database handler and ensures the database file is created.

        Parameters:
        -----------
        db_name : str
            The name of the SQLite database file to create or connect to.
        
        Example:
        --------
        db = SqliteDB('employees.db')
        """
        self.db_name = db_name
        self.create(self.db_name)

    def create(self, db_name):
        """
        Creates a database file if it doesn't already exist.

        Parameters:
        -----------
        db_name : str
            The name of the SQLite database file to create.

        Example:
        --------
        db = SqliteDB('employees.db')
        """
        detect_DB_file = [f for f in os.listdir('.') if f == f'{db_name}']
        if detect_DB_file:
            print(f"Database '{db_name}' already exists. You can now connect and perform operations.")
        else:
            try:
                conn = sqlite3.connect(db_name)
                conn.close()
                print(f"Database '{db_name}' created successfully.")
            except sqlite3.Error as e:
                print(f"Error creating database '{db_name}': {e}")

    @staticmethod
    def is_duplicate(database, table_name, data, unique_columns):
        """
        Checks if a record already exists in the table based on specified unique columns.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.
        
        table_name : str
            The name of the table to check for duplicates.
        
        data : dict
            The data to check for duplicates.
        
        unique_columns : list
            List of column names to check for uniqueness.

        Returns:
        --------
        bool
            True if a duplicate exists, False otherwise.

        Example:
        --------
        data = {'email': 'john@example.com', 'name': 'John'}
        is_dup = SqliteDB.is_duplicate('employees.db', 'employees', data, ['email'])
        """
        if not unique_columns:
            return False

        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        try:
            # Build WHERE clause for unique columns
            conditions = []
            params = []
            for col in unique_columns:
                if col in data:
                    conditions.append(f"{col} = ?")
                    params.append(data[col])

            if not conditions:
                return False

            where_clause = " AND ".join(conditions)
            query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
            
            cursor.execute(query, tuple(params))
            count = cursor.fetchone()[0]
            return count > 0

        except sqlite3.Error as e:
            print(f"Error checking for duplicates in '{table_name}': {e}")
            return False
        finally:
            conn.close()

    def table(database, table_name, columns, foreign_keys=None):
        """
        Creates a table in the connected database with the provided columns and optional foreign key constraints.

        Parameters:
        -----------
        table_name : str
            The name of the table to be created.
        
        columns : list of tuples
            A list of tuples where each tuple defines a column with the following structure:
            - (column_name, data_type, constraints)
            The `constraints` can include properties like 'PRIMARY KEY', 'NOT NULL', etc.
        
        foreign_keys : list of tuples, optional
            A list of foreign key definitions where each tuple is structured as:
            - (column_name, referenced_table, referenced_column)

        Example:
        --------
        db = SqliteDB('employees.db')
        columns = [('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT'),
                   ('email', 'TEXT', 'UNIQUE NOT NULL'),
                   ('name', 'TEXT', 'NOT NULL')]
        db.table('employee.db', 'employees', columns)
        """
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        column_definitions = []
        for column in columns:
            column_definitions.append(f'{column[0]} {column[1]} {column[2]}')

        if foreign_keys:
            for fk in foreign_keys:
                column_definitions.append(
                    f'FOREIGN KEY ({fk[0]}) REFERENCES {fk[1]}({fk[2]})'
                )

        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(column_definitions)}
        )
        '''

        try:
            cursor.execute(create_table_query)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table '{table_name}': {e}")
        finally:
            conn.close()

    @staticmethod
    def insert(database, table_name, data, unique_columns=None):
        """
        Inserts a row of data into a specified table, preventing duplicates based on specified unique columns.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.
        
        table_name : str
            The name of the table where data will be inserted.
        
        data : dict
            A dictionary where keys represent the column names, and values represent the data to insert.
        
        unique_columns : list, optional
            List of column names to check for uniqueness before insertion.
            If None, no duplicate checking is performed.

        Example:
        --------
        data = {'email': 'john@example.com', 'name': 'John Doe'}
        SqliteDB.insert('employees.db', 'employees', data, unique_columns=['email'])
        """
        # Check for duplicates if unique columns are specified
        if unique_columns and SqliteDB.is_duplicate(database, table_name, data, unique_columns):
            print(f"Duplicate record found in '{table_name}'. Insertion skipped.")
            return False

        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

        try:
            cursor.execute(insert_query, tuple(data.values()))
            conn.commit()
            print(f"Data successfully inserted into '{table_name}'.")
            return True
        except sqlite3.Error as e:
            print(f"Error inserting data into '{table_name}': {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update(database, table_name, data, condition):
        """
        Updates rows in a table based on a condition. Uses parameterized queries to prevent SQL injection.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.
        
        table_name : str
            The name of the table where the data will be updated.
        
        data : dict
            A dictionary where keys represent the column names to update, and values represent the new data.
        
        condition : str
            A condition string to specify which rows should be updated (e.g., 'id = 1').

        Example:
        --------
        data = {'salary': 70000}
        condition = 'id = ?'
        SqliteDB.update('employees.db', 'employees', data, condition, (1,))
        """
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        set_clause = ', '.join([f'{key} = ?' for key in data.keys()])
        update_query = f'UPDATE {table_name} SET {set_clause} WHERE {condition}'

        try:
            cursor.execute(update_query, tuple(data.values()))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating table '{table_name}': {e}")
        finally:
            conn.close()

    @staticmethod
    def delete(database, table_name, condition, params=()):
        """
        Deletes rows from a table based on a condition. Uses parameterized queries to prevent SQL injection.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.
        
        table_name : str
            The name of the table from which data will be deleted.
        
        condition : str
            A condition string to specify which rows should be deleted (e.g., 'id = ?').
        
        params : tuple, optional
            Parameters to be used with the condition string to prevent SQL injection.

        Example:
        --------
        SqliteDB.delete('employees.db', 'employees', 'id = ?', (1,))
        """
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        delete_query = f'DELETE FROM {table_name} WHERE {condition}'

        try:
            cursor.execute(delete_query, params)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting data from '{table_name}': {e}")
        finally:
            conn.close()

    @staticmethod
    def select(database, table_name, columns='*', condition=None, params=()):
        """
        Selects and retrieves data from a specified table. Uses parameterized queries to prevent SQL injection.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.
        
        table_name : str
            The name of the table from which data will be selected.
        
        columns : str or list, optional
            The columns to select. Default is all columns ('*').
        
        condition : str, optional
            A condition string to filter the rows (e.g., 'salary > ?').
        
        params : tuple, optional
            Parameters to be used with the condition string.

        Returns:
        --------
        list of tuples
            A list of tuples representing the rows that match the query.

        Example:
        --------
        rows = SqliteDB.select('employees.db', 'employees', ['name', 'email'], 'salary > ?', (50000,))
        """
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        if isinstance(columns, list):
            columns = ', '.join(columns)

        select_query = f'SELECT {columns} FROM {table_name}'
        if condition:
            select_query += f' WHERE {condition}'

        try:
            cursor.execute(select_query, params)
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Error selecting data from '{table_name}': {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_tables(database):
        """
        Returns the names of all tables in the database.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.

        Returns:
        --------
        list of tuples
            A list of tuples containing table names.

        Example:
        --------
        tables = SqliteDB.get_tables('employees.db')
        """
        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            select_query = "SELECT name FROM sqlite_master WHERE type='table';"
            cursor.execute(select_query)
            tables = cursor.fetchall()
            return tables
        except sqlite3.Error as error:
            print("Failed to execute the query:", error)
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def del_table(database, table_name):
        """
        Deletes a table from the database.

        Parameters:
        -----------
        database : str
            The name of the SQLite database file.
        
        table_name : str
            The name of the table to delete.

        Example:
        --------
        SqliteDB.del_table('employees.db', 'old_employees')
        """
        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            select_query = f"DROP TABLE IF EXISTS {table_name};"
            cursor.execute(select_query)
            print(f"Successfully deleted {table_name} table")
        except sqlite3.Error as error:
            print("Failed to execute the query:", error)
        finally:
            if conn:
                conn.close()










import mysql.connector
from mysql.connector import errorcode

class MysqlDB:
    """
    A class to handle MySQL database operations, including creating tables and performing CRUD operations 
    with SQL injection protection and duplicate entry prevention.

    Methods:
    --------
    - create_db: Creates a new MySQL database if it does not exist.
    - table: Creates a table with specified columns and optional foreign key constraints.
    - insert: Inserts a row of data into a specified table, with duplicate prevention based on unique columns.
    - update: Updates rows in the table based on a condition.
    - delete: Deletes rows from the table based on a condition.
    - select: Selects and retrieves data from the table.
    - is_duplicate: Checks if a record already exists based on specified unique columns.
    - get_tables: Returns the names of all tables in the database.
    - del_table: Deletes a specified table from the database.

    Example Usage:
    --------------
    # Initialize the MySQLDB instance
    db = MySQLDB(host='localhost', user='your_user', password='your_password', database='test_db')
    """

    def __init__(self, host, user, password, database):
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.create_db(database)

    def connect(self):
        """Creates a connection to the MySQL database."""
        return mysql.connector.connect(**self.db_config)

    def create(self, database):
        """Creates the MySQL database if it doesn't exist.
        """
        try:
            conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"Database '{database}' created successfully.")
        except mysql.connector.Error as e:
            print(f"Error creating database '{database}': {e}")
        finally:
            conn.close()

    def is_duplicate(self, table_name, data, unique_columns):
        """Checks for duplicates based on unique columns."""
        if not unique_columns:
            return False
        try:
            conn = self.connect()
            cursor = conn.cursor()
            conditions = " AND ".join([f"{col} = %s" for col in unique_columns])
            params = [data[col] for col in unique_columns if col in data]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {conditions}", tuple(params))
            count = cursor.fetchone()[0]
            return count > 0
        except mysql.connector.Error as e:
            print(f"Error checking for duplicates in '{table_name}': {e}")
            return False
        finally:
            conn.close()

    def table(self, table_name, columns, foreign_keys=None):
        """Creates a table with columns and optional foreign key constraints.
            Example Usage:
            --------------
            # Create a new table
            columns = [
                ('id', 'INT', 'PRIMARY KEY AUTO_INCREMENT'),
                ('name', 'VARCHAR(100)', 'NOT NULL'),
                ('email', 'VARCHAR(100)', 'UNIQUE')
            ]
            db.table('users', columns)
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            column_defs = ", ".join([f"{col[0]} {col[1]} {col[2]}" for col in columns])
            if foreign_keys:
                fk_defs = ", ".join([f"FOREIGN KEY ({fk[0]}) REFERENCES {fk[1]}({fk[2]})" for fk in foreign_keys])
                column_defs += f", {fk_defs}"
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})")
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error creating table '{table_name}': {e}")
        finally:
            conn.close()

    def insert(self, table_name, data, unique_columns=None):
        """Inserts data with duplicate checking.
            Example Usage:
            --------------
            # Insert data into the table
            data = {'name': 'John Doe', 'email': 'johndoe@example.com'}
            db.insert('users', data, unique_columns=['email'])
        """
        if unique_columns and self.is_duplicate(table_name, data, unique_columns):
            print(f"Duplicate entry found in '{table_name}'. Insertion skipped.")
            return False
        try:
            conn = self.connect()
            cursor = conn.cursor()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            print(f"Data inserted into '{table_name}' successfully.")
            return True
        except mysql.connector.Error as e:
            print(f"Error inserting data into '{table_name}': {e}")
            return False
        finally:
            conn.close()

    def update(self, table_name, data, condition, params):
        """Updates data based on a condition.
            Example Usage:
            --------------
           # Update data in the table
           db.update('users', {'name': 'Jane Doe'}, 'email = %s', ('johndoe@example.com',))
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            cursor.execute(query, tuple(data.values()) + params)
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error updating table '{table_name}': {e}")
        finally:
            conn.close()

    def delete(self, table_name, condition, params=()):
        """Deletes data based on a condition.
            Example Usage:
            --------------
            # Delete data from the table
            db.delete('users', 'email = %s', ('johndoe@example.com',))
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = f"DELETE FROM {table_name} WHERE {condition}"
            cursor.execute(query, params)
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error deleting data from '{table_name}': {e}")
        finally:
            conn.close()

    def select(self, table_name, columns='*', condition=None, params=()):
        """Selects and retrieves data based on a condition.
            Example Usage:
            --------------
            # Select data from the table
            results = db.select('users')
            print("Selected Rows:", results)
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = f"SELECT {columns} FROM {table_name}"
            if condition:
                query += f" WHERE {condition}"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows
        except mysql.connector.Error as e:
            print(f"Error selecting data from '{table_name}': {e}")
            return []
        finally:
            conn.close()

    def get_tables(self):
        """Returns a list of all tables in the database.
            Example Usage:
            --------------
            # Retrieve all tables in the database
            tables = db.get_tables()
            print("Tables in Database:", tables)
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        except mysql.connector.Error as e:
            print(f"Error fetching table names: {e}")
            return []
        finally:
            conn.close()

    def del_table(self, table_name):
        """Deletes a table from the database.
            Example Usage:
            --------------
            # Delete the table
            db.del_table('users')
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
            print(f"Table '{table_name}' deleted successfully.")
        except mysql.connector.Error as e:
            print(f"Error deleting table '{table_name}': {e}")
        finally:
            conn.close()
