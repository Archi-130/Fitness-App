import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext

conn = sqlite3.connect('fitness_app.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        phone TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        height_cm REAL,
        weight_kg REAL,
        bmi REAL
    )
''')
conn.commit()

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return bmi

def suggest_exercises(bmi):
    if bmi < 18.5:
        return "Underweight: Strength training, yoga, balanced diet."
    elif 18.5 <= bmi < 24.9:
        return "Normal weight: Maintain routine, light cardio, yoga."
    elif 25 <= bmi < 29.9:
        return "Overweight: Cardio (walking, running), swimming, cycling."
    else:
        return "Obese: Low-impact cardio, swimming, consult a fitness trainer."

def create_account():
    phone = entry_phone.get()
    name = entry_name.get()
    try:
        age = int(entry_age.get())
        height_cm = float(entry_height.get())
        weight_kg = float(entry_weight.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numerical values for age, height, and weight.")
        return
    
    # Check if account exists
    cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
    existing = cursor.fetchone()
    if existing:
        messagebox.showinfo("Account Exists", "An account with this phone number already exists.")
        return
    
    bmi = calculate_bmi(weight_kg, height_cm)
    exercise = suggest_exercises(bmi)
    
    cursor.execute('''
        INSERT INTO customers (phone, name, age, height_cm, weight_kg, bmi)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (phone, name, age, height_cm, weight_kg, bmi))
    conn.commit()
    
    result_label.config(text=f"Your BMI is: {bmi:.2f}\n{exercise}")
    messagebox.showinfo("Success", "Your account has been created and saved!")

def fetch_account():
    phone = entry_phone.get()
    cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
    existing = cursor.fetchone()
    if existing:
        bmi = existing[5]
        exercise = suggest_exercises(bmi)
        result_label.config(text=f"Name: {existing[1]}\nAge: {existing[2]}\nHeight: {existing[3]} cm\nWeight: {existing[4]} kg\nBMI: {bmi:.2f}\n{exercise}")
    else:
        messagebox.showinfo("Not Found", "No account found with this phone number.")

def update_weight():
    phone = entry_phone.get()
    try:
        new_weight = float(entry_weight.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid numerical value for weight.")
        return
    
    cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
    existing = cursor.fetchone()
    if not existing:
        messagebox.showinfo("Not Found", "No account found with this phone number.")
        return
    
    height_cm = existing[3]
    new_bmi = calculate_bmi(new_weight, height_cm)
    exercise = suggest_exercises(new_bmi)
    
    cursor.execute("UPDATE customers SET weight_kg = ?, bmi = ? WHERE phone = ?", (new_weight, new_bmi, phone))
    conn.commit()
    
    result_label.config(text=f"Updated BMI is: {new_bmi:.2f}\n{exercise}")
    messagebox.showinfo("Success", "Weight and BMI have been updated!")

def view_all_customers():
    cursor.execute("SELECT * FROM customers")
    all_customers = cursor.fetchall()
    
    if not all_customers:
        messagebox.showinfo("No Records", "No customer records found.")
        return

    view_window = tk.Toplevel(root)
    view_window.title("All Customer Records")
    
    text_area = scrolledtext.ScrolledText(view_window, width=80, height=20)
    text_area.pack(padx=10, pady=10)
    
    text_area.insert(tk.END, "Phone\tName\tAge\tHeight(cm)\tWeight(kg)\tBMI\n")
    text_area.insert(tk.END, "-"*80 + "\n")
    for customer in all_customers:
        line = f"{customer[0]}\t{customer[1]}\t{customer[2]}\t{customer[3]}\t{customer[4]}\t{customer[5]:.2f}\n"
        text_area.insert(tk.END, line)
    
    text_area.config(state='disabled')

root = tk.Tk()
root.title("Fitness App")

tk.Label(root, text="Phone Number (Primary Key):").grid(row=0, column=0, sticky='w')
entry_phone = tk.Entry(root)
entry_phone.grid(row=0, column=1)

tk.Label(root, text="Name:").grid(row=1, column=0, sticky='w')
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1)

tk.Label(root, text="Age:").grid(row=2, column=0, sticky='w')
entry_age = tk.Entry(root)
entry_age.grid(row=2, column=1)

tk.Label(root, text="Height (cm):").grid(row=3, column=0, sticky='w')
entry_height = tk.Entry(root)
entry_height.grid(row=3, column=1)

tk.Label(root, text="Weight (kg):").grid(row=4, column=0, sticky='w')
entry_weight = tk.Entry(root)
entry_weight.grid(row=4, column=1)

tk.Button(root, text="Create Account / Submit", command=create_account).grid(row=5, column=0, pady=10)
tk.Button(root, text="Fetch Existing Account", command=fetch_account).grid(row=5, column=1, pady=10)
tk.Button(root, text="Update Weight & Recalculate BMI", command=update_weight).grid(row=6, column=0, pady=10)
tk.Button(root, text="View All Customers (Admin)", command=view_all_customers).grid(row=6, column=1, pady=10)

result_label = tk.Label(root, text="", fg="blue", font=("Arial", 12))
result_label.grid(row=7, column=0, columnspan=2, pady=20)

root.mainloop()
conn.close()