from tkinter import *
import time

class alien(object):
     def __init__(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, width=350, height = 800)
        self.canvas.pack()
        self.alien1 = self.canvas.create_oval(20, 260, 120, 360, outline='white', fill='blue')
        self.alien2 = self.canvas.create_rectangle(2, 2, 80, 100, outline='black',)
        self.canvas.pack()
        self.root.after(0, self.animation)
        self.root.mainloop()

     def animation(self):
        track = 0
        while True:
            x = 0
            y = 5
            if track == 0:
               for i in range(0,51):
                    time.sleep(0.025)
                    self.canvas.move(self.alien1, x, y)
                    self.canvas.move(self.alien2, x, y)
                    self.canvas.update()
               track = 1
               print("check")

            else:
               for i in range(0,51):
                    time.sleep(0.025)
                    self.canvas.move(self.alien1, x, -y)
                    self.canvas.move(self.alien2, x, -y)
                    self.canvas.update()
               track = 0
            print(track)

alien()