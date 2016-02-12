#!/usr/bin/python
from client import Client
from server import Server
import threading
import sys

# Threading class to run server/client
class Worker(threading.Thread):
    def __init__(self, server_holder):
        threading.Thread.__init__(self)
        self.server = server_holder
        
    def run(self):
        self.server.chat_server()

if __name__ == "__main__":
    fh = open('server_output.log', 'w')
    # Set output to file to prevent writing to screen
    sys.stdout = fh

    # Init server
    server = Server()
    # Thread server
    worker = Worker(server)
    worker.start()

    # Init client
    client = Client()

    try:
        client.chat_client()  # Run main client process
    except(KeyboardInterrupt, SystemExit):
        # Stop server/client on normal exit
        server.server_stop = True
        fh.close()
        sys.exit(client.end_session())
    except:
        # Stop server/client on unexpected exit
        server.server_stop = True
        fh.close()
        client.end_session()
        traceback.print_exc()
        sys.exit(1)
