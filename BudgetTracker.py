import tkinter as Tk
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
        
def select_transactions(conn,year,month):
    """
    """
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM transactions where
                    date BETWEEN '{year}-{month}-01' AND '{year}-{month}-31'  ''')

 
    rows = cur.fetchall()
    for row in rows:
        print(row)

def show_balance(conn,year,month):
    """
    """
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM transactions where
                    date BETWEEN '{year}-{month}-01' AND '{year}-{month}-31'  ''')

    rows = cur.fetchall()
    total=0
    expenses=0
    income=0
    for row in rows:
        total+=float(row[2])
        if float(row[2])>0:
            income+=row[2]
        else:
            expenses+=row[2]
    print(f"Spent: {expenses:.2f}£\nIncome: {income:.2f}£\nMonthly balance: {total:.2f}£\n")
        
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
def create_transaction(conn,transaction):
    """
    Create a new project into the projects table
    :param conn:
    :param transaction:
    :return: project id
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
       
        create_transaction(conn,transaction)

        select_all_transactions(conn)

if __name__ == '__main__':
    main()