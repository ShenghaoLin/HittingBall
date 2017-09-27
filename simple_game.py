from tkinter import *
import tkinter.messagebox
import time

global R
R = 10


class GAME:
    def __init__(self):
        self.mainwindow = Tk()
        self.CV = Canvas(self.mainwindow, width=800, height=600)
        self.cx = 400
        self.cy = 300
        self.ball = self.CV.create_oval((self.cx - R, self.cy - R, self.cx + R, self.cy + R), fill='black')
        self.CV.bind("<W>", self.up)
        self.CV.bind("<A>", self.left)
        self.CV.bind("<S>", self.down)
        self.CV.bind("<D>", self.right)
        self.mainwindow.mainloop()

    def up(self):
        if self.cy <= 580:
            self.cy += 2
        self.CV.coords(self.ball, (self.cx - R, self.cy - R, self.cx + R, self.cy + R))

    def left(self):
        if self.cx >= 20:
            self.cx -= 2
        self.CV.coords(self.ball, (self.cx - R, self.cy - R, self.cx + R, self.cy + R))

    def down(self):
        if self.cy >= 20:
            self.cy -= 2
        self.CV.coords(self.ball, (self.cx - R, self.cy - R, self.cx + R, self.cy + R))

    def right(self):
        if self.cx <= 780:
            self.cx += 2
        self.CV.coords(self.ball, (self.cx - R, self.cy - R, self.cx + R, self.cy + R))


GUI = GAME()
