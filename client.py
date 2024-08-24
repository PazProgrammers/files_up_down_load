import socket
import os
LENGTH_FIELD_SIZE = 5
directory = r"C:\Users\uriel\PycharmProjects\pythonProject15\client_folder"

def create_client():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", 8200))
    return my_socket


def get_msg(my_socket, type):
    if type == "txt":
        length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
        message = my_socket.recv(int(length)).decode()
    elif type == "jpg":
        message = my_socket.recv(200000)
    return message


def send_msg(my_socket, data, type):
    if type == "txt":
        length = str(len(data))
        zfill_length = length.zfill(LENGTH_FIELD_SIZE)
        data = zfill_length + data
        my_socket.send(data.encode())
    else:
        my_socket.send(data)


def open_file(filename, directory, type):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, filename)
    if type == "txt":
        file = open(file_path, 'w')
    elif type == "jpg":
        file = open(file_path, 'wb')
    return file


def upload(my_socket, cmd):
    filename = input("Input filename you want to upload: ")
    #filename = file_path[file_path.rfind(""):]
    directory = input("Input the directory you would like to upload the file from: ")
    file_path = os.path.join(directory, filename)
    data = cmd + " " + filename
    send_msg(my_socket, data, "txt")
    type = filename[filename.rfind(".") + 1:]
    try:
        # Reading file and sending data to server
        if type == "txt":
            file = open(file_path, "r")
        elif type == "jpg":
            file = open(file_path, "rb")
        data = file.read()
        if not data:
            return
        while data:
            send_msg(my_socket, data, type)
            data = file.read()
            # File is closed after data is sent
        file.close()
        send_msg(my_socket, "DONE", "txt")

    except IOError:
        print("You entered an invalid filename!\
        Please enter a valid name")


def download(my_socket, cmd):
    filename = input("Input filename you want to download: ")
    request = cmd + " " + filename
    send_msg(my_socket, request, "txt")
    type = filename[filename.rfind(".") + 1:]
    data = get_msg(my_socket, type)
    if type == "txt" and filename in data:
        print(data)
        return
    elif type == "jpg" and filename.encode() in data:
        print(data.decode())
        return
    directory = input("Input the directory you would like to download the file to: ")
    file = open_file(filename, directory, type)
    while True:
        if type == "txt" and data == "DONE":
            break
        file.write(data)
        if type == "jpg":
            break
        data = get_msg(my_socket, type)
    file.close()


def main():
    my_socket = create_client()
    while True:
        cmd = input("Input your command: ")
        if cmd == "UPLOAD":
            upload(my_socket, cmd)
        elif cmd == "DOWNLOAD":
            download(my_socket, cmd)
        elif cmd == "EXIT":
            send_msg(my_socket, cmd, "txt")
            print("Closing\n")
            # Close socket
            my_socket.close()
            return


if __name__ == "__main__":
    main()
