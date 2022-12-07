
from genericpath import isfile
import socket
import random
import string
from threading import Thread
import os
import shutil
from pathlib import Path


def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + \
        '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + \
        '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token(length):
    """Helper method to generates a random token that starts with '<' and ends with '>'.
        The total length of the token (including '<' and '>') should be 10.
        Examples: '<1f56xc5d>', '<KfOVnVMV>'
        return: the generated token.
        """
    letters = string.ascii_letters
    digits = string.digits
    random_token = letters+digits
    eof_token = ''.join(random.choice(random_token) for i in range(length))
    eof_token = '<'+eof_token+'>'
    # print("Random string of length", len(eof_token), "is:", eof_token)
    print("Handshake Completed - eof_token is", eof_token)
    return eof_token
    # raise NotImplementedError('Your implementation here.')


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
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


def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """
    try:
        path = os.path.join(current_working_directory, new_working_directory)
        if (new_working_directory == ".."):
            os.chdir(path)
            print(os.getcwd())
            return os.path.abspath(path)

        elif (os.path.isfile(path)):
            print("file name cannot be passed")

        else:
            path = os.getcwd()
            os.chdir(os.path.join(
                current_working_directory, new_working_directory))
            print(os.getcwd())
            return os.path.abspath(os.getcwd())

    except:
        print("Directory not found")
        print("Current Directory", os.path.abspath(os.getcwd()))


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    try:
        path = os.path.join(current_working_directory, directory_name)
        os.makedirs(path)
    except:
        print("Cannot make directory")
        print("Current Directory", os.path.abspath(os.getcwd()))


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    try:
        path = os.path.join(current_working_directory, object_name)
        if (os.path.isfile(path)):
            os.remove(path)
        elif len(os.listdir(path)) == 0:
            os.rmdir(path)
        elif os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
        else:
            print("Directory is not empty")
    except:
        print("Cannot remove directory or file")


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """

    path = os.path.join(current_working_directory, file_name)
    file_content = receive_message_ending_with_token(
        service_socket, 1024, eof_token)

    if file_content != b'File not present':
        with open(path, 'wb') as f:
            f.write(file_content)
            print("file uploaded successfully")
    else:
        print("File not present")


def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """
    try:

        path = os.path.join(current_working_directory, file_name)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                file_content = f.read()
                file_content_with_token = file_content + eof_token
                service_socket.sendall(file_content_with_token)
                print("Downloaded Successfully")
        else:
            service_socket.sendall(
                b"File doesn't exist"+eof_token)
            print("Could not download file - File doesn't exist")
    except:
        print("File not present")


class ClientThread(Thread):
    def __init__(self, service_socket: socket.socket, address: str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address

    def init_working_dir(self, client_working_directory):
        self.client_working_directory = client_working_directory

    def run(self):

        print(f"Connected by {self.address}")
        # send random eof token
        eof_token = generate_random_eof_token(8).encode()
        self.service_socket.sendall(eof_token)

        self.init_working_dir(common_dir)
        # establish working directory
        directory = (get_working_directory_info(
            self.client_working_directory)).encode()+eof_token
        # send the current dir info
        self.service_socket.sendall(directory)

        while True:
            client_cmd = receive_message_ending_with_token(
                self.service_socket, 1024, eof_token)
            client_cmd = client_cmd.decode()
            # get the command and arguments and call the corresponding method
            if (client_cmd.split(' ')[0] == "cd"):
                receive = handle_cd(
                    self.client_working_directory, client_cmd.split(' ')[1])
                self.service_socket.sendall(
                    (get_working_directory_info(receive).encode()+eof_token))

            elif (client_cmd.split(' ')[0] == "mkdir"):
                handle_mkdir(self.client_working_directory,
                             client_cmd.split(' ')[1])
                self.service_socket.sendall(
                    (get_working_directory_info(self.client_working_directory)).encode()+eof_token)

            elif (client_cmd.split(' ')[0] == "rm"):
                handle_rm(self.client_working_directory,
                          client_cmd.split(' ')[1])
                self.service_socket.sendall(
                    (get_working_directory_info(self.client_working_directory)).encode()+eof_token)

            elif (client_cmd.split(' ')[0] == "ul"):
                handle_ul(self.client_working_directory, client_cmd.split(' ')[1],
                          self.service_socket, eof_token)
                self.service_socket.sendall(
                    (get_working_directory_info(self.client_working_directory)).encode()+eof_token)

            elif (client_cmd.split(' ')[0] == "dl"):
                handle_dl(self.client_working_directory, client_cmd.split(' ')[
                          1], self.service_socket, eof_token)
                self.service_socket.sendall(
                    (get_working_directory_info(self.client_working_directory)).encode()+eof_token)

            elif (client_cmd.split(' ')[0] == "exit"):
                print("Exit from directory")
                print('Connection closed from:', self.address)
            else:
                print("Completed")
            self.init_working_dir(receive)


def main():
    HOST = "127.0.0.1"
    PORT = 65432
    global common_dir
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        common_dir = os.getcwd()
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print('Server is up and Listening')
        print('Waiting for the incoming connections')
        while True:
            conn, addr = server_socket.accept()
            client_thread = ClientThread(conn, addr)
            client_thread.start()


if __name__ == '__main__':
    main()
