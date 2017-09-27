from tkinter import *
import tkinter.messagebox
import math
import chat_utils
import pickle

X = 600
Y = 480
R = 15
CO = 0.2


class GAME:
    def __init__(self, s, online, home, name, op):
        self.mainwindow = Tk()
        self.online = online
        self.ai_speed = 2
        self.ai_iq = 0.5
        if self.online:
            self.op = op
        else:
            self.op = 'Computer'
        self.name = name
        self.mainwindow.title('Game: ' + self.name)
        self.me = s
        self.win = 0
        self.lose = 0
        self.ai = True
        self.CV = Canvas(self.mainwindow, width=X, height=Y)
        self.CV.create_line(R, R, X - R, R)
        self.CV.create_line(X - R, R, X - R, Y - R)
        self.CV.create_line(R, R, R, Y - R)
        self.CV.create_line(R, Y - R, X - R, Y - R)
        self.home = home
        if self.home:
            self.cx = [X / 4, X * 3 / 4]
        else:
            self.cx = [X * 3 / 4, X / 4]
        self.cy = [Y / 2, Y / 2]
        self.xg = [0, 0]
        self.yg = [0, 0]
        self.ball0 = self.CV.create_oval((self.cx[0] - R, self.cy[0] - R, self.cx[0] + R, self.cy[0] + R), fill='black')
        self.ball1 = self.CV.create_oval((self.cx[1] - R, self.cy[1] - R, self.cx[1] + R, self.cy[1] + R), fill='white')
        self.mainwindow.bind('<KeyPress>', self.move)
        self.frame0 = Frame(self.mainwindow)
        self.frame1 = Frame(self.mainwindow)
        self.frame2 = Frame(self.mainwindow)
        self.frame_bottom = Frame(self.mainwindow)
        self.frame_top = Frame(self.mainwindow)
        self.frame_blank0 = Frame(self.mainwindow)
        self.frame_blank1 = Frame(self.mainwindow)
        self.label_b = Label(self.frame_bottom, text='   ')
        self.label_t = Label(self.frame_top, text='   ')
        self.label_blank0 = Label(self.frame_blank0, text='   ')
        self.label_blank1 = Label(self.frame_blank1, text='   ')
        self.score = StringVar()
        self.score.set("      You    " + str(self.win) + " : " + str(self.lose) + "   Opponent")
        self.label = Label(self.frame0, textvariable=self.score)
        self.difficulty = StringVar()
        self.difficulty.set('Normal')
        self.option = OptionMenu(self.frame1, self.difficulty, 'Easy', 'Normal', 'Hard')
        self.button_ai = Button(self.frame2, text=" AI start ", command=self.start_ai)
        self.button_quit = Button(self.frame2, text='   Quit   ', command=self.quit)
        self.label.pack()
        self.label_blank0.pack()
        self.label_blank1.pack()
        self.button_ai.pack(side='left')
        self.button_quit.pack()
        self.frame_top.pack()
        self.frame0.pack()
        self.CV.pack()
        self.frame_blank0.pack()
        self.option.pack()
        self.label_b.pack()
        self.label_t.pack()
        self.frame1.pack()
        self.frame_blank1.pack()
        self.frame2.pack()
        self.frame_bottom.pack()
        self.physics()
        if self.online:
            self.exchange()

    def start(self):
        self.mainwindow.mainloop()

    def move(self, event):
        if event.char.lower() == 's':
            self.yg[0] += 2
        if event.char.lower() == 'k':
            self.yg[1] += 2
        if event.char.lower() == 'a':
            self.xg[0] -= 2
        if event.char.lower() == 'j':
            self.xg[1] -= 2
        if event.char.lower() == 'w':
            self.yg[0] -= 2
        if event.char.lower() == 'i':
            self.yg[1] -= 2
        if event.char.lower() == 'd':
            self.xg[0] += 2
        if event.char.lower() == 'l':
            self.xg[1] += 2

    def save(self):
        try:
            infile = open(self.name + '.dat', 'rb')
            dic = pickle.load(infile)
            infile.close()
        except IOError:
            dic = {}
        if self.op in dic.keys():
            dic[self.op].append((self.win, self.lose))
        else:
            dic[self.op] = [(self.win, self.lose)]
        infile = open(self.name + '.dat', 'wb')
        pickle.dump(dic, infile)
        infile.close()

    def quit(self):
        self.save()
        if self.online:
            chat_utils.mysend(self.me, chat_utils.M_QGAME)
        self.mainwindow.destroy()

    def distance(self):
        return math.sqrt((self.cx[0] - self.cx[1]) ** 2 + (self.cy[0] - self.cy[1]) ** 2)

    def start_ai(self):
        self.initial_ai()
        self.match_up()

    def initial_ai(self):
        if self.difficulty.get() == 'Easy':
            self.ai_speed = 1.5
            self.ai_iq = 0.5
        elif self.difficulty.get() == 'Normal':
            self.ai_speed = 2
            self.ai_iq = 3
        elif self.difficulty.get() == 'Hard':
            self.ai_speed = 2.5
            self.ai_iq = 7

    def match_up(self):
        x = self.cx[0] - self.cx[1]
        y = self.cy[0] - self.cy[1]
        t = math.sqrt(x ** 2 + y ** 2)
        self.xg[1] += self.ai_speed * x / t
        self.yg[1] += self.ai_speed * y / t
        if self.cx[1] < X * CO:
            self.xg[1] += self.ai_iq
        if self.cx[1] + R > X * (1 - CO):
            self.xg[1] -= self.ai_iq
        if self.cy[1] - R < Y * CO:
            self.yg[1] += self.ai_iq
        if self.cy[1] + R > Y * (1 - CO):
            self.yg[1] -= self.ai_iq
        if self.ai:
            self.mainwindow.after(200, self.match_up)
        else:
            self.xg[1] = 0
            self.yg[1] = 0

    def hit(self):
        if self.distance() <= 2 * R:
            tmp0 = math.sqrt(self.xg[0] ** 2 + self.yg[0] ** 2)
            tmp1 = math.sqrt(self.xg[1] ** 2 + self.yg[1] ** 2)
            x = self.cx[0] - self.cx[1]
            y = self.cy[0] - self.cy[1]
            tmp = math.sqrt(x ** 2 + y ** 2)
            self.xg[0] = x / tmp * tmp1
            self.yg[0] = y / tmp * tmp1
            self.xg[1] = -x / tmp * tmp0
            self.yg[1] = -y / tmp * tmp0

    def exchange(self):
        chat_utils.mysend(self.me, chat_utils.M_INGAME +
                          str(self.cx[0]) + ' ' + str(self.cy[0]) + ' ' +
                          str(self.xg[0]) + ' ' + str(self.yg[0]))
        move = chat_utils.myrecv(self.me)
        if len(move) > 0:
            if move[0] == chat_utils.M_INGAME:
                op = move[1:].split()
                for i in range(4):
                    op[i] = float(op[i])
                self.cx[1] = op[0]
                self.cy[1] = op[1]
                self.xg[1] = op[2]
                self.yg[1] = op[3]
                self.CV.after(50, self.exchange)
            elif move[0] == chat_utils.M_QGAME:
                self.save()
                self.online = False
                self.mainwindow.destroy()

    def physics(self):
        self.hit()
        for i in range(2):
            if self.xg[i] > 0:
                self.xg[i] = max(self.xg[i] - 0.05, 0)
            if self.xg[i] < 0:
                self.xg[i] = min(self.xg[i] + 0.05, 0)
            if self.yg[i] > 0:
                self.yg[i] = max(self.yg[i] - 0.05, 0)
            if self.yg[i] < 0:
                self.yg[i] = min(self.yg[i] + 0.05, 0)
            if (self.cx[i] + self.xg[i] >= R) and \
                    (self.cx[i] + self.xg[i] <= X - R) and \
                    (self.cy[i] + self.yg[i] >= R) and \
                    (self.cy[i] + self.yg[i] <= Y - R):
                self.cx[i] += self.xg[i]
                self.cy[i] += self.yg[i]
            else:
                if i == 0:
                    self.lose += 1
                else:
                    self.win += 1
                self.ai = False
                self.cx[i] += self.xg[i]
                self.cy[i] += self.yg[i]
                self.CV.coords(self.ball0, (self.cx[0] - R, self.cy[0] - R, self.cx[0] + R, self.cy[0] + R))
                self.CV.coords(self.ball1, (self.cx[1] - R, self.cy[1] - R, self.cx[1] + R, self.cy[1] + R))
                if self.home:
                    self.cx = [X / 4, X * 3 / 4]
                else:
                    self.cx = [X * 3 / 4, X / 4]
                self.cy = [Y / 2, Y / 2]
                self.xg = [0, 0]
                self.yg = [0, 0]
                if i == 0:
                    self.score.set("      You    " + str(self.win) + " : " + str(self.lose) + "   Opponent")
                    tkinter.messagebox.showinfo("Information",
                                                "You are out!")
                else:
                    self.score.set("      You    " + str(self.win) + " : " + str(self.lose) + "   Opponent")
                    tkinter.messagebox.showinfo("Information",
                                                "You win!")
                self.ai = True
        self.CV.coords(self.ball0, (self.cx[0] - R, self.cy[0] - R, self.cx[0] + R, self.cy[0] + R))
        self.CV.coords(self.ball1, (self.cx[1] - R, self.cy[1] - R, self.cx[1] + R, self.cy[1] + R))
        self.mainwindow.after(5, self.physics)


if __name__ == '__main__':
    MyGUI = GAME('s', False, True, 'lin', '')
    MyGUI.start()
