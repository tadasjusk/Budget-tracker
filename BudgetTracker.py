import sqlite3



def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None

def select_all_transactions(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions")

    rows = cur.fetchall()
    for row in rows:
        print(row)


def select_transactions(conn, date_from, date_to, *args):
    """
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
    """
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

    return f"Spent: {expenses:.2f}£\nReceived: {income:.2f}£\nTotal balance: {total:.2f}£"

def delete_transactions(conn, ids):
    cur = conn.cursor()
    for id in ids:
        cur.execute("DELETE from transactions WHERE id=? ", (id,))
    conn.commit()


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)
def create_transaction(conn, transaction):
    """
    Create a new entry into the transactions table
    :param conn:
    :param transaction:

    """
    sql = ''' INSERT INTO transactions(date,value,currency,desc,type)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, transaction)

def main():
    database = "mydatabase.db"
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
        create_table(conn, sql_create_transactions_table)

    else:
        print("Error! cannot create the database connection.")
    with conn:

        select_all_transactions(conn)

if __name__ == '__main__':
    main()
