import sys
import socket
import select
import time

HOST = 'localhost' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9998
USERS = {}

class Server:
    def __init__(self):
        self._server_stop = False
    
    @property
    def server_stop(self):
        return self._server_stop

    def chat_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)

        # add server socket object to the list of readable connections
        SOCKET_LIST.append(server_socket)
     
        print "Chat server started on port " + str(PORT)
     
        while not self.server_stop:
            #sleep for .1ms to reduce CPU usage (ugly, but it works)
            time.sleep(0.0001)
            
            ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
          
            for sock in ready_to_read:
                # a new connection request recieved
                if sock == server_socket: 
                    sockfd, addr = server_socket.accept()
                    SOCKET_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                    temp_name = 'Guest' + str(len(SOCKET_LIST))
                    USERS[sockfd] = temp_name
                    nicklist = ''
                    for key in USERS.keys():
                        nicklist += USERS[key]+','
                    sockfd.send("USERS|%s" % nicklist.strip(','))
                    self.broadcast(server_socket, sockfd, "[%s] entered the chat\n" % USERS[sockfd])
                # a message from a client, not a new connection
                else:
                    # process data recieved from client, 
                    try:
                        # receiving data from the socket.
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            new_nick = data.split(' ')
                            if '/nick' == new_nick[0] and len(new_nick) > 1:
                                new_nick = new_nick[1]
                                nick_found = False
                                for nicks in USERS.keys():
                                    if USERS[nicks] == new_nick:
                                        sock.send("\r" + new_nick + " is taken.")
                                        nick_found = True
                                if not nick_found:
                                    former_nick = USERS[sock]
                                    USERS[sock] = new_nick
                                    self.broadcast(server_socket, sock, "%s is now known as %s" % (former_nick, USERS[sock]))
                            elif '/users' == new_nick[0]:
                                nicklist = ''
                                for key in USERS.keys():
                                    nicklist += USERS[key]+','
                                sock.send("USERS|%s" % nicklist.strip(','))
                            # there is something in the socket #+ '[' + str(sock.getpeername()) + '] ' +
                            else:
                                self.broadcast(server_socket, sock, "\r" + '[' + USERS[sock] + ']' + data)
                        else:
                            # remove the socket that's broken    
                            if sock in SOCKET_LIST:
                                SOCKET_LIST.remove(sock)
                                del USERS[sock]

                            # at this stage, no data means probably the connection has been broken
                            self.broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

                    # exception 
                    except:
                        self.broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                        continue

        server_socket.close()
        
    # broadcast chat messages to all connected clients
    def broadcast (self,server_socket, sock, message):
        for socket in SOCKET_LIST:
            # send the message only to peer
            if socket != server_socket and socket != sock :
                try :
                    socket.send(message)
                except :
                    # broken socket connection
                    socket.close()
                    # broken socket, remove it
                    if socket in SOCKET_LIST:
                        SOCKET_LIST.remove(socket)
                        del USERS[socket]
 
if __name__ == "__main__":
    server = Server()
    server.chat_server()
