import sys
import socket
import select
import curses
import traceback

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
			while len(self.name) > 10 or len(self.name) == 0 or not self.name.isalnum():
				self.stdscr.addstr("Invalid name. Try again: ")
				self.name = self.stdscr.getstr()
				self.stdscr.clear()
				self.stdscr.refresh()
			curses.noecho()

			#Initialize chat windows
			maxy,maxx = self.stdscr.getmaxyx()
			self.top = curses.newwin(3*maxy/4-2, maxx-11, 0, 0);
			self.bottom = curses.newwin(3*maxy/4, maxx, 3*maxy/4, 0);
			self.nick_panel = curses.newwin(3*maxy/4-2, 11, 0, maxx-11)
			self.refresh_bottom()
			self.top.nodelay(1)
			self.bottom.nodelay(1)
			self.top.scrollok(1)
			self.bottom.scrollok(1)
		except:
			self.end_session()
			sys.exit()

	def chat_client(self):
		host = 'localhost'
		port = 9999
		 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		 
		#Connect to remote host
		try:
			s.connect((host, port))
			s.send('/nick ' + self.name)
		except:
			print 'Unable to connect'
			sys.exit()
		self.top.addstr("You are now connected to the server.\n")
		self.top.refresh()
		self.bottom.refresh()
		 
		send_message = ''
		message = '' 
		#keys = 0
		while 1:
			socket_list = [sys.stdin, s]
			read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
			#Get the list sockets which are readable
			ch = self.bottom.getch()
			if ch != curses.ERR:
				#Exit on escape
				if ch == 27:
					self.bottom.clear()
					self.bottom.addstr("Are you sure you want to quit? [y/n] ")
					self.bottom.refresh()
					self.bottom.nodelay(0)
					answer = chr(self.bottom.getch()).lower
					if answer == 'y':
						self.end_session()
						sys.exit()
						break
					else:
						self.bottom.nodelay(1)
						self.refresh_bottom()
						self.bottom.addstr(message)
						self.bottom.refresh()
				#Backspace
				elif ch == 8 or ch == 127:#curses.KEY_BACKSPACE:
					#bottom.refresh()
					self.backspace()
					if len(message) > 0:
						message = message[:len(message)-1]
				#Displays message on return
				elif ch == 10:
					if '/nick' not in message and '/users' not in message:
						self.top.addstr('[Me] ' + message+'\n')
					send_message = message
					self.top.refresh()
					self.refresh_bottom()
					message = ''
					#pass
				elif ch == curses.KEY_RESIZE or ch == 410:
					#if curses.is_term_resized(maxy,maxx):
					y,x = self.stdscr.getmaxyx()
					self.stdscr.clear()
					curses.resizeterm(y,x)
					self.stdscr.refresh()
					self.top.resize(3*y/4-2, x);
					self.bottom.resize(3*y/4, x);
					self.bottom.refresh()
					self.top.refresh()
				#Writes message
				elif ch < 256:
					message += chr(ch)
					self.bottom.addch(ch)
					self.bottom.refresh()
			
			#Recieve message 
			for sock in read_sockets:            
				if sock == s:
					data = sock.recv(4096)
					if not data:
						self.end_session()
						print '\nDisconnected from chat server'
						sys.exit()
					else :
						nicklist = data.split('|')
						if nicklist[0] == 'USERS' and len(nicklist) > 1:
							nicklist = nicklist[1].split(',')
							self.nick_panel.clear()
							for n in nicklist:
								self.nick_panel.addstr(n+'\n')
							self.nick_panel.refresh()
						else:
							self.top.addstr(data+'\n')
						self.top.refresh()
						self.bottom.refresh()
				else :
					# user entered a message
					if ch == 10 and len(send_message) > 0:
						s.send(send_message)
						send_message = ''

	#Backspace function
	def backspace(self):#currwin):
		curses.noecho()
		curses.nocbreak()
		r,c = self.bottom.getyx()
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
	except KeyboardInterrupt:
		sys.exit(client.end_session())
	except:
		client.end_session()
		traceback.print_exc()
		sys.exit(1)
