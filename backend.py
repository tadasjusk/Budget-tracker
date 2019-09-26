"""
This module is a Python interface to perform SQLite commands to interact
with SQLite database. It contains methods specific for 'transactions'
table, that is:
create_connection(db_file),
create_table(conn, create_table_sql),
create_transaction(conn, transaction),
select_transactions(conn, date_from, date_to, *args),
get_balance(conn, date_from, date_to, *args),
delete_transactions(conn, ids)
"""

import sqlite3
import sys

def create_connection(db_file):
    """Creates a connection to the SQLite database specified by db_file.

    Parameters:
        param db_file (string): Path to database file
    Returns:
         Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e, file=sys.stderr)
    return None

def select_transactions(conn, date_from, date_to, *args):
    """Selects all columns from 'transaction' with conditions given.

    Parameters:
        conn (Connection): Connection object
        date_from (string): Earliest date to select entries from
        data_to (string): Latest date to select entries from
        *args: Variable length argument list
            Possible argument combinations:
            (string): Category
            (string): Category, (string): Search
            (float): Min_value, (float): Max_value, (string): Category
            (float): Min_value, (float): Max_value, (string): Category, (string): Search

    Returns:
        list of tuples: Entries from 'transaction' table
    """
    cur = conn.cursor()
    if len(args) == 0:
        cur.execute('''SELECT * FROM transactions
                        WHERE date BETWEEN ? AND ?
                        ORDER BY date  ''', (date_from, date_to))
    if len(args) == 1:
        cur.execute('''SELECT * FROM transactions
                        WHERE date BETWEEN ? AND ?
                        AND (type = ? OR ? = 'All')
                        ORDER BY date  ''',
                    (date_from, date_to, args[0], args[0]))
    if len(args) == 2:
        cur.execute('''SELECT * FROM transactions
                        WHERE date BETWEEN ? AND ?
                        AND (type = ? OR ? = 'All')
                        AND desc LIKE ?
                        ORDER BY date  ''',
                    (date_from, date_to, args[0], args[0], '%'+args[1]+'%'))

    if len(args) == 3:
        cur.execute('''SELECT * FROM transactions
                        WHERE date BETWEEN ? AND ?
                        AND value BETWEEN ? AND ?
                        AND (type = ? OR ? = 'All')
                        ORDER BY date  ''',
                    (date_from, date_to, args[0], args[1], args[2], args[2]))
    if len(args) == 4:
        cur.execute('''SELECT * FROM transactions
                        WHERE date BETWEEN ? AND ?
                        AND value BETWEEN ? AND ?
                        AND (type = ? OR ? = 'All')
                        AND desc LIKE ?
                        ORDER BY date  ''',
                    (date_from, date_to, args[0], args[1], args[2], args[2],
                     '%'+args[3]+'%'))

    return cur.fetchall()

def get_balance(conn, date_from, date_to, *args):
    """Returns dictionary containing amount spent, received and total balance.

    Parameters:
        conn (Connection): Connection object
        date_from (string): Earliest date to select entries from
        data_to (string): Latest date to select entries from
        *args: Variable length argument list
            Possible argument combinations:
            (string): Category
            (string): Category, (string): Search
            (float): Min_value, (float): Max_value, (string): Category
            (float): Min_value, (float): Max_value, (string): Category, (string): Search
    Returns:
        dict: 'Expenses', 'Received' and 'Total' amounts in GBP(£)
    """
    rows = select_transactions(conn, date_from, date_to, *args)
    total = 0
    expenses = 0
    income = 0
    multiplier = 1
    for row in rows:
        if row[3] == "£":
            multiplier = 1
        elif row[3] == "€":
            multiplier = 0.9
        elif row[3] == "$":
            multiplier = 0.8
        total += float(row[2])*multiplier
        if float(row[2]) > 0:
            income += row[2]*multiplier
        else:
            expenses += row[2]*multiplier
    return {"Expenses":expenses, "Received":income, "Total":total}

def get_balance_by_category(conn, date_from, date_to, *args):
    """Returns total balance for each category found

    Parameters:
    conn (Connection): Connection object
    date_from (string): Earliest date to select entries from
    data_to (string): Latest date to select entries from
    *args: Variable length argument list
        Possible argument combinations:
        (string): Category
        (string): Category, (string): Search
        (float): Min_value, (float): Max_value, (string): Category
        (float): Min_value, (float): Max_value, (string): Category, (string): Search
    Returns:
        dict: Balance for each category found
    """
    rows = select_transactions(conn, date_from, date_to, *args)
    balance_by_category = {}
    for row in rows:
        if row[3] == "£":
            multiplier = 1
        elif row[3] == "€":
            multiplier = 0.9
        elif row[3] == "$":
            multiplier = 0.8
        try:
            balance_by_category[f"{row[5]}"] += float(row[2])*multiplier
        except KeyError:
            balance_by_category[f"{row[5]}"] = float(row[2])*multiplier
    return balance_by_category


def delete_transactions(conn, ids):
    """Delete entries from 'transactions' table given their id's.

    Parameters:
        ids (list): List of id's of entries to be deleted
    """
    cur = conn.cursor()
    for item in ids:
        cur.execute("DELETE from transactions WHERE id=? ", (item,))
    conn.commit()

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement.
    Parameters:
        conn (Connection): Connection object
        create_table_sql (String): a CREATE TABLE statement

    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e, file=sys.stderr)

def create_transaction(conn, transaction):
    """Create a new entry into the 'transactions' table.

    Parameters:
        conn (Connection): Connection object
        transaction (Tuple): Tuple containing data to be inserted to table
    """
    sql = ''' INSERT INTO transactions(date, value, currency, desc, type)
              VALUES(?, ?, ?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, transaction)

def main():
    database = "transaction_database.db"
    sql_create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
                                        id integer PRIMARY KEY,
                                        date text,
                                        value float,
                                        currency text,
                                        desc text,
                                        type text
                                    ); """

    # create a database connection
    conn = create_connection(database)

    if conn is not None:
        # create transactions table
        with conn:
            create_table(conn, sql_create_transactions_table)

if __name__ == '__main__':
    main()
