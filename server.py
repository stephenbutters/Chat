import utils
import sys
import socket
import select

def pad_message(message):
  while len(message) < utils.MESSAGE_LENGTH:
    message += " "
  return message[:utils.MESSAGE_LENGTH]

class ChatServer:
    def __init__(self, server_port):
        self.serverSocket = socket.socket()
        self.serverSocket.bind(('', server_port))
        self.SocketList = [self.serverSocket]
        self.Channels = {}
        self.socket_and_name = {}
        self.serverSocket.listen(5)

    def run(self):
        while True:
            ready_to_read, ready_to_write, in_error = select.select(self.SocketList, [], [], 0)
            for sock in ready_to_read:
                #New connection request
                if sock == self.serverSocket:
                    newConnectionSocket, newConnectionAddress = self.serverSocket.accept()
                    self.SocketList.append(newConnectionSocket)
                #Message from clients
                else:
                    message = sock.recv(200)
                    tmp = message
                    while tmp:
                        if len(tmp) >= 200:
                            break
                        tmp = sock.recv(200)
                        message = message + tmp
                    if message:
                        print(message)
                        self.process(sock, message)
                    else:
                        if sock in self.SocketList:
                            self.SocketList.remove(sock)
                        for channel in self.Channels:
                            if sock in self.Channels[channel]:
                                self.broadcast(sock, channel, utils.SERVER_CLIENT_LEFT_CHANNEL.format(self.socket_and_name[sock]))
                                self.Channels[channel].remove(sock)


    def process(self, sock, message):
        print('xxxxxxxxxxxxxx')
        client_name = message.strip().split()[0]
        self.socket_and_name[sock] = client_name
        message = message[len(client_name)+1:]
        #Control message
        if message[0] == '/':
            control_message = message.strip().split()
            if control_message[0] == '/list':
                self.notify(sock, ''.join(self.Channels.keys()))
            elif control_message[0] == '/create':
                if len(control_message) != 2:
                    self.notify(sock, utils.SERVER_CREATE_REQUIRES_ARGUMENT)
                    return
                channel_name = control_message[1]
                if channel_name not in self.Channels.keys():
                    self.Channels[channel_name] = []
                    self.join_channel(sock, channel_name, client_name)
                else:
                    self.notify(sock, utils.SERVER_CHANNEL_EXISTS.format(channel_name))
                    return
            elif control_message[0] == '/join':
                if len(control_message) != 2:
                    self.notify(sock, utils.SERVER_JOIN_REQUIRES_ARGUMENT)
                    return
                channel_name = control_message[1]
                if channel_name in self.Channels.keys():
                    self.join_channel(sock, channel_name, client_name)
                else:
                    self.notify(sock, utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name))
                    return
            else:
                self.notify(sock, utils.SERVER_INVALID_CONTROL_MESSAGE.format(control_message[0]))
                return
        #Normal message
        else:
            Not_In_Channel = True
            for channel in self.Channels:
                if sock in self.Channels[channel]:
                    Not_In_Channel = False
                    self.broadcast(sock, channel, '['+client_name+'] '+message)
                    break
            if Not_In_Channel:
                self.notify(sock, utils.SERVER_CLIENT_NOT_IN_CHANNEL)

    def notify(self, sock, notification):
        try:
            sock.send(pad_message(notification))
        except:
            sock.close()
            if sock in self.SocketList:
                self.SocketList.remove(sock)

    def broadcast(self, sock, channel_name, message):
        for socket in self.Channels[channel_name]:
            if socket != sock:
                try:
                    socket.send(pad_message(message))
                except:
                    if socket in self.SocketList:
                        self.SocketList.remove(socket)
                        for channel in self.Channels:
                            if sock in self.Channels[channel]:
                                self.Channels[channel].remove(socket)

    def join_channel(self, sock, channel_name, client_name):
        for channel in self.Channels:
            if channel != channel_name and sock in self.Channels[channel]:
                self.broadcast(sock, channel, utils.SERVER_CLIENT_LEFT_CHANNEL.format(client_name))
                self.Channels[channel].remove(sock)
        if sock not in self.Channels[channel_name]:
            if self.Channels[channel_name]:
                self.broadcast(sock, channel_name, utils.SERVER_CLIENT_JOINED_CHANNEL.format(client_name))
            self.Channels[channel_name].append(sock)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py ServerPort")
        exit(1)

    chat_server = ChatServer(int(sys.argv[1]))
    exit(chat_server.run())
