import sys
import socket
import select
import curses
import traceback
from window import Window


class Client:
    def __init__(self):
        try:
            # Start curses window
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()

            # Get usernanme
            self.stdscr.addstr("Enter a username: ")
            self.stdscr.move(0, 18)
            curses.echo()
            self.name = self.stdscr.getstr()
            self.stdscr.clear()
            self.stdscr.refresh()

            # If username is invalid, try until valid name is found
            # Name must be alphanumeric and <= 10 characters
            while(len(self.name) > 10 or len(self.name) == 0 or
                    not self.name.isalnum()):
                self.stdscr.addstr("Invalid name. Try again: ")
                self.name = self.stdscr.getstr()
                self.stdscr.clear()
                self.stdscr.refresh()
            curses.noecho()

            # Initialize chat windows
            maxy, maxx = self.stdscr.getmaxyx()
            self.chat_window = Window(maxy, maxx)

        except Exception, exc:
            # Problem with window init; exit
            self.end_session()
            print exc
            sys.exit()

    # Format message
    def format_message(self, msg_type, msg):
        message = ''
        buff = '{'
        # User request
        if msg_type == 'USERS':
            message = msg_type + '|' + buff

        # Nick change request
        elif msg_type == 'NICK':
            if len(msg.split(' ')) > 1:
                message = msg_type + '|' + msg.split(' ')[1]

        # Normal message
        elif msg_type == 'MSG':
            message = msg_type + '|' + msg
        return message

    # Parse recieved message
    def parse_message(self, message):
        # Delimiter is |
        msg_type = message.split('|')[0]
        msg = message[message.find('|') + 1:]

        # User list recieved
        if msg_type == 'USERS':
            self.chat_window.update_nickpanel(msg)

        # Nick change response recieved
        elif msg_type == 'NICK':
            # Name taken if recieved message is same as the old nick
            if msg == self.name:
                self.chat_window.add_str('Name taken')

            # If new nick is recieved, the name has been changed
            else:
                self.name = msg
                self.chat_window.add_str('Name changed')

        # Normal message recieved; add to window
        elif msg_type == 'MSG':
            self.chat_window.add_str(msg)

    # Main process
    def chat_client(self):
        # Socket variables
        host = 'localhost'
        port = 9998

        # Connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)

        # Connect to remote host
        try:
            # Send nick once connected
            s.connect((host, port))
            s.send('NICK|' + self.name)
        except:
            # Failed to connect
            print 'Unable to connect'
            sys.exit()

        # Notify connection
        self.chat_window.print_connected()

        send_message = ''
        message = ''
        # Main loop
        while 1:
            # Socket list for input and server
            socket_list = [sys.stdin, s]

            # Check for read/write sockets
            read_sockets, write_sockets, error_sockets = select.select(
                                                            socket_list,
                                                            [], [])

            # Get/handle input
            ch = self.chat_window.get_ch()
            if ch != curses.ERR:  # Character input found
                # Exit on escape
                if ch == 27:
                    self.chat_window.escape(message)

                # Backspace
                elif ch == 8 or ch == 127:
                    # Handle backspace
                    self.chat_window.backspace()

                    # Remove last character from message
                    if len(message) > 0:
                        message = message[:-1]

                # Displays message on return
                elif ch == 10:
                    self.chat_window.enter(message)
                    # Update message to be sent to server
                    send_message = message
                    message = ''  # Empty current message

                # Writes message
                elif ch < 256:
                    message += chr(ch)  # Add character to message
                    self.chat_window.add_ch(ch)  # Add character to screen

            # Recieve message
            for sock in read_sockets:
                # If read is coming from server
                if sock == s:
                    # Get data from server
                    data = sock.recv(4096)

                    # If data is empty, the client has been disconnected
                    if not data:
                        self.end_session()
                        print '\nDisconnected from chat server'
                        sys.exit()

                    # If data was recieved from socket, parse message
                    else:
                        self.parse_message(data)

                else:
                    # User entered a message
                    if ch == 10 and len(send_message) > 0:
                        # User requested nick change
                        if '/nick' == send_message.split(' ')[0]:
                            s.send(self.format_message('NICK', send_message))

                        # User requested nick list
                        if '/users' == send_message.split(' ')[0]:
                            s.send(self.format_message('USERS', send_message))

                        # User sending normal message
                        else:
                            s.send(self.format_message('MSG', send_message))
                        send_message = ''

    # Function to exit session properly
    def end_session(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


if __name__ == "__main__":
    # Run client
    client = Client()

    try:
        client.chat_client()
    except KeyboardInterrupt, SystemExit:  # Normal exit
        sys.exit(client.end_session())
    except:  # Unexpected exit
        client.end_session()
        traceback.print_exc()
        sys.exit(1)
