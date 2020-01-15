import tkinter as tk
from tkinter import ttk
 
window = tk.Tk()
canvas = tk.Canvas(window, width=1280, height=720)
window.title("Lift Algorithm")
window.geometry('1280x720')
height = 720
width = 1280

tab_control = ttk.Notebook(window)
tab_1 = tk.Frame(tab_control)
tab_2 = tk.Frame(tab_control)
tab_control.add(tab_1, text='Demonstrations')
tab_control.add(tab_2, text='Graphs')

base_label = tk.Label(tab_1, text="Base Algorithm", font=("Helvetica", 16), padx=5, pady=5)
new_label = tk.Label(tab_1, text="New Algorithm", font=("Helvetica", 16), padx=5, pady=5)
base_label.place(relx=0.25, rely=0)
new_label.place(relx=0.75, rely=0)

canvas.create_rectangle(50, 0, 100, 50, fill='red') 

tab_control.pack(expand=1, fill='both')
 
window.mainloop()