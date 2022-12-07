import socket


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """
    file_content = bytearray()

    while True:
        packet = active_socket.recv(buffer_size)
        if packet[-10:] == eof_token:
            file_content += packet[:-10]
            break
        file_content += packet
    return file_content


def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """
    global eof_token
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print('Connected to server at IP:', host, 'and Port:', port)
    eof_token = client_socket.recv(1024)
    print('Handshake Done. EOF token sent by the server is:', eof_token.decode())

    cwd_getinfo = receive_message_ending_with_token(
        client_socket, 1024, eof_token)
    print(cwd_getinfo.decode())
    return client_socket


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg+(eof_token.decode())).encode())
    cwd_getinfo = receive_message_ending_with_token(
        client_socket, 1024, eof_token)
    print(cwd_getinfo.decode())


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg+(eof_token.decode())).encode())
    cwd_getinfo = receive_message_ending_with_token(
        client_socket, 1024, eof_token)
    print(cwd_getinfo.decode())


def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    client_socket.sendall((command_and_arg+(eof_token.decode())).encode())
    cwd_getinfo = receive_message_ending_with_token(
        client_socket, 1024, eof_token)
    print(cwd_getinfo.decode())


def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    try:
        client_socket.sendall((command_and_arg+(eof_token.decode())).encode())
        file_name = command_and_arg.split(' ')[1]
        with open(file_name, 'rb') as f:
            file_content = f.read()

            # EOF token
        file_content_with_token = file_content + eof_token
        client_socket.sendall(file_content_with_token)
    except:
        print("File not present")
        client_socket.sendall(b'File not present' + eof_token)
    else:
        cwd_getinfo = receive_message_ending_with_token(
            client_socket, 1024, eof_token)
        print(cwd_getinfo.decode())


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """

    client_socket.sendall((command_and_arg+(eof_token.decode())).encode())

    file_content = receive_message_ending_with_token(
        client_socket, 1024, eof_token)

    if (file_content != b"File doesn't exist"):
        with open(command_and_arg.split(' ')[1], 'wb') as f:
            f.write(file_content)
        print("file downloaded successfully")
    else:
        print("File doesn't exist")
    cwd_getinfo = receive_message_ending_with_token(
        client_socket, 1024, eof_token)
    print(cwd_getinfo.decode())


def main():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    #raise NotImplementedError('Your implementation here.')

    # initialize
    server_socket = initialize("127.0.0.1", 65432)

    while True:
        # get user input

        cmd = input("Enter the command you want to execute:")
        if (cmd.startswith("cd")):
            issue_cd(cmd, server_socket, eof_token)
        elif (cmd.startswith("mkdir")):
            issue_mkdir(cmd, server_socket, eof_token)
        elif (cmd.startswith("rm")):
            issue_rm(cmd, server_socket, eof_token)
        elif (cmd.startswith("ul")):
            issue_ul(cmd, server_socket, eof_token)
        elif (cmd.startswith("dl")):
            issue_dl(cmd, server_socket, eof_token)
        elif (cmd.startswith("exit")):
            server_socket.sendall((cmd).encode()+eof_token)
            print('Exiting the application.')
            server_socket.close()
            break
        else:
            print("Invalid Command")


if __name__ == '__main__':
    main()
