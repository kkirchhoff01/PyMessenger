import sys
import socket
import select
import curses
import traceback
from window import Window


class Client:
    def __init__(self):
        try:
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            #stdscr.keypad(1)
            self.stdscr.addstr("Enter a username: ")
            self.stdscr.move(0, 18)
            curses.echo()
            self.name = self.stdscr.getstr()
            self.stdscr.clear()
            self.stdscr.refresh()
            while(len(self.name) > 10 or len(self.name) == 0 or
                    not self.name.isalnum()):
                self.stdscr.addstr("Invalid name. Try again: ")
                self.name = self.stdscr.getstr()
                self.stdscr.clear()
                self.stdscr.refresh()
            curses.noecho()

            #Initialize chat windows
            maxy, maxx = self.stdscr.getmaxyx()
            self.chat_window = Window(maxy, maxx)
        except Exception, exc:
            self.end_session()
            print exc
            sys.exit()

    def format_message(self, msg_type, msg):
        message = ''
        buff = '{'
        if msg_type == 'USERS':
            message = msg_type + '|' + buff
        elif msg_type == 'NICK':
            if len(msg.split(' ')) > 1:
                message = msg_type + '|' + msg.split(' ')[1]
        elif msg_type == 'MSG':
            message = msg_type + '|' + msg
        return message

    def parse_message(self, message):
        msg_type = message.split('|')[0]
        msg = message[message.find('|') + 1: ]
        if msg_type == 'USERS':
            self.chat_window.update_nickpanel(msg)
        elif msg_type == 'NICK':
            if msg == self.name:
                self.chat_window.add_str('Name taken')
            else:
                self.name = msg
                self.chat_window.add_str('Name changed')
        elif msg_type == 'MSG':
            self.chat_window.add_str(msg)


    def chat_client(self):
        host = 'localhost'
        port = 9998
         
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
         
        #Connect to remote host
        try:
            s.connect((host, port))
            s.send('NICK|' + self.name)
        except:
            print 'Unable to connect'
            sys.exit()

        self.chat_window.print_connected()
         
        send_message = ''
        message = '' 
        #keys = 0
        while 1:
            socket_list = [sys.stdin, s]
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
            #Get the list sockets which are readable
            ch = self.chat_window.get_ch()
            if ch != curses.ERR:
                #Exit on escape
                if ch == 27:
                    self.chat_window.escape(message)
                #Backspace
                elif ch == 8 or ch == 127:#curses.KEY_BACKSPACE:
                    #bottom.refresh()
                    self.chat_window.backspace()
                    if len(message) > 0:
                        message = message[:len(message)-1]
                #Displays message on return
                elif ch == 10:
                    self.chat_window.enter(message)
                    send_message = message
                    message = ''
                    #pass

                #Writes message
                elif ch < 256:
                    message += chr(ch)
                    self.chat_window.add_ch(ch)
            
            #Recieve message 
            for sock in read_sockets:            
                if sock == s:
                    data = sock.recv(4096)
                    if not data:
                        self.end_session()
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else:
                        self.parse_message(data)
                else :
                    # user entered a message
                    if ch == 10 and len(send_message) > 0:
                        if '/nick' == send_message.split(' ')[0]:
                            s.send(self.format_message('NICK', send_message))
                        if '/users' == send_message.split(' ')[0]:
                            s.send(self.format_message('USERS', send_message))
                        else:
                            s.send(self.format_message('MSG', send_message))
                            # self.chat_window.enter(send_message)
                        # s.send(send_message)
                        send_message = ''


    #Function to exit session properly
    def end_session(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


if __name__ == "__main__":
    client = Client()
    try:
        client.chat_client()
    except KeyboardInterrupt, SystemExit:
        sys.exit(client.end_session())
    except:
        client.end_session()
        traceback.print_exc()
        sys.exit(1)
