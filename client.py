import sys
#import locale
import socket
import select
import curses
import traceback

try:
	stdscr = curses.initscr()
	curses.noecho()
	curses.cbreak()
	#stdscr.keypad(1)
	stdscr.addstr("Enter a username: ")
	stdscr.move(0, 18)
	curses.echo()
	name = stdscr.getstr()
	stdscr.clear()
	stdscr.refresh()
	while len(name) > 10 or len(name) == 0 or not name.isalnum():
		stdscr.addstr("Invalid name. Try again: ")
		name = stdscr.getstr()
		stdscr.clear()
		stdscr.refresh()
	curses.noecho()

	#Initialize chat windows
	maxy,maxx = stdscr.getmaxyx()
	top = curses.newwin(3*maxy/4-2, maxx, 0, 0);
	bottom = curses.newwin(3*maxy/4, maxx, 3*maxy/4, 0);
	bottom.addch('>')
	bottom.refresh()
	top.nodelay(1)
	bottom.nodelay(1)
	top.scrollok(1)
	bottom.scrollok(1)
except:
	end_session()

def chat_client():
	host = 'localhost'
	port = 9999
	 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	 
	#Connect to remote host
	try :
		s.connect((host, port))
	except :
		print 'Unable to connect'
		sys.exit()
	top.addstr("You are now connected to the server.\n")
	top.refresh()
	bottom.refresh()
	 
	send_message = ''
	message = '' 
	while 1:
		socket_list = [sys.stdin, s]
		#Get the list sockets which are readable
		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
		ch = bottom.getch()
		if ch != curses.ERR:
			#Exit on escape
			if ch == 27:
				bottom.clear()
				bottom.addstr("Are you sure you want to quit? [y/n] ")
				bottom.refresh()
				bottom.nodelay(0)
				answer = chr(bottom.getch()).lower()
				if answer == 'y':
					end_session()
					break
				else:
					bottom.nodelay(1)
					bottom.clear()
					bottom.addch(62)
					bottom.addstr(message)
					bottom.refresh()
			#Backspace
			elif ch == 8 or ch == 127:#curses.KEY_BACKSPACE:
				#bottom.refresh()
				backspace()
				if len(message) > 0:
					message = message[:len(message)-1]
			#Displays message on return
			elif ch == 10:
				top.addstr('[' + name + '] ' + message+'\n')
				send_message = message
				bottom.clear()
				bottom.addch(62)
				top.refresh()
				bottom.refresh()
				message = ''
				#pass
			elif ch == curses.KEY_RESIZE or ch == 410:
				#if curses.is_term_resized(maxy,maxx):
				y,x = stdscr.getmaxyx()
				stdscr.clear()
				curses.resizeterm(y,x)
				stdscr.refresh()
				top.resize(3*y/4-2, x);
				bottom.resize(3*y/4, x);
				bottom.refresh()
				top.refresh()
				sys.stdin.reset()
			#Writes message
			elif ch < 256:
				message += chr(ch)
				bottom.addch(ch)
				bottom.refresh()
		
		#Recieve message 
		for sock in read_sockets:            
			if sock == s:
				data = sock.recv(4096)
				if not data :
					end_session()
					print '\nDisconnected from chat server'
					sys.exit()
				else :
					top.addstr(data+'\n')
					top.refresh()
					bottom.refresh()
			
			else :
				# user entered a message
				if ch == 10 and len(send_message) > 0:
					s.send('[' + name + '] ' + send_message)
					send_message = ''

#Backspace function
def backspace():#currwin):
	curses.noecho()
	curses.nocbreak()
	r,c = bottom.getyx()
	if c < 2 and r == 0:
		pass
	elif c == 0 and r > 0:
		bottom.move(r-1, maxx-1)
		bottom.delch()
	else:
		bottom.move(r,c-1)
		bottom.delch()
		
	curses.cbreak()
	bottom.refresh()

#Function to exit session properly
def end_session():
	stdscr.keypad(0)
	curses.echo()
	curses.nocbreak()
	curses.endwin()

if __name__ == "__main__":
	try:
		chat_client()
	except KeyboardInterrupt:
		sys.exit(end_session())
	except:
		end_session()
		traceback.print_exc()
		sys.exit(1)
