import utils
import sys
import socket
import select

def pad_message(message):
  while len(message) < utils.MESSAGE_LENGTH:
    message += " "
  return message[:utils.MESSAGE_LENGTH]

class ChatClient:
    def __init__(self, name, server_address, server_port):
        self.name = name
        self.server_address = server_address
        self.server_port = server_port
        self.clientSocket = socket.socket()
        try:
            self.clientSocket.connect((server_address, server_port))
        except:
            print(utils.CLIENT_CANNOT_CONNECT.format(server_address, server_port))
            exit(1)

    def run(self):
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()
        while True:
            socket_list = [sys.stdin, self.clientSocket]
            ready_to_read, ready_to_write, in_error = select.select(socket_list , [], [])
            for sock in ready_to_read:
                #Incomming message
                if sock == self.clientSocket:
                    message = sock.recv(200)
                    tmp = message
                    while tmp:
                        if len(tmp) >= 200:
                            break
                        tmp = sock.recv(200)
                        message = message + tmp
                    if message:
                        message = message.strip()
                        if message:
                            sys.stdout.write(utils.CLIENT_WIPE_ME + message + '\n')
                            sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                            sys.stdout.flush()
                    else:
                        print(utils.CLIENT_WIPE_ME + utils.CLIENT_SERVER_DISCONNECTED.format(self.server_address, self.server_port))
                        exit(1)
                else:
                    msg = sys.stdin.readline()
                    self.clientSocket.send(pad_message(self.name + ' ' + msg))
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python client.py YourName HostAddress ServerPort')
        exit(1)

    chat_client = ChatClient(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    exit(chat_client.run())
