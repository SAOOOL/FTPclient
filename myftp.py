#This program is an FTP client that supports ls, cd, get, put, delete, and quit commands. 
import sys
from socket import socket, AF_INET, SOCK_STREAM

# get server name from command line
if len(sys.argv) != 2:
    print('Usage: myftp ftp_server_name')
    sys.exit()
server = sys.argv[1]

# create control connection socket
control_socket = socket(AF_INET, SOCK_STREAM)
# initiate control TCP connection
try:
    control_socket.connect((server, 21))
except Exception:
    print(f'Error: server {server} cannot be found.')
    sys.exit()
print(f'Connected to {server}.')

# print message from server
response = control_socket.recv(1024).decode('utf-8').strip()
print(response)

# send user name to server
username = input('Enter username: ')
control_socket.send(bytes(f'USER {username}\r\n', 'utf-8'))
response = control_socket.recv(1024).decode('utf-8').strip()
print(response)

# send password to server
password = input('Enter password: ')
control_socket.send(bytes(f'PASS {password}\r\n', 'utf-8'))
response = control_socket.recv(1024).decode('utf-8').strip()
print(response)
ip = 0
port = 0 
# login successful
if response.startswith('230'):
    # main loop
    loop = True
    while loop:
        print('Please enter a command')
        command_input = input('myftp> ')
        command =  command_input.split()[0]
        if command == 'quit':
            # end session
            control_socket.send(bytes('QUIT\r\n', 'utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            control_socket.close()
            loop = False
        elif command == 'get':
            arg = command_input.split()[1]
            #Get available port for data transfer from server using PASV
            control_socket.send(bytes('PASV\r\n', 'utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            # parse response to extract ip and port numbers
            start = response.index("(") + 1
            end = response.index(")")
            data_conn = tuple(map(int, response[start:end].split(",")))
            ip = ".".join(str(x) for x in data_conn[:4])
            port = data_conn[4] * 256 + data_conn[5]
            #create socket for data transfer
            data_socket = socket(AF_INET, SOCK_STREAM)
            data_socket.connect((ip, port))
            # send List Command, recieve responses
            control_socket.sendall(f'RETR {arg}\r\n'.encode('utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            # receive the file's contents
            bytes_transferred = 0
            file_contents = b""
            while True:
                chunk = data_socket.recv(1024)
                if not chunk:
                    break
                file_contents += chunk
                bytes_transferred += len(chunk)
            # write the file's contents to disk
            with open(arg, "wb") as file:
                file.write(file_contents)
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            print(f"bytes transferred: {bytes_transferred}")
            bytes_transferred = 0
            data_socket.close()
        elif command == 'put':
            arg = command_input.split()[1]
            #Get available port for data transfer from server using PASV
            control_socket.send(bytes('PASV\r\n', 'utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            # parse response to extract ip and port numbers
            start = response.index("(") + 1
            end = response.index(")")
            data_conn = tuple(map(int, response[start:end].split(",")))
            ip = ".".join(str(x) for x in data_conn[:4])
            port = data_conn[4] * 256 + data_conn[5]
            #create socket for data transfer
            data_socket = socket(AF_INET, SOCK_STREAM)
            data_socket.connect((ip, port))
            # send Put(STOR) Command
            control_socket.sendall(f'STOR {arg}\r\n'.encode('utf-8'))
            response = control_socket.recv(1024).decode("utf-8").strip()
            print(response)
            # Send the file and it's contents
            bytes_transferred = 0
            with open(arg, "rb") as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        data_socket.close()
                        break
                    data_socket.send(chunk)
                    bytes_transferred += len(chunk)
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            print(f"bytes transferred: {bytes_transferred}")
            bytes_transferred = 0
            # data_socket.close()
        elif command == 'ls':
            # Get available port for data transfer from server using PASV
            control_socket.send(bytes('PASV\r\n', 'utf-8'))
            print(response)
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            # parse response to extract ip and port numbers
            start = response.index("(") + 1
            end = response.index(")")
            data_conn = tuple(map(int, response[start:end].split(",")))
            ip = ".".join(str(x) for x in data_conn[:4])
            port = data_conn[4] * 256 + data_conn[5]
            # create socket for data transfer
            data_socket = socket(AF_INET, SOCK_STREAM)
            data_socket.connect((ip, port))
            # send List Command, recieve responses
            control_socket.sendall(f'LIST\r\n'.encode('utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            files = data_socket.recv(1024).decode('utf-8').strip().split('\n')
            for file in files:
                print(file)
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
            data_socket.close()
            #cd and delete commands do not require any data sockets since no information is being exchanged
        elif command == 'delete':
            arg = command_input.split()[1]
            print(arg)
            control_socket.sendall(f'DELE {arg}\r\n'.encode('utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)
        elif command == 'cd':
            arg = command_input.split()[1]
            control_socket.sendall(f'CWD {arg}\r\n'.encode('utf-8'))
            response = control_socket.recv(1024).decode('utf-8').strip()
            print(response)


        else:
            print(f'Error: command "{command}" not supported.')
