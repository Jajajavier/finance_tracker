import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import subprocess
import json

# File to store transactions
DATA_FILE = "transactions.txt"
CONFIG_FILE = "github_config.txt"

# Function to load transactions from file
def load_transactions():
    transactions = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            for line in file:
                date, desc, amount = line.strip().split("|")
                transactions.append((date, desc, float(amount)))
    return transactions

# Function to save transactions to file
def save_transactions(transactions):
    with open(DATA_FILE, "w") as file:
        for date, desc, amount in transactions:
            file.write(f"{date}|{desc}|{amount}\n")

# Function to update balance
def update_balance(target_date=None):
    if target_date is None:
        target_date = datetime.now()
    else:
        try:
            target_date = datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                target_date = datetime.strptime(target_date, "%Y-%m-%d")
                target_date = target_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                messagebox.showerror("Invalid date format", "Date must be in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format")
                return

    balance = 0.0
    for date, _, amount in transactions:
        if datetime.strptime(date, "%Y-%m-%d %H:%M:%S") <= target_date:
            balance += amount
    balance_label.config(text=f"Balance on {target_date.strftime('%Y-%m-%d %H:%M:%S')}: ${balance:.2f}")

# Function to add a new transaction
def add_transaction():
    date_str = date_entry.get()
    if not date_str:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Invalid date format", "Date must be in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format")
                return
    
    desc = desc_entry.get()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Amount must be a number")
        return

    if transaction_type.get() == "Expense":
        amount = -amount

    transactions.append((date, desc, amount))
    transactions.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"))
    save_transactions(transactions)
    update_balance()

    transactions_listbox.delete(0, tk.END)
    for date, desc, amount in transactions:
        transactions_listbox.insert(tk.END, f"{date} | {desc} | ${amount:.2f}")
    
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

# Function to edit a selected transaction
def edit_transaction():
    selected_index = transactions_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Select an entry", "Please select a transaction to edit.")
        return

    selected_index = selected_index[0]
    selected_transaction = transactions[selected_index]

    new_date = simpledialog.askstring("Edit Date", "Enter new date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS):", initialvalue=selected_transaction[0])
    if not new_date:
        return
    try:
        new_date = datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            new_date = datetime.strptime(new_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Invalid date format", "Date must be in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format")
            return

    new_desc = simpledialog.askstring("Edit Description", "Enter new description:", initialvalue=selected_transaction[1])
    if not new_desc:
        return

    new_amount_str = simpledialog.askstring("Edit Amount", "Enter new amount:", initialvalue=str(selected_transaction[2]))
    try:
        new_amount = float(new_amount_str)
    except ValueError:
        messagebox.showerror("Invalid input", "Amount must be a number")
        return

    transactions[selected_index] = (new_date, new_desc, new_amount)
    transactions.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"))
    save_transactions(transactions)
    update_balance()

    transactions_listbox.delete(0, tk.END)
    for date, desc, amount in transactions:
        transactions_listbox.insert(tk.END, f"{date} | {desc} | ${amount:.2f}")

# Function to duplicate a selected transaction for a different date
def duplicate_transaction():
    selected_index = transactions_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Select an entry", "Please select a transaction to duplicate.")
        return

    selected_index = selected_index[0]
    selected_transaction = transactions[selected_index]

    # Calculate the suggested default date (next month, same day)
    original_date = datetime.strptime(selected_transaction[0], "%Y-%m-%d %H:%M:%S")
    next_month_date = original_date + relativedelta(months=1)
    new_date = next_month_date.strftime("%Y-%m-%d %H:%M:%S")

    new_date = simpledialog.askstring("Duplicate Date", "Enter new date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS):", initialvalue=new_date)
    if not new_date:
        return
    try:
        new_date = datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            new_date = datetime.strptime(new_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("Invalid date format", "Date must be in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format")
            return

    new_desc = selected_transaction[1]
    new_amount = selected_transaction[2]

    transactions.append((new_date, new_desc, new_amount))
    transactions.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"))
    save_transactions(transactions)
    update_balance()

    transactions_listbox.delete(0, tk.END)
    for date, desc, amount in transactions:
        transactions_listbox.insert(tk.END, f"{date} | {desc} | ${amount:.2f}")

# Function to synchronize with GitHub
def synchronize_with_github():
    subprocess.run(["python", "github_sync.py"])

# Load existing transactions
transactions = load_transactions()

# Create main window
root = tk.Tk()
root.title("Finance Tracker")

# Create UI components
balance_label = tk.Label(root, text="Balance: $0.00", font=("Arial", 16))
balance_label.pack(pady=10)

date_balance_frame = tk.Frame(root)
date_balance_frame.pack(pady=10)

date_balance_label = tk.Label(date_balance_frame, text="Enter date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS):")
date_balance_label.pack(side=tk.LEFT, padx=5)

balance_date_entry = tk.Entry(date_balance_frame, width=20)
balance_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
balance_date_entry.pack(side=tk.LEFT, padx=5)

show_balance_button = tk.Button(date_balance_frame, text="Show Balance", command=lambda: update_balance(balance_date_entry.get()))
show_balance_button.pack(side=tk.LEFT, padx=5)

transactions_frame = tk.Frame(root)
transactions_frame.pack(pady=10)

transactions_listbox = tk.Listbox(transactions_frame, width=50)
transactions_listbox.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(transactions_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

transactions_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=transactions_listbox.yview)

for date, desc, amount in transactions:
    transactions_listbox.insert(tk.END, f"{date} | {desc} | ${amount:.2f}")

desc_label = tk.Label(root, text="Description:")
desc_label.pack(pady=5)
desc_entry = tk.Entry(root, width=40)
desc_entry.pack(pady=5)

amount_label = tk.Label(root, text="Amount:")
amount_label.pack(pady=5)
amount_entry = tk.Entry(root, width=20)
amount_entry.pack(pady=5)

transaction_type = tk.StringVar(value="Income")
income_radio = tk.Radiobutton(root, text="Income", variable=transaction_type, value="Income")
income_radio.pack()
expense_radio = tk.Radiobutton(root, text="Expense", variable=transaction_type, value="Expense")
expense_radio.pack()

date_label = tk.Label(root, text="Enter date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS):")
date_label.pack(pady=5)
date_entry = tk.Entry(root, width=20)
date_entry.pack(pady=5)

add_button = tk.Button(root, text="Add Transaction", command=add_transaction)
add_button.pack(pady=10)

edit_button = tk.Button(root, text="Edit Transaction", command=edit_transaction)
edit_button.pack(pady=10)

duplicate_button = tk.Button(root, text="Duplicate Transaction", command=duplicate_transaction)
duplicate_button.pack(pady=10)

sync_button = tk.Button(root, text="Sync with GitHub", command=synchronize_with_github)
sync_button.pack(pady=10)

# Update the balance initially
update_balance()

# Start the main loop
root.mainloop()
