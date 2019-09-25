"""
This module handles the interface of Budget Tracker program. Interface is
implemented using 'tkinter' library. Part of the program that contains SQLite
commands is in 'backend' module. The idea of the program is to be able 
to visually interact with a database containing records of monetary transactions.
Program allows to browse, filter, delete, enter records to the database.

Module contains 2 classes - BudgetTracker and EntryFrame(tk.Toplevel),
and 1 exception - EmptyDescriptionError(Exception). 

"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
from tkcalendar import DateEntry
import backend

class EntryFrame(tk.Toplevel):
    """Class that handles the frame to enter data.

    Attributes:
        database (string): path to the SQLite database file
        main_window (BudgetTracker): instance of BudgetTracker class.
            used to manage the main window of the application
        status_message (tkinter.StringVar): holds information text to 
            be outputted
        entry_date (tkinter.DateEntry): DateEntry object to select date
        entry_value (tkinter.ttk.Entry): Entry object to enter value
        var_currency (tkinter.StringVar): holds selected currency symbol
        entry_description (tkinter.ttk.Entry): Entry object to enter description
        var_category (tkinter.StringVar): holds selected category
    """
    
    def __init__(self, main_window):
        """
        Parameters:
            main_window (BudgetTracker): instance of BudgetTracker class.
                used to manage the main window of the application
        """
        self.database = "transaction_database.db"
        self.main_window = main_window
        tk.Toplevel.__init__(self)
        self.title("Enter a transaction")

        self.status_message = tk.StringVar()
        

        validation = self.register(lambda char: is_numeric(char) or char in ".-")

        ttk.Label(self, text="Date").grid(row=0, column=0)

        self.entry_date = DateEntry(self, date_pattern='yyyy/mm/dd')
        self.entry_date.grid(row=1, column=0)
        
        ttk.Label(self, text="Value").grid(row=0, column=1)

        self.entry_value = ttk.Entry(self, validate="key", validatecommand=(validation, '%S'))

        self.entry_value.grid(row=1, column=1)

        ttk.Label(self, text="Currency").grid(row=0, column=2)
        
        self.var_currency = tk.StringVar()

        currencies = {'£', '$', '€'}
        ttk.OptionMenu(self, self.var_currency, '£', *currencies).grid(row=1, column=2)

        ttk.Label(self, text="Description").grid(row=0, column=3)

        self.entry_description = ttk.Entry(self)
        self.entry_description.grid(row=1, column=3)

        ttk.Label(self, text="Category").grid(row=0, column=4)
        
        self.var_category = tk.StringVar()

        categories = {'Groceries', 'New items', 'Entertainment', 'Eating out',
                      'Drinks', 'Subscriptions', 'Rent', 'Leisure', 'Transport',
                      'Debt', 'Salary', 'Cash withdrawal'}
        ttk.OptionMenu(self, self.var_category, 'Groceries', *categories).grid(row=1, column=4)

        ttk.Button(self, text="Enter", command=self.on_enter).grid(row=1, column=5)

        ttk.Button(self, text="Close", command=self.on_close).grid(row=1, column=6)
        
        ttk.Label(self, textvariable=self.status_message).grid(row=2, columnspan=7, sticky="w")

        self.focus_force()
        self.main_window.is_entry_window_open = True

        self.update_idletasks()
        x_position = int(self.main_window.root.winfo_x()
                         + self.main_window.root.winfo_width()/2
                         - self.winfo_width()/2)
        y_position = int(self.main_window.root.winfo_y()
                         + self.main_window.root.winfo_height()/2
                         - self.winfo_height()/2)
        self.geometry(f"+{x_position}+{y_position}")


    def on_enter(self):
        """Checks if entered data valid. If it is, enters to database"""

        now = datetime.datetime.now().strftime("[%H:%M:%S]")

        try:
            entry = (self.entry_date.get_date(),
                     float(self.entry_value.get()),
                     self.var_currency.get(),
                     self.entry_description.get(),
                     self.var_category.get())

            if not self.entry_description.get():
                raise EmptyDescriptionError()
     
        except ValueError:
            if len(self.status_message.get().split("\n")) > 10: #number of lines more than 10 
                self.status_message.set(
                    "{}".format('\n'.join((self.status_message.get().split("\n"))[1:]))
                    + f"{now} " + "Whooops, looks like you entered a wrong value. Try again!\n")
            else:
                self.status_message.set(self.status_message.get()
                    + f"{now} " + "Whooops, looks like you entered a wrong value. Try again!\n")
        except EmptyDescriptionError:
            if len(self.status_message.get().split("\n")) > 10: #number of lines more than 10 
                self.status_message.set(
                    "{}".format('\n'.join((self.status_message.get().split("\n"))[1:]))
                    + f"{now} " + "Failed to insert data. Please enter description\n")
            else:
                self.status_message.set(self.status_message.get()
                    + f"{now} " + "Failed to insert data. Please enter description\n")

        else:
            conn = backend.create_connection(self.database)

            if conn is None:
                self.status_message.set("Error! cannot create the database connection.")
            with conn:
                backend.create_transaction(conn, entry)

            if len(self.status_message.get().split("\n")) > 10: #number of lines more than 10 
                self.status_message.set(
                    "{}".format('\n'.join((self.status_message.get().split("\n"))[1:]))
                    + f"{now} " + "Succesfully inserted into database\n")
            else:
                self.status_message.set(self.status_message.get()
                    + f"{now} " + "Succesfully inserted into database\n")
            self.entry_value.delete(0, "end")
            self.entry_description.delete(0, "end")

    def on_close(self):
        """Closes the entry window"""
        self.main_window.is_entry_window_open = False
        self.destroy()


class EmptyDescriptionError(Exception):
    """Exception thrown to stop entries without desciptions to be inserted"""
    pass


class BudgetTracker:
    """Class that handles the main window of application.
    
    Attributes:
        database (string): path to the SQLite database file
        root (tkinter.tk): widget representing the main window of application
        is_entry_window_open (bool): specifies whether the entry window is open
        date_from (tkinter.DateEntry): DateEntry object to select earliest date
        date_to (tkinter.DateEntry): DateEntry object to select latest date
        delete_btn (tkinter.ttk.Button): Button to delete selected entries
        status_msg (tkinter.ttk.Label): Information message about status of program
        apply_filters_state (tkinter.IntVar): Holds state if filters are to be applied
        var_category (tkinter.StringVar): Holds category to be shown
        show_only_menu (tkinter.ttk.OptionMenu): Option menu to select category
        in_value_range_state (tkinter.IntVar): holds state whether to filter entries
            by value
        in_value_range_cbutton (tkinter.ttk.Checkbutton): button to select whether
            to filter entries by value
        minimum_value_entry (tkinter.ttk.Entry): Entry to enter minimum value to be
            returned
        maximum_value_entry (tkinter.ttk.Entry): Entry to enter maximum value to be
            returned
        search_description_state (tkinter.IntVar): holds state whether to search in
            description
        search_description_cbutton (tkinter.ttk.Checkbutton): button to select whether
            to search in description
        search_description_entry (tkinter.ttk.Entry): Entry to enter what to search for
            in description
        table_canvas (tkinter.Canvas): widget that contains all the data returned from 
            database
        scroll_bar (tkinter.ttk.Scrollbar): scrollbar widget
        data_entry_cbuttons (list): list containing checkbuttons next to data entries
        data_entry_ids (list): list containing ids of returned data entries
    """
    def __init__(self, parent):
        """Constructor"""
        self.database = "transaction_database.db"
        self.root = parent
        self.root.title("Budget tracker")

        self.root.update_idletasks() 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
            
        x = int((screen_width / 2) - (window_width / 2))  
        y = int((screen_height / 10) - (window_height / 10))
        
        self.root.geometry(f"+{x}+{y}")

        self.is_entry_window_open = False

        menu_frame = ttk.Frame(self.root)
        menu_frame.grid(row=0, column=0, columnspan=2)

        ttk.Label(menu_frame, text="Date").grid(row=0, column=1)

        ttk.Label(menu_frame, text="From: ").grid(row=1, column=0)

        self.date_from = DateEntry(menu_frame, date_pattern='yyyy-mm-dd')
        self.date_from.grid(row=1, column=1)

        ttk.Label(menu_frame, text="To: ").grid(row=2, column=0)

        self.date_to = DateEntry(menu_frame, date_pattern='yyyy-mm-dd')
        self.date_to.grid(row=2, column=1)

        ttk.Button(menu_frame, text="Show transactions",
                   command=self.on_show_entries).grid(row=3, column=0, columnspan=2,
                                                      sticky="nesw")

        add_btn = ttk.Button(
            menu_frame,
            text="Add new transactions",
            command=lambda: EntryFrame(self) if not self.is_entry_window_open else None)
        add_btn.grid(row=4, column=0)

        self.delete_btn = ttk.Button(menu_frame,
                                     text="Delete selected",
                                     command=self.on_delete)
        self.delete_btn.grid(row=4, column=1, sticky="nesw")
        self.delete_btn.state(["disabled"])


        self.status_msg = ttk.Label(menu_frame, foreground="red")
        self.status_msg.grid(row=5, column=0, columnspan=2, sticky="w")

        self.apply_filters_state = tk.IntVar()
        apply_filter_cbtn = ttk.Checkbutton(menu_frame,
                                            variable=self.apply_filters_state,
                                            text="Apply filters",
                                            command=self.on_change_apply_filters_state)
        apply_filter_cbtn.grid(row=0, column=2, columnspan=2)

        ttk.Label(menu_frame,
                  text="Show only from category:").grid(row=1, column=2, columnspan=3)

        categories = {'Groceries', 'New items', 'Entertainment', 'Eating out',
                      'Drinks', 'Subscriptions', 'Rent', 'Leisure', 'Transport',
                      'Debt', 'Salary', 'Cash withdrawal', 'All'}
        self.var_category = tk.StringVar()
        self.show_only_menu = ttk.OptionMenu(menu_frame, self.var_category, "All", *categories)
        self.show_only_menu.grid(row=1, column=5)
        self.show_only_menu.configure(state="disabled")

        self.in_value_range_state = tk.IntVar()
        self.in_value_range_cbutton = ttk.Checkbutton(menu_frame,
                                           variable=self.in_value_range_state,
                                           text="In value range: ",
                                           command=self.on_change_in_value_range_state)
        self.in_value_range_cbutton.grid(row=2, column=2, columnspan=4)
        self.in_value_range_cbutton.configure(state="disabled")

        ttk.Label(menu_frame, text="Min(£):").grid(row=3, column=2)

        validation = self.root.register(lambda char: is_numeric(char) or char in ".-")

        self.minimum_value_entry = ttk.Entry(menu_frame,
                                             width=6,
                                             justify="center",
                                             validate="key",
                                             validatecommand=(validation, '%S'))
        self.minimum_value_entry.grid(row=3, column=3)
        self.minimum_value_entry.insert(0, "0.0")
        self.minimum_value_entry.configure(state="disabled")


        ttk.Label(menu_frame, text="Max(£):").grid(row=3, column=4)

        self.maximum_value_entry = ttk.Entry(menu_frame,
                                             width=6,
                                             justify="center",
                                             validate="key",
                                             validatecommand=(validation, '%S'))
        self.maximum_value_entry.grid(row=3, column=5)
        self.maximum_value_entry.insert(0, "0.0")
        self.maximum_value_entry.configure(state="disabled")

        self.search_description_state = tk.IntVar()
        self.search_description_cbutton = ttk.Checkbutton(menu_frame,
                                           variable=self.search_description_state,
                                           text="Search in description: ",
                                           command=self.on_change_search_description_state)
        self.search_description_cbutton.grid(row=4, column=2, columnspan=4)
        self.search_description_cbutton.configure(state="disabled")

        self.search_description_entry = ttk.Entry(menu_frame)
        self.search_description_entry.grid(row=5, column=2, columnspan=4)
        self.search_description_entry.configure(state="disabled")

        self.table_canvas = None
        self.scroll_bar = None
        self.data_entry_cbuttons = []
        self.data_entry_ids = []
        

    def on_delete(self):
        selected_rows = []
        for cbutton in self.data_entry_cbuttons:
            if cbutton.instate(["selected"]):
                selected_rows.append(cbutton.grid_info()["row"]-1)
        if selected_rows:
            if messagebox.askokcancel("Delete",
                                      "Are you sure you want to delete "
                                      f"{len(selected_rows)} selected entries?"):
                ids_to_delete = []
                for selected_row in selected_rows:
                    ids_to_delete.append(self.data_entry_ids[selected_row])
                conn = backend.create_connection(self.database)
                with conn:
                    backend.delete_transactions(conn, ids_to_delete)

                self.on_show_entries()
        
    def on_change_apply_filters_state(self):
        if self.apply_filters_state.get():
            self.show_only_menu.configure(state="enabled")
            self.in_value_range_cbutton.configure(state="enabled")
            self.search_description_cbutton.configure(state="enabled")
            if self.in_value_range_state.get():
                self.minimum_value_entry.configure(state="enabled")
                self.maximum_value_entry.configure(state="enabled")
            if self.search_description_state.get():
                self.search_description_entry.configure(state="enabled")

        else:
            self.show_only_menu.configure(state="disabled")
            self.in_value_range_cbutton.configure(state="disabled")
            self.minimum_value_entry.configure(state="disabled")
            self.maximum_value_entry.configure(state="disabled")
            self.search_description_cbutton.configure(state="disabled")
            self.search_description_entry.configure(state="disabled")
    def on_change_in_value_range_state(self):
        if self.in_value_range_state.get():
            self.minimum_value_entry.configure(state="enabled")
            self.maximum_value_entry.configure(state="enabled") 
        else:
            self.minimum_value_entry.configure(state="disabled")
            self.maximum_value_entry.configure(state="disabled")

    def on_change_search_description_state(self):
        if self.search_description_state.get():
            self.search_description_entry.configure(state="enabled")
        else:
            self.search_description_entry.configure(state="disabled")

    def on_show_entries(self):
        conn = backend.create_connection(self.database)
        if conn is None:
            print("Error! cannot create the database connection.")
        with conn:
            try:
                if self.apply_filters_state.get():
                    if self.in_value_range_state.get():
                        if self.search_description_state.get():
                            table_data = backend.select_transactions(
                                conn, self.date_from.get(), self.date_to.get(),
                                float(self.minimum_value_entry.get()),
                                float(self.maximum_value_entry.get()),
                                self.var_category.get(),
                                self.search_description_entry.get())
                            balance = backend.get_balance(
                                conn, self.date_from.get(), self.date_to.get(),
                                float(self.minimum_value_entry.get()),
                                float(self.maximum_value_entry.get()),
                                self.var_category.get(),
                                self.search_description_entry.get())
                        else:
                            table_data = backend.select_transactions(
                                conn, self.date_from.get(), self.date_to.get(),
                                float(self.minimum_value_entry.get()),
                                float(self.maximum_value_entry.get()),
                                self.var_category.get())
                            balance = backend.get_balance(
                                conn, self.date_from.get(), self.date_to.get(),
                                float(self.minimum_value_entry.get()),
                                float(self.maximum_value_entry.get()),
                                self.var_category.get())
                    else:
                        if self.search_description_state.get():
                            table_data = backend.select_transactions(
                                conn, self.date_from.get(), self.date_to.get(),
                                self.var_category.get(),
                                self.search_description_entry.get())
                            balance = backend.get_balance(
                                conn, self.date_from.get(), self.date_to.get(),
                                self.var_category.get(),
                                self.search_description_entry.get())
                        else:
                            table_data = backend.select_transactions(
                                conn, self.date_from.get(), self.date_to.get(),
                                self.var_category.get())
                            balance = backend.get_balance(
                                conn, self.date_from.get(), self.date_to.get(),
                                self.var_category.get())
                else:
                    table_data = backend.select_transactions(
                        conn, self.date_from.get(), self.date_to.get())
                    balance = backend.get_balance(
                        conn, self.date_from.get(), self.date_to.get())
            except ValueError:
                self.status_msg.configure(text="Error. Invalid min or max value")
                return
            else:
                self.status_msg.configure(text="")
        
        if self.table_canvas:
            self.table_canvas.destroy()
        if self.scroll_bar:
            self.scroll_bar.destroy()

        self.table_canvas = tk.Canvas(self.root, highlightthickness=0)
        table_frame = ttk.Frame(self.table_canvas)
        self.scroll_bar = ttk.Scrollbar(self.root,
                                        orient="vertical",
                                        command=self.table_canvas.yview)
        self.table_canvas.configure(yscrollcommand=self.scroll_bar.set)

        self.table_canvas.grid(row=1, column=0, sticky="ns")
        self.scroll_bar.grid(row=1, column=1, sticky="ns")
        self.table_canvas.create_window((0, 0), window=table_frame, anchor="nw", 
                                        tags="table_frame")
        table_frame.bind("<Configure>",
            lambda event: self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all")))
        
        if table_data:
            
            self.delete_btn.state(["!disabled"])
            ttk.Style().configure("Bold.TLabel", font=("Arial", "10", "bold"))
            ttk.Label(table_frame, text="Date", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=1, sticky="w")
            ttk.Label(table_frame, text="Value", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=2, sticky="w")
            ttk.Label(table_frame, text="Description", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=3, sticky="w")
            ttk.Label(table_frame, text="Category", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=4, sticky="w")

            self.data_entry_cbuttons = []
            self.data_entry_ids = []
            for i, row in enumerate(table_data):
                self.data_entry_cbuttons.append(ttk.Checkbutton(table_frame))
                self.data_entry_cbuttons[-1].grid(row=1+i, column=0)
                self.data_entry_cbuttons[-1].state(["!alternate"])
                self.data_entry_ids.append(row[0])

                ttk.Label(table_frame, text=f"{row[1]}", relief="groove",
                          padding=(6, 0)).grid(row=1+i, column=1, sticky="nesw")
                ttk.Label(table_frame, text=f"{row[2]}{row[3]}", relief="groove",
                          padding=(6, 0)).grid(row=1+i, column=2, sticky="nesw")
                ttk.Label(table_frame, text=f"{row[4]}", relief="groove",
                          padding=(6, 0)).grid(row=1+i, column=3, sticky="nesw")
                ttk.Label(table_frame, text=f"{row[5]}", relief="groove",
                          padding=(6, 0)).grid(row=1+i, column=4, sticky="nesw")
            ttk.Label(
                table_frame,
                text=f"Spent: {balance['Expenses']:.2f}£\n"
                     f"Received: {balance['Received']:.2f}£\n"
                     f"Total balance: {balance['Total']:.2f}£").grid(columnspan=5, sticky="w")
        else:
            self.delete_btn.state(["disabled"])
            ttk.Label(table_frame, text="No data to show").pack(anchor="w")

        self.root.grid_rowconfigure(1, weight=1)
        table_frame.update_idletasks()

        if table_frame.winfo_height() < self.root.winfo_screenheight()*0.75:
            canvas_height = table_frame.winfo_height()
        else:
            canvas_height = self.root.winfo_screenheight()*0.75
        self.table_canvas.config(width=table_frame.winfo_width(), height=canvas_height)


def is_numeric(char):
    """Function to validate whether entry is numeric """
    try:
        float(char)
        return True
    except ValueError:
        return False

def main():
    root = tk.Tk()
    app = BudgetTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
