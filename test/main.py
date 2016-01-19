from client import Client
from server import Server
import threading
import sys

class Worker(threading.Thread):
    def __init__(self, server_holder):
        threading.Thread.__init__(self)
        self.server = server_holder
        
    def run(self):
        self.server.chat_server()

if __name__ == "__main__":
    fh = open('server_output.log', 'w')
    sys.stdout = fh
    server = Server()
    worker = Worker(server)
    worker.start()
    client = Client()

    try:
        client.chat_client()
    except(KeyboardInterrupt, SystemExit):
        server.server_stop = True
        fh.close()
        sys.exit(client.end_session())
    except:
        server.server_stop = True
        fh.close()
        client.end_session()
        traceback.print_exc()
        sys.exit(1)
