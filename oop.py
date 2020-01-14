import tkinter as tk
from tkinter import ttk

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        tab_control = ttk.Notebook(self)
        tab_1 = tk.Frame(tab_control)
        tab_2 = tk.Frame(tab_control)
        tab_control.add(tab_1, text='Demonstrations')
        tab_control.add(tab_2, text='Graphs')

        base_label = tk.Label(tab_1, text="Base Algorithm", font=("Helvetica", 16), padx=5, pady=5)
        new_label = tk.Label(tab_1, text="New Algorithm", font=("Helvetica", 16), padx=5, pady=5)
        base_label.place(relx=0.25, rely=0)
        new_label.place(relx=0.75, rely=0)
        tab_control.pack(expand=1, fill='both')

        canvas.create_rectangle(230, 10, 290, 60, outline="#f11", fill="#1f1", width=2)
        #root.create_rectangle(50, 0, 100, 50, fill='red')


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()