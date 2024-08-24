import socket
import os
LENGTH_FIELD_SIZE = 5
directory = r"C:\Users\uriel\PycharmProjects\pythonProject15\download_folder"


def create_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8200))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")
    return server_socket, client_socket


def get_msg(my_socket, type):
    if type == "txt":
        length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
        message = my_socket.recv(int(length)).decode()
    elif type == "jpg":
        message = my_socket.recv(20000)
    return message


def send_msg(my_socket, data, type):
    if type == "txt":
        length = str(len(data))
        zfill_length = length.zfill(LENGTH_FIELD_SIZE)
        data = zfill_length + data
        my_socket.send(data.encode())
    else:
        my_socket.send(data)


def open_file(filename, type):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    if type == "txt":
        file = open(file_path, 'w')
    elif type == "jpg":
        file = open(file_path, 'wb')
    return file


def upload(filename, client_socket):
    type = filename[filename.rfind(".") + 1:]
    file = open_file(filename, type)
    while True:
        data = get_msg(client_socket, type)
        if type == "txt" and data == "DONE" or type == "jpg" and "DONE".encode() is data:
            break
        file.write(data)
    file.close()


def download(filename, client_socket):
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        send_msg(client_socket, filename + " does not exist in files folder", "txt")
        return
    type = filename[filename.rfind(".") + 1:]
    if type == "txt":
        file = open(file_path, "r")
    elif type == "jpg":
        file = open(file_path, "rb")
    data = file.read()
    if not data:
        return
    while data:
        send_msg(client_socket, data, type)
        data = file.read()
        # File is closed after data is sent
    file.close()
    send_msg(client_socket, "DONE", "txt")


def main():
    server_socket, client_socket = create_server()
    while True:
        msg = get_msg(client_socket, "txt").split(" ")
        cmd = msg[0]
        if cmd == "UPLOAD":
            upload(msg[1], client_socket)
        elif cmd == "DOWNLOAD":
            download(msg[1], client_socket)
        elif cmd == "EXIT":
            print("Closing\n")
            # Close sockets
            client_socket.close()
            server_socket.close()
            return


if __name__ == "__main__":
    main()