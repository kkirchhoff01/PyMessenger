import curses
import sys
import traceback

class Window:
    def __init__(self, maxy, maxx):
        self.top = curses.newwin(3*maxy/4-2, maxx-11, 0, 0);
        self.bottom = curses.newwin(3*maxy/4, maxx, 3*maxy/4, 0);
        self.nick_panel = curses.newwin(3*maxy/4-2, 11, 0, maxx-11)
        self.refresh_bottom()
        self.top.nodelay(1)
        self.bottom.nodelay(1)
        self.top.scrollok(1)
        self.bottom.scrollok(1)

    def get_ch(self):
        return self.bottom.getch()

    def escape(self, message):
        self.bottom.clear()
        self.bottom.addstr("Are you sure you want to quit? [y/n] ")
        self.bottom.refresh()
        self.bottom.nodelay(0)
        answer = self.bottom.getch()
        if answer == ord('y') or answer == ord('Y'):
            sys.exit()
        else:
            self.bottom.nodelay(1)
            self.refresh_bottom()
            self.bottom.addstr(message)
            self.bottom.refresh()

    def enter(self, message):
        if '/nick' not in message and '/users' not in message:
            self.top.addstr('[Me] ' + message +'\n')
        self.top.refresh()
        self.refresh_bottom()

    def add_str(self, data):
        self.top.addstr(data+'\n')
        self.top.refresh()
        self.bottom.refresh()

    def add_ch(self, ch):
        self.bottom.addch(ch)
        self.bottom.refresh()

    #Backspace function
    def backspace(self):#currwin):
        curses.noecho()
        curses.nocbreak()
        r,c = self.bottom.getyx()
        maxy, maxx = self.bottom.getmaxyx()
        if c < 2 and r == 0:
            pass
        elif c == 0 and r > 0:
            self.bottom.move(r-1, maxx-1)
            self.bottom.delch()
        else:
            self.bottom.move(r,c-1)
            self.bottom.delch()
            
        curses.cbreak()
        self.bottom.refresh()
    
    def refresh_bottom(self):
        self.bottom.clear()
        self.bottom.addch(62)
        self.bottom.refresh()

    def update_nickpanel(self, nicks):
        nicklist = nicks.split(' ')
        self.nick_panel.clear()
        for n in nicklist:
            self.nick_panel.addstr(n+'\n')
        self.nick_panel.refresh()
        self.bottom.refresh()

    def print_connected(self):
        self.top.addstr("You are now connected to the server.\n")
        self.top.refresh()
        self.bottom.refresh()
