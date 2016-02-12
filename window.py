import curses
import sys
import traceback


class Window:
    # Init window with size
    def __init__(self, maxy, maxx):
        # Init top window to display messages
        self.top = curses.newwin(3*maxy/4-2, maxx-11, 0, 0)
        # Bottom window to display input
        self.bottom = curses.newwin(3*maxy/4, maxx, 3*maxy/4, 0)
        # Sind window to display list of users
        self.nick_panel = curses.newwin(3*maxy/4-2, 11, 0, maxx-11)
        self.refresh_bottom()  # Refresh to update

        # Window settings
        self.top.nodelay(1)
        self.bottom.nodelay(1)
        self.top.scrollok(1)
        self.bottom.scrollok(1)

    # Curses getch()
    def get_ch(self):
        return self.bottom.getch()

    # Escape key pressed (exit requested)
    def escape(self, message):
        # Clear bottom and display message to make sure client wants to exit
        self.bottom.clear()
        self.bottom.addstr("Are you sure you want to quit? [y/n] ")
        self.bottom.refresh()
        self.bottom.nodelay(0)

        # Get client's response
        answer = self.bottom.getch()
        if answer == ord('y') or answer == ord('Y'):
            # Client wants to exit
            sys.exit()
        else:
            # Client does not want to exit; go back to normal input screen
            self.bottom.nodelay(1)
            self.refresh_bottom()
            self.bottom.addstr(message)
            self.bottom.refresh()

    # Return key pressed
    def enter(self, message):
        # Make sure message is not a request from server
        if '/nick' not in message and '/users' not in message:
            # Add message to screen
            self.top.addstr('[Me] ' + message + '\n')
        self.top.refresh()
        self.refresh_bottom()

    # Add string to screen
    def add_str(self, data):
        self.top.addstr(data + '\n')
        self.top.refresh()
        self.bottom.refresh()

    # Add character to input screen
    def add_ch(self, ch):
        self.bottom.addch(ch)
        self.bottom.refresh()

    # Backspace key pressed
    def backspace(self):
        # Curses doesn't handle backspace properly
        # Function writes backspace manually
        curses.noecho()
        curses.nocbreak()
        r, c = self.bottom.getyx()
        maxy, maxx = self.bottom.getmaxyx()

        # Handle backspace when there is no input
        if c < 2 and r == 0:
            pass

        # Backspace on first character of new line
        elif c == 0 and r > 0:
            self.bottom.move(r-1, maxx-1)
            self.bottom.delch()

        # Normal backspace
        else:
            self.bottom.move(r, c-1)
            self.bottom.delch()

        # Return to normal
        curses.cbreak()
        self.bottom.refresh()

    # Simple refresh of bottom screen
    def refresh_bottom(self):
        self.bottom.clear()
        self.bottom.addch(62)  # add '>' to display where input starts
        self.bottom.refresh()

    # Update side panel with list of nicks
    def update_nickpanel(self, nicks):
        # Split nicklist and clear panel
        nicklist = nicks.split(' ')
        self.nick_panel.clear()

        # Add nicks
        for n in nicklist:
            self.nick_panel.addstr(n + '\n')

        self.nick_panel.refresh()
        self.bottom.refresh()

    # Print message to client when it is connected to the server
    def print_connected(self):
        self.top.addstr("You are now connected to the server.\n")
        self.top.refresh()
        self.bottom.refresh()
