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
import matplotlib.pyplot as plt
import sqlite3
import backend

class EntryFrame(tk.Toplevel):
    """Class that handles the frame to enter data.

    Attributes:
        database (string): path to the SQLite database file
        main_window (BudgetTracker): instance of BudgetTracker class.
            used to manage the main window of the application
        widgets (dict): stores all the tkinter widgets that need to accessed from
            other methods in class
        status_message (tkinter.StringVar): holds information text to 
            be outputted
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
        # hide window in background during drawing
        self.withdraw()
        self.title("Enter a transaction")
        self.configure(background="white")
        self.status_message = tk.StringVar()
        self.widgets = {}

        validation = self.register(lambda char: is_numeric(char) or char in ".-")

        ttk.Label(self, text="Date").grid(row=0, column=0)

        self.widgets["entry_date"] = DateEntry(self, date_pattern='yyyy/mm/dd')
        self.widgets["entry_date"].grid(row=1, column=0)
        
        ttk.Label(self, text="Value").grid(row=0, column=1)

        self.widgets["entry_value"] = ttk.Entry(self,
                                                validate="key",
                                                validatecommand=(validation, '%S'))

        self.widgets["entry_value"].grid(row=1, column=1)

        ttk.Label(self, text="Currency").grid(row=0, column=2)
        
        self.var_currency = tk.StringVar()

        currencies = {'£', '$', '€'}
        ttk.OptionMenu(self, self.var_currency, '£', *currencies).grid(row=1, column=2)

        ttk.Label(self, text="Description").grid(row=0, column=3)

        self.widgets["entry_description"] = ttk.Entry(self)
        self.widgets["entry_description"].grid(row=1, column=3)

        ttk.Label(self, text="Category").grid(row=0, column=4)
        
        self.var_category = tk.StringVar()

        categories = {'Groceries', 'Shopping', 'Entertainment', 'Restaurants/Bars',
                      'Subscriptions', 'Rent', 'Sports', 'Transport',
                      'Debt', 'Salary', 'Cash withdrawal', 'Other'}
        ttk.OptionMenu(self,
                       self.var_category,
                       'Groceries',
                       *categories).grid(row=1, column=4)

        ttk.Button(self, text="Enter", command=self.on_enter).grid(row=1, column=5)

        ttk.Button(self, text="Close", command=self.on_close).grid(row=1, column=6)
        
        ttk.Label(self, textvariable=self.status_message).grid(row=2,
                                                               columnspan=7,
                                                               sticky="w")

        self.focus_force()
        self.main_window.is_entry_window_open = True

        self.update_idletasks()
        self.deiconify()
        x_position = int(self.main_window.root.winfo_x()
                         + self.main_window.root.winfo_width()/2
                         - self.winfo_width()/2)
        y_position = int(self.main_window.root.winfo_y()
                         + self.main_window.root.winfo_height()/2
                         - self.winfo_height()/2)
        self.geometry(f"+{x_position}+{y_position}")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        

    def on_enter(self):
        """Checks if entered data valid. If it is, enters to database"""

        now = datetime.datetime.now().strftime("[%H:%M:%S]")

        try:
            entry = (self.widgets["entry_date"].get_date(),
                     float(self.widgets["entry_value"].get()),
                     self.var_currency.get(),
                     self.widgets["entry_description"].get(),
                     self.var_category.get())

            if not self.widgets["entry_description"].get():
                raise EmptyDescriptionError()
     
        except ValueError:
            if len(self.status_message.get().split("\n")) > 10: #number of lines more than 10 
                self.status_message.set(
                    "{}".format('\n'.join((self.status_message.get().split("\n"))[1:]))
                    + f"{now} "
                    + "Whooops, looks like you entered a wrong value. Try again!\n")
            else:
                self.status_message.set(
                    self.status_message.get()
                    + f"{now} "
                    + "Whooops, looks like you entered a wrong value. Try again!\n")
        except EmptyDescriptionError:
            if len(self.status_message.get().split("\n")) > 10: #number of lines more than 10 
                self.status_message.set(
                    "{}".format('\n'.join((self.status_message.get().split("\n"))[1:]))
                    + f"{now} "
                    + "Failed to insert data. Please enter description\n")
            else:
                self.status_message.set(
                    self.status_message.get()
                    + f"{now} "
                    + "Failed to insert data. Please enter description\n")

        else:
            conn = backend.create_connection(self.database)

            if conn is None:
                self.status_message.set("Error! cannot create the database connection.")
            with conn:
                try:
                    backend.create_transaction(conn, entry)
                except sqlite3.OperationalError as e:
                    if str(e) == "no such table: transactions":
                        backend.create_transactions_table(conn)
                        backend.create_transaction(conn, entry)
                        self.status_message.set("Created a new 'transactions' table\n")
                    else:
                        raise

            if len(self.status_message.get().split("\n")) > 10: #number of lines more than 10 
                self.status_message.set(
                    "{}".format('\n'.join((self.status_message.get().split("\n"))[1:]))
                    + f"{now} " + "Succesfully inserted into database\n")
            else:
                self.status_message.set(
                    self.status_message.get()
                    + f"{now} " + "Succesfully inserted into database\n")
            self.widgets["entry_value"].delete(0, "end")
            self.widgets["entry_description"].delete(0, "end")

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
        widgets (dict): stores all the tkinter widgets that need to accessed from
            other methods in class
        apply_filters_state (tkinter.IntVar): Holds state if filters are to be applied
        var_category (tkinter.StringVar): Holds category to be shown
        in_value_range_state (tkinter.IntVar): holds state whether to filter entries
            by value
        search_description_state (tkinter.IntVar): holds state whether to search in
            description
        data_entry_ids (list): list containing ids of returned data entries
        expenses_by_category (dict): stores total balance for each category found.
            Used to plot bar chart.
    """
    def __init__(self, parent):
        """
        Parameters:
            parent (tkinter.tk): widget representing the main window of application
        """
        self.database = "transaction_database.db"
        self.root = parent
        self.root.title("Budget tracker")
        self.root.configure(background="white")
        # hide window in background during drawing
        self.root.withdraw()
        self.root.update_idletasks() 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
            
        x_coordinate = int((screen_width / 2) - (window_width / 2))  
        y_coordinate = int((screen_height / 10) - (window_height / 10))
        
        self.root.geometry(f"+{x_coordinate}+{y_coordinate}")

        self.is_entry_window_open = False

        self.widgets = {}

        gui_style = ttk.Style()
        gui_style.configure('TFrame', background='white')
        gui_style.configure('TLabel', background='white')
        gui_style.configure('TCheckbutton', background='white')
        gui_style.configure('TMenubutton', background='white')

        menu_frame = ttk.Frame(self.root)
        menu_frame.grid(row=0, column=0, columnspan=2)

        ttk.Label(menu_frame, text="Date").grid(row=0, column=1)

        ttk.Label(menu_frame, text="From: ").grid(row=1, column=0)

        self.widgets["date_from"] = DateEntry(menu_frame, date_pattern='y-mm-dd')
        self.widgets["date_from"].grid(row=1, column=1)

        ttk.Label(menu_frame, text="To: ").grid(row=2, column=0)

        self.widgets["date_to"] = DateEntry(menu_frame, date_pattern='y-mm-dd')
        self.widgets["date_to"].grid(row=2, column=1)

        ttk.Button(menu_frame, text="Show transactions",
                   command=self.on_show_entries).grid(row=3, column=0, columnspan=2,
                                                      sticky="nesw")

        add_btn = ttk.Button(
            menu_frame,
            text="Add new transactions",
            command=lambda: EntryFrame(self) if not self.is_entry_window_open else None)
        add_btn.grid(row=4, column=0)

        self.widgets["delete_btn"] = ttk.Button(
            menu_frame,
            text="Delete selected",
            command=self.on_delete)

        self.widgets["delete_btn"].grid(row=4, column=1, sticky="nesw")
        self.widgets["delete_btn"].state(["disabled"])

        plot_bar_chart_btn = ttk.Button(
            menu_frame,
            text="Plot bar charts",
            command=self.on_plot_bar_charts)
        plot_bar_chart_btn.grid(row=5, column=0, sticky="nesw")


        self.widgets["status_msg"] = ttk.Label(menu_frame, foreground="red")
        self.widgets["status_msg"].grid(row=6, column=0, columnspan=4, sticky="w")

        self.apply_filters_state = tk.IntVar()
        apply_filter_cbtn = ttk.Checkbutton(menu_frame,
                                            variable=self.apply_filters_state,
                                            text="Apply filters",
                                            command=self.on_change_apply_filters_state)
        apply_filter_cbtn.grid(row=0, column=2, columnspan=2)

        ttk.Label(
            menu_frame,
            text="Show only from category:").grid(row=1, column=2, columnspan=3)

        categories = {'Groceries', 'New items', 'Entertainment', 'Eating out',
                      'Drinks', 'Subscriptions', 'Rent', 'Leisure', 'Transport',
                      'Debt', 'Salary', 'Cash withdrawal', 'All'}
        self.var_category = tk.StringVar()
        self.widgets["show_only_menu"] = ttk.OptionMenu(menu_frame,
                                                        self.var_category,
                                                        "All",
                                                        *categories)
        self.widgets["show_only_menu"].grid(row=1, column=5)
        self.widgets["show_only_menu"].configure(state="disabled")

        self.in_value_range_state = tk.IntVar()
        self.widgets["in_value_range_cbutton"] = ttk.Checkbutton(
            menu_frame,
            variable=self.in_value_range_state,
            text="In value range: ",
            command=self.on_change_in_value_range_state)
        self.widgets["in_value_range_cbutton"].grid(row=2, column=2, columnspan=4)
        self.widgets["in_value_range_cbutton"].configure(state="disabled")

        ttk.Label(menu_frame, text="Min(£):").grid(row=3, column=2)

        validation = self.root.register(lambda char: is_numeric(char) or char in ".-")

        self.widgets["minimum_value_entry"] = ttk.Entry(
            menu_frame,
            width=6,
            justify="center",
            validate="key",
            validatecommand=(validation, '%S'))
        self.widgets["minimum_value_entry"].grid(row=3, column=3)
        self.widgets["minimum_value_entry"].insert(0, "0.0")
        self.widgets["minimum_value_entry"].configure(state="disabled")


        ttk.Label(menu_frame, text="Max(£):").grid(row=3, column=4)

        self.widgets["maximum_value_entry"] = ttk.Entry(
            menu_frame,
            width=6,
            justify="center",
            validate="key",
            validatecommand=(validation, '%S'))
        self.widgets["maximum_value_entry"].grid(row=3, column=5)
        self.widgets["maximum_value_entry"].insert(0, "0.0")
        self.widgets["maximum_value_entry"].configure(state="disabled")

        self.search_description_state = tk.IntVar()
        self.widgets["search_description_cbutton"] = ttk.Checkbutton(
            menu_frame,
            variable=self.search_description_state,
            text="Search in description: ",
            command=self.on_change_search_description_state)
        self.widgets["search_description_cbutton"].grid(row=4, column=2, columnspan=4)
        self.widgets["search_description_cbutton"].configure(state="disabled")

        self.widgets["search_description_entry"] = ttk.Entry(menu_frame)
        self.widgets["search_description_entry"].grid(row=5, column=2, columnspan=4)
        self.widgets["search_description_entry"].configure(state="disabled")

        self.widgets["table_canvas"] = None
        self.widgets["scroll_bar"] = None
        self.widgets["data_entry_cbuttons"] = []
        self.data_entry_ids = []
        self.expenses_by_category = {}

        self.root.deiconify()
        

    def on_delete(self):
        """Deletes selected entries of the table."""
        selected_rows = []
        for cbutton in self.widgets["data_entry_cbuttons"]:
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
        """Changes state of filter widgets."""
        if self.apply_filters_state.get():
            self.widgets["show_only_menu"].configure(state="enabled")
            self.widgets["in_value_range_cbutton"].configure(state="enabled")
            self.widgets["search_description_cbutton"].configure(state="enabled")
            if self.in_value_range_state.get():
                self.widgets["minimum_value_entry"].configure(state="enabled")
                self.widgets["maximum_value_entry"].configure(state="enabled")
            if self.search_description_state.get():
                self.widgets["search_description_entry"].configure(state="enabled")

        else:
            self.widgets["show_only_menu"].configure(state="disabled")
            self.widgets["in_value_range_cbutton"].configure(state="disabled")
            self.widgets["minimum_value_entry"].configure(state="disabled")
            self.widgets["maximum_value_entry"].configure(state="disabled")
            self.widgets["search_description_cbutton"].configure(state="disabled")
            self.widgets["search_description_entry"].configure(state="disabled")

    def on_change_in_value_range_state(self):
        """Changes state of maximum and minimum value entries."""
        if self.in_value_range_state.get():
            self.widgets["minimum_value_entry"].configure(state="enabled")
            self.widgets["maximum_value_entry"].configure(state="enabled") 
        else:
            self.widgets["minimum_value_entry"].configure(state="disabled")
            self.widgets["maximum_value_entry"].configure(state="disabled")

    def on_change_search_description_state(self):
        """Changes state of search in description entry."""
        if self.search_description_state.get():
            self.widgets["search_description_entry"].configure(state="enabled")
        else:
            self.widgets["search_description_entry"].configure(state="disabled")

    def on_plot_bar_charts(self):
        """Plot bar charts to visualize retrieved data """
        conn = backend.create_connection(self.database)
        if conn is None:
            self.widgets["status_msg"].configure(
                text="Error. Cannot create database connection")
        with conn:
            try:
                if self.apply_filters_state.get():
                    if self.in_value_range_state.get():
                        if self.search_description_state.get():
                            self.expenses_by_category = backend.get_expenses_by_category()
                        else:
                            self.expenses_by_category = backend.get_expenses_by_category(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                float(self.widgets["minimum_value_entry"].get()),
                                float(self.widgets["maximum_value_entry"].get()),
                                self.var_category.get())
                    else:
                        if self.search_description_state.get():
                            self.expenses_by_category = backend.get_expenses_by_category(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get(),
                                self.widgets["search_description_entry"].get())
                        else:
                            self.expenses_by_category = backend.get_expenses_by_category(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get())
                else:
                    self.expenses_by_category = backend.get_expenses_by_category(
                        conn,
                        self.widgets["date_from"].get(),
                        self.widgets["date_to"].get())

            except ValueError:
                self.widgets["status_msg"].configure(
                    text="Error. Invalid min or max value")
                return
            except sqlite3.OperationalError as e :
                if str(e) == "no such table: transactions":
                    self.widgets["status_msg"].configure(
                        text="Database error. Could not find table 'transactions'.")
                    return
            else:
                self.widgets["status_msg"].configure(text="")
        if not self.expenses_by_category:
            self.widgets["status_msg"].configure(
                text="No data to show")
            return
        else:
            self.widgets["status_msg"].configure(text="")

        salary = self.expenses_by_category.pop("Salary", 0)
        if len(self.expenses_by_category.keys()) > 1: # Need at least 2 categories to compare
            fig1 = plt.figure(figsize=(14, 6))
            axes1 = fig1.gca()
            axes1.bar(list(self.expenses_by_category.keys()),
                    self.expenses_by_category.values(),
                    color="#87e37d")
            axes1.set_ylabel("Balance (£)")
            axes1.set_title(f"Expenses from {self.widgets['date_from'].get()} to {self.widgets['date_to'].get()}")
            for i, v in enumerate(self.expenses_by_category.values()):
                axes1.text(i-0.25, v, str(round(v,2)), fontweight="bold")
            plt.tight_layout()
            axes1.grid()
            fig2 = plt.figure()
            axes2 = fig2.gca()
            color_list = ['silver', 'lightcoral', 'red', 'peru', 'orange', 'gold',
                         'yellowgreen', 'lime', 'turquoise', 'deepskyblue', 'blue', 'indogo']
            data = {}
            data["Earnings"] = salary
            data["Expenses"] = 0
            axes2.bar(data.keys(), [salary, 0], label="Earnings")
            for idx, item in enumerate(self.expenses_by_category.values()):
                if item < 0:
                    axes2.bar(
                        data.keys(), [0, -item], bottom=data["Expenses"],
                        color=color_list[idx%len(color_list)],
                        label =f"{list(self.expenses_by_category.keys())[idx]}")
                    data["Expenses"]+=-item
                else:
                    axes2.bar(
                        data.keys(), [item, 0], bottom=data["Earnings"],
                        color=color_list[idx%len(color_list)],
                        label =f"{list(self.expenses_by_category.keys())[idx]}")
                    data["Earnings"]+=item

            for i, v in enumerate(data.values()):
                axes2.text(i-.1, v, str(round(v,2)), fontweight="bold")

            axes2.legend(loc="best", prop={'size': 6}).set_draggable(True)
            axes2.set_ylabel("Amount (£)")
            axes2.grid()
        
            plt.show()
        else:
            self.widgets["status_msg"].configure(
                text="Need data from at least 2 categories")

    def on_show_entries(self):
        """Displays the data table according to conditions given."""
        conn = backend.create_connection(self.database)
        if conn is None:
            self.widgets["status_msg"].configure(
                text="Error. Cannot create database connection")
        with conn:
            try:
                if self.apply_filters_state.get():
                    if self.in_value_range_state.get():
                        if self.search_description_state.get():
                            table_data = backend.select_transactions(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                float(self.widgets["minimum_value_entry"].get()),
                                float(self.widgets["maximum_value_entry"].get()),
                                self.var_category.get(),
                                self.widgets["search_description_entry"].get())
                            balance = backend.get_balance(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                float(self.widgets["minimum_value_entry"].get()),
                                float(self.widgets["maximum_value_entry"].get()),
                                self.var_category.get(),
                                self.widgets["search_description_entry"].get())
                            self.expenses_by_category = backend.get_expenses_by_category()
                        else:
                            table_data = backend.select_transactions(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                float(self.widgets["minimum_value_entry"].get()),
                                float(self.widgets["maximum_value_entry"].get()),
                                self.var_category.get())
                            balance = backend.get_balance(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                float(self.widgets["minimum_value_entry"].get()),
                                float(self.widgets["maximum_value_entry"].get()),
                                self.var_category.get())
                            self.expenses_by_category = backend.get_expenses_by_category(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                float(self.widgets["minimum_value_entry"].get()),
                                float(self.widgets["maximum_value_entry"].get()),
                                self.var_category.get())
                    else:
                        if self.search_description_state.get():
                            table_data = backend.select_transactions(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get(),
                                self.widgets["search_description_entry"].get())
                            balance = backend.get_balance(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get(),
                                self.widgets["search_description_entry"].get())
                            self.expenses_by_category = backend.get_expenses_by_category(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get(),
                                self.widgets["search_description_entry"].get())
                        else:
                            table_data = backend.select_transactions(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get())
                            balance = backend.get_balance(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get())
                            self.expenses_by_category = backend.get_expenses_by_category(
                                conn,
                                self.widgets["date_from"].get(),
                                self.widgets["date_to"].get(),
                                self.var_category.get())
                else:
                    table_data = backend.select_transactions(
                        conn,
                        self.widgets["date_from"].get(),
                        self.widgets["date_to"].get())
                    balance = backend.get_balance(
                        conn,
                        self.widgets["date_from"].get(),
                        self.widgets["date_to"].get())
                    self.expenses_by_category = backend.get_expenses_by_category(
                        conn,
                        self.widgets["date_from"].get(),
                        self.widgets["date_to"].get())

            except ValueError:
                self.widgets["status_msg"].configure(
                    text="Error. Invalid min or max value")
                return
            except sqlite3.OperationalError as e :
                if str(e) == "no such table: transactions":
                    self.widgets["status_msg"].configure(
                        text="Database error. Could not find table 'transactions'.")
                    return
                else:
                    raise
            else:
                self.widgets["status_msg"].configure(text="")
        
        if self.widgets["table_canvas"]:
            self.widgets["table_canvas"].destroy()
        if self.widgets["scroll_bar"]:
            self.widgets["scroll_bar"].destroy()
        
        if table_data:
            self.widgets["table_canvas"] = tk.Canvas(self.root,
                                                     highlightthickness=0,
                                                     background="White")
            table_frame = ttk.Frame(self.widgets["table_canvas"])
            self.widgets["scroll_bar"] = ttk.Scrollbar(
                self.root,
                orient="vertical",
                command=self.widgets["table_canvas"].yview)
            self.widgets["table_canvas"].configure(
                yscrollcommand=self.widgets["scroll_bar"].set)

            self.widgets["table_canvas"].grid(row=1, column=0, sticky="ns")
            self.widgets["scroll_bar"].grid(row=1, column=1, sticky="ns")
            self.widgets["table_canvas"].create_window((0, 0),
                                                       window=table_frame, anchor="nw",
                                                       tags="table_frame")
            table_frame.bind(
                "<Configure>",
                lambda event: self.widgets["table_canvas"].configure(
                    scrollregion=self.widgets["table_canvas"].bbox("all")))    
            self.widgets["status_msg"].configure(text="")
            self.widgets["delete_btn"].state(["!disabled"])
            ttk.Style().configure("Bold.TLabel", font=("Arial", "10", "bold"))
            ttk.Label(table_frame, text="Date", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=1, sticky="w")
            ttk.Label(table_frame, text="Value", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=2, sticky="w")
            ttk.Label(table_frame, text="Description", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=3, sticky="w")
            ttk.Label(table_frame, text="Category", style="Bold.TLabel",
                      padding=(6, 0)).grid(row=0, column=4, sticky="w")

            self.widgets["data_entry_cbuttons"] = []
            self.data_entry_ids = []
            for i, row in enumerate(table_data):
                self.widgets["data_entry_cbuttons"].append(ttk.Checkbutton(table_frame))
                self.widgets["data_entry_cbuttons"][-1].grid(row=1+i, column=0)
                self.widgets["data_entry_cbuttons"][-1].state(["!alternate"])
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
                     f"Total balance: {balance['Total']:.2f}£").grid(columnspan=5,
                                                                     sticky="w")

            self.root.grid_rowconfigure(1, weight=1)
            table_frame.update_idletasks()

            if table_frame.winfo_height() < self.root.winfo_screenheight()*0.75:
                canvas_height = table_frame.winfo_height()
            else:
                canvas_height = self.root.winfo_screenheight()*0.75
            self.widgets["table_canvas"].config(width=table_frame.winfo_width(),
                                                height=canvas_height)
        else:
            self.widgets["delete_btn"].state(["disabled"])
            self.widgets["status_msg"].configure(
                text="No data to show")
            return


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
