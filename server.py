import sys
import socket
import select
import time

# Define global variables
HOST = 'localhost'
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9998
USERS = {}


class Server:
    def __init__(self):
        self.server_stop = False  # Variable to stop server

    def chat_server(self):
        # Start server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(10)

        # add server socket object to the list of readable connections
        SOCKET_LIST.append(server_socket)

        print "Chat server started on port " + str(PORT)

        # Main loop
        while not self.server_stop:
            # Sleep for .1ms to reduce CPU usage (ugly, but it works)
            time.sleep(0.0001)

            # Get ready to read/write
            (ready_to_read,
             ready_to_write,
             in_error) = select.select(SOCKET_LIST, [], [], 0)

            for sock in ready_to_read:
                # A new connection request recieved
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    SOCKET_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr

                    # Assign guest nick as default nick
                    temp_name = 'Guest' + str(len(SOCKET_LIST))
                    USERS[sockfd] = temp_name

                    # Update nick list
                    nicklist = ' '.join(USERS.values())

                    # Send client list of users upon joining
                    sockfd.send("USERS|%s" % nicklist)

                    # Notify clients of new connection
                    self.broadcast(server_socket,
                                   sockfd,
                                   "MSG|[%s] entered the chat\n"
                                   % USERS[sockfd])
                # A message from a client, not a new connection
                else:
                    # Process data recieved from client,
                    try:
                        # Receiving data from the socket.
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            # Handle recieved data
                            self.handle_data(data, server_socket, sock)
                        else:
                            # Remove the socket that's broken
                            if sock in SOCKET_LIST:
                                SOCKET_LIST.remove(sock)
                                del USERS[sock]

                            # Connection has been broken
                            self.broadcast(server_socket,
                                           sock,
                                           "MSG|Client (%s, %s) is offline\n" %
                                           addr)

                    # Exception
                    except:
                        # Client has diconnected
                        self.broadcast(server_socket,
                                       sock,
                                       "MSG|Client (%s, %s) is offline\n" %
                                       addr)
                        continue

        server_socket.close()

    # Handle data from read socket
    def handle_data(self, data, server_socket, sock):
        # Split using | delimiter
        msg_type = data.split('|')[0]
        msg = data[data.find('|') + 1:]

        # Nick change request found
        if 'NICK' == msg_type:
            new_nick = msg
            print msg
            # Nick taken
            if msg in USERS.values():
                sock.send("NICK|" % USERS[sock])
            else:
                # Nick not already in use; change user's nick
                former_nick = USERS[sock]
                USERS[sock] = msg
                # Notify clients of nick change
                self.broadcast(server_socket, sock,
                               "MSG|%s is now known as %s" %
                               (former_nick, USERS[sock]))

        # User list update requested
        elif 'USERS' == msg_type:
            nicklist = ' '.join(USERS.values())
            print nicklist
            # Send nick list
            sock.send("USERS|%s" % nicklist)

        # Normal message recieved
        elif 'MSG' == msg_type:
            # Send message to clients
            self.broadcast(server_socket, sock,
                           "MSG|[%s] %s" % (USERS[sock], msg))

    # Broadcast chat messages to all connected clients
    def broadcast(self, server_socket, sock, message):
        for socket in SOCKET_LIST:
            # Send the message only to peers
            if socket != server_socket and socket != sock:
                try:
                    socket.send(message)
                except:
                    # Broken socket connection; remove it
                    socket.close()
                    if socket in SOCKET_LIST:
                        SOCKET_LIST.remove(socket)
                        del USERS[socket]

if __name__ == "__main__":
    # Run server
    server = Server()
    server.chat_server()
