import tkinter as Tk

from tkcalendar import DateEntry
import BudgetTracker


##########################################################################
class EntryFrame(Tk.Toplevel):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, original):
        """Constructor"""
        self.database = "transaction_database.db"
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.title("Enter a transaction")

        label_date = Tk.Label(self, text="Date")
        label_date.grid(row=0,column=0)
        self.entry_date = DateEntry(self)
        self.entry_date.grid(row=1,column=0)

        label_value = Tk.Label(self, text="Value")
        label_value.grid(row=0,column=1)
        self.entry_value = Tk.Entry(self)
        self.entry_value.grid(row=1,column=1)

        label_currency = Tk.Label(self, text="Currency")
        label_currency.grid(row=0,column=2)
        self.var_currency = Tk.StringVar(self)
        self.var_currency.set('£')
        currencies ={'£','$','€'}
        cur_popmenu = Tk.OptionMenu(self,self.var_currency,*currencies)
        cur_popmenu.grid(row=1, column=2)


        label_description = Tk.Label(self, text="Description")
        label_description.grid(row=0,column=3)
        self.entry_description = Tk.Entry(self)
        self.entry_description.grid(row=1,column=3)


        label_type = Tk.Label(self, text="Type")
        label_type.grid(row=0,column=4)
        self.var_type = Tk.StringVar(self)
        self.var_type.set('Groceries')
        types= {'Groceries','New items','Entertainment','Eating out',\
                'Drinks','Subscriptions','Rent','Leisure','Transport','Debt'}
        types_popmenu = Tk.OptionMenu(self,self.var_type,*types)
        types_popmenu.grid(row=1,column=4)
        
        enterbtn = Tk.Button(self, text="Enter", command=self.onEnter)
        enterbtn.grid(row=1,column=5)

        cancelbtn = Tk.Button(self, text="Cancel", command=self.onCancel)
        cancelbtn.grid(row=1,column=6)
        
 
    #----------------------------------------------------------------------
    def onEnter(self):
        """"""
        try:
            temp=(str(self.entry_date.get_date()),float(self.entry_value.get()),self.var_currency.get(),\
                    self.entry_description.get(),self.var_type.get())
        except:
            print("Whooops, looks like you entered a wrong value. Try again!\n")
        else:
            conn=BudgetTracker.create_connection(self.database)

            if conn == None:
                print("Error! cannot create the database connection.")
            with conn:
                BudgetTracker.create_transaction(conn,temp)
            
            self.destroy()
            self.original_frame.showWindow()
    def onCancel(self):
        self.destroy()
        self.original_frame.showWindow()

class HistoryFrame(Tk.Toplevel):
    
    def __init__(self,original):
        self.database = "transaction_database.db"
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.title("Browse history")

        label_year = Tk.Label(self, text="Year")
        label_year.grid(row=0,column=0)
        self.var_year = Tk.StringVar(self)
        self.var_year.set('2019')
        years =['2017','2018','2019']
        year_popmenu = Tk.OptionMenu(self,self.var_year,*years)
        year_popmenu.grid(row=1, column=0)

        label_month = Tk.Label(self, text="Month")
        label_month.grid(row=0,column=1)
        self.var_month = Tk.StringVar(self)
        self.var_month.set('01')
        months =['01','02','03','04','05','06','07','08','09','10','11','12']
        month_popmenu = Tk.OptionMenu(self,self.var_month,*months)
        month_popmenu.grid(row=1, column=1)

        enterbtn = Tk.Button(self, text="Show entries", command=self.onShowEntries)
        enterbtn.grid(row=1,column=2)

        balancebtn = Tk.Button(self, text="Show balance", command=self.onShowBalance)
        balancebtn.grid(row=1,column=3)
        
        closebtn = Tk.Button(self,text="Return", command=self.onReturn)
        closebtn.grid(row=1,column=4)

        self.display = Tk.Label(self)
        self.display.grid(row=2, columnspan=5)

    def onShowEntries(self):
        conn=BudgetTracker.create_connection(self.database)
        if conn == None:
            print("Error! cannot create the database connection.")
        with conn:
            self.display.config(text=BudgetTracker.select_transactions(conn,self.var_year.get(),self.var_month.get()))

    def onShowBalance(self):
        conn=BudgetTracker.create_connection(self.database)
        if conn == None:
            print("Error! cannot create the database connection.")
        with conn:
            self.display.config(text=BudgetTracker.show_balance(conn,self.var_year.get(),self.var_month.get()))

    def onReturn(self):
        self.destroy()
        self.original_frame.showWindow()
        

        
 
########################################################################
class MyApp:
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        self.database = "transaction_database.db"
        self.root = parent
        self.root.title("Budget tracker")
        self.frame = Tk.Frame(parent)
        self.frame.pack()
        
 
        btn = Tk.Button(self.frame, text="Add new transaction", command=self.openEntryFrame)
        btn.grid(row=0,column=0)

        show_btn = Tk.Button(self.frame, text="History", command=self.showTransactions) 
        show_btn.grid(row=0,column=1)
        
    def showTransactions(self):
        self.root.withdraw()
        HistoryFrame(self)
        
    def openEntryFrame(self):
        """"""
        self.root.withdraw()
        EntryFrame(self)
 
    def showWindow(self):
        """"""
        self.root.update()
        self.root.deiconify()
 

if __name__ == "__main__":
    root = Tk.Tk()
    root.geometry("400x300")
    app = MyApp(root)
    root.mainloop()
