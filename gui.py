import tkinter as Tk
from tkinter import ttk

from tkcalendar import DateEntry
import BudgetTracker


class EntryFrame(Tk.Toplevel):
    """"""

    def __init__(self, original):
        """Constructor"""
        self.database = "transaction_database.db"
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.title("Enter a transaction")
        self.geometry(f"+{original.root.winfo_x()}+{original.root.winfo_y()}")

        label_date = ttk.Label(self, text="Date")
        label_date.grid(row=0, column=0)
        self.entry_date = DateEntry(self, date_pattern='yyyy/mm/dd')
        self.entry_date.grid(row=1, column=0)

        validation = self.register(lambda char : char.isdigit() or char in ".-")


        label_value = ttk.Label(self, text="Value")
        label_value.grid(row=0, column=1)
        self.entry_value = ttk.Entry(self, validate="key", validatecommand=(validation, '%S')
)
        self.entry_value.grid(row=1, column=1)

        label_currency = ttk.Label(self, text="Currency")
        label_currency.grid(row=0, column=2)
        self.var_currency = Tk.StringVar(self)

        currencies = {'£', '$', '€'}
        cur_popmenu = ttk.OptionMenu(self, self.var_currency, '£',  *currencies)
        cur_popmenu.grid(row=1, column=2)

        label_description = ttk.Label(self, text="Description")
        label_description.grid(row=0, column=3)
        self.entry_description = ttk.Entry(self)
        self.entry_description.grid(row=1, column=3)


        label_type = ttk.Label(self, text="Category")
        label_type.grid(row=0, column=4)
        self.var_type = Tk.StringVar(self)

        types = {'Groceries', 'New items', 'Entertainment', 'Eating out',
                 'Drinks', 'Subscriptions', 'Rent', 'Leisure', 'Transport',
                 'Debt', 'Salary', 'Cash withdrawal'}
        types_popmenu = ttk.OptionMenu(self, self.var_type, 'Groceries', *types)
        types_popmenu.grid(row=1, column=4)

        enterbtn = ttk.Button(self, text="Enter", command=self.on_enter)
        enterbtn.grid(row=1, column=5)

        cancelbtn = ttk.Button(self, text="Cancel", command=self.on_cancel)
        cancelbtn.grid(row=1, column=6)

        self.status = ttk.Label(self)
        self.status.grid(row=2, columnspan=7, sticky="w")

        self.focus_force()

    def on_enter(self):
        """"""
        try:
            temp = (str(self.entry_date.get_date()),
                    float(self.entry_value.get()),
                    self.var_currency.get(),
                    self.entry_description.get(),
                    self.var_type.get())
        except:
            self.status.config(text="Whooops, looks like you entered a wrong value. Try again!\n")
        else:
            conn = BudgetTracker.create_connection(self.database)

            if conn is None:
                self.status.config(text="Error! cannot create the database connection.")
            with conn:
                BudgetTracker.create_transaction(conn, temp)

            self.destroy()
            self.original_frame.show_window()
    def on_cancel(self):
        self.destroy()
        self.original_frame.show_window()

class HistoryFrame(Tk.Toplevel):

    def __init__(self, original):
        self.database = "transaction_database.db"
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.title("Browse history")
        self.geometry(f"+{original.root.winfo_x()}+{original.root.winfo_y()}")
        self.maxsize(width=0, height=original.root.winfo_screenheight())
        menu_frame = ttk.Frame(self)
        menu_frame.grid(row=0, column=0, columnspan=2)
        label_from = ttk.Label(menu_frame, text="From: ")
        label_from.grid(row=1, column=0)

        self.date_from = DateEntry(menu_frame, date_pattern='yyyy-mm-dd')
        self.date_from.grid(row=1, column=1)

        label_to = ttk.Label(menu_frame, text="To: ")
        label_to.grid(row=2, column=0)

        self.date_to = DateEntry(menu_frame, date_pattern='yyyy-mm-dd')
        self.date_to.grid(row=2, column=1)

        enterbtn = ttk.Button(menu_frame, text="Show transactions", command=self.on_show_entries)
        enterbtn.grid(row=3, column=0, sticky="nesw")

        closebtn = ttk.Button(menu_frame, text="Return", command=self.on_return)
        closebtn.grid(row=3, column=1, sticky="nesw")

        self.table_canvas = None
        self.scroll_bar = None
        
        self.focus_force()



    def on_show_entries(self):
        conn = BudgetTracker.create_connection(self.database)
        if conn is None:
            print("Error! cannot create the database connection.")
        with conn:
            table_data = BudgetTracker.select_transactions(
                conn, self.date_from.get(), self.date_to.get())
            balance = BudgetTracker.get_balance(
                conn, self.date_from.get(), self.date_to.get())
        if self.table_canvas:
            self.table_canvas.destroy()
        if self.scroll_bar:
            self.scroll_bar.destroy()

        self.table_canvas = Tk.Canvas(self)
        table_frame = ttk.Frame(self.table_canvas)
        self.scroll_bar = ttk.Scrollbar(self, orient="vertical", command=self.table_canvas.yview)
        self.table_canvas.configure(yscrollcommand=self.scroll_bar.set)

        self.table_canvas.grid(row=1, column=0, sticky="ns")
        self.scroll_bar.grid(row=1, column=1, sticky="ns")
        self.table_canvas.create_window((0,0), window=table_frame, anchor="nw", 
                                  tags="table_frame")
        table_frame.bind("<Configure>", lambda event : self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all")))
        

        if table_data:

            ttk.Style().configure("Bold.TLabel", font=("Arial", "10", "bold"))
            
            ttk.Label(table_frame, text="Date", style="Bold.TLabel",
                      padding=(6,0)).grid(row=4, column=0, sticky="w")
            ttk.Label(table_frame, text="Value", style="Bold.TLabel",
                      padding=(6,0)).grid(row=4, column=1, sticky="w")
            ttk.Label(table_frame, text="Description", style="Bold.TLabel",
                      padding=(6,0)).grid(row=4, column=2, sticky="w")
            ttk.Label(table_frame, text="Category", style="Bold.TLabel",
                      padding=(6,0)).grid(row=4, column=3, sticky="w")

            for i, row in enumerate(table_data):
                ttk.Label(table_frame, text=f"{row[1]}", relief="groove",
                          padding=(6,0)).grid(row=5+i, column=0, sticky="nesw")
                ttk.Label(table_frame, text=f"{row[2]}{row[3]}", relief="groove",
                          padding=(6,0)).grid(row=5+i, column=1, sticky="nesw")
                ttk.Label(table_frame, text=f"{row[4]}", relief="groove",
                          padding=(6,0)).grid(row=5+i, column=2, sticky="nesw")
                ttk.Label(table_frame, text=f"{row[5]}", relief="groove",
                          padding=(6,0)).grid(row=5+i, column=3, sticky="nesw")
            ttk.Label(table_frame, text=balance).grid(columnspan=4, sticky="w")
        else:
            ttk.Label(table_frame, text="No data to show").pack(anchor="w")

        self.grid_rowconfigure(1, weight=1)
        table_frame.update_idletasks()
        canvas_height = 0
        if table_frame.winfo_height() < self.original_frame.root.winfo_screenheight()*0.75:
            canvas_height=table_frame.winfo_height()
        else:
            canvas_height=self.original_frame.root.winfo_screenheight()*0.75
        self.table_canvas.config(width=table_frame.winfo_width(), height=canvas_height)
        #table_frame.update_idletasks()
        #pass
    def on_return(self):
        self.destroy()
        self.original_frame.show_window()




class MyApp:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        self.database = "transaction_database.db"
        self.root = parent
        self.root.title("Budget tracker")


        btn = ttk.Button(self.root, text="Add new transaction",
                        command=self.open_entry_frame)
        btn.grid(row=0, column=0)

        show_btn = ttk.Button(self.root, text="Browse History",
                             command=self.show_transactions)
        show_btn.grid(row=0, column=1)

        root.update_idletasks() 
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_width()
        window_height = root.winfo_height()
            
        x = int((screen_width / 2) - (window_width / 2))  
        y = int((screen_height / 10) - (window_height / 10))
        
        self.root.geometry(f"+{x}+{y}")

    def show_transactions(self):
        self.root.withdraw()
        HistoryFrame(self)

    def open_entry_frame(self):
        """"""
        self.root.withdraw()
        EntryFrame(self)

    def show_window(self):
        """"""
        self.root.deiconify()


if __name__ == "__main__":
    root = Tk.Tk()
    app = MyApp(root)
    root.mainloop()
