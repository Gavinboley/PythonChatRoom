"""
Project Part One

Name: Gavin Boley

Pawprint: gzbkxc
Student Number:12582542

Date: 10/19/2023

Program Description: A simple chat room application that consists of a server script for handling user accounts and client connections, and two client scripts that allow users to connect to the server, send messages, and interact in a multi-user chat room environment.
"""

from re import I
import socket
import threading

# Initialize an empty dictionary to store user accounts
users = {}
user_lock = threading.Lock()
MAXCLIENTS = 3

client_sockets = []
client_usernames = []
username_sockets = {}
logged_in_users = []

# Function to read user accounts from a file (if it exists)
def read_user_accounts():
    try:
        with open('users.txt', 'r') as file:
            for line in file:
                data = line.strip()[1:-1].split(', ')
                if len(data) == 2:
                    username, password = data
                    with user_lock:
                        users[username] = password
    except FileNotFoundError:
        # Create the file if it doesn't exist
        open('users.txt', 'w').close()

# Function to handle client requests
def handle_client(client_socket):
    username = None

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')

            if not data:
                break

            command = data.split()

            if command[0] == 'login':
                if username is None:
                    if len(command) == 3:
                        with user_lock:
                            if command[1] in users and users[command[1]] == command[2]:
                                if isLoggedIn(command[1]):
                                    client_socket.send("Denied. User name already logged in.".encode('utf-8'))
                                else:
                                    username = command[1]
                                    username_sockets[username] = client_socket
                                    client_usernames.append(username)
                                    logged_in_users.append(username)
                                    print(f"{username} login.")
                                    client_socket.send("login confirmed.".encode('utf-8'))
                                    broadcast(f'{username} joins.', client_socket)
                            else:
                                client_socket.send("Denied. User name or password incorrect.".encode('utf-8'))
                    else:
                        client_socket.send("Denied. Invalid Arguments. Format: {Username} {Password}".encode('utf-8'))
                else:
                    client_socket.send("Denied. Already logged in.".encode('utf-8'))
            elif command[0] == 'newuser':
                if username is None:
                    if len(command) == 3 and 3 <= len(command[1]) <= 32 and 4 <= len(command[2]) <= 8:
                        with user_lock:
                            if command[1] not in users:
                                users[command[1]] = command[2]
                                with open('users.txt', 'a') as file:
                                    file.write(f'\n({command[1]}, {command[2]})')
                                print(f"New user account created.")
                                client_socket.send("New user account created. Please login.".encode('utf-8'))
                            else:
                                client_socket.send("Denied. User account already exists.".encode('utf-8'))
                    else:
                        client_socket.send("Denied. Invalid username or password.".encode('utf-8'))
                else:
                    client_socket.send("Denied. Already logged in.".encode('utf-8'))
            elif command[0] == 'send':
                if command[1] == 'all':
                    if username is not None:
                        message = ' '.join(command[2:])
                        if len(command) > 2 and len(message) <= 256:
                            broadcast_message = f'{username}: {message}'
                            print(broadcast_message)
                            broadcast(f'{username}: {message}', client_socket)
                        elif len(message) >= 257:
                            client_socket.send("Denied. Character Limit 256.".encode('utf-8'))
                        else:
                            client_socket.send("Denied. Please provide a message to send.".encode('utf-8'))
                    else:
                        client_socket.send("Denied. Please login first.".encode('utf-8'))
                elif isUsername(command[1]):
                    if username is not None:
                        message = ' '.join(command[2:])
                        if len(command) > 2 and len(message) <= 256:
                            private_message = f'{username}: {message}'
                            print(f"{username} (To {command[1]}): " + message)
                            send_private_message(command[1], private_message)
                    else:
                        client_socket.send("Denied. Please login first.".encode('utf-8'))
                else:
                    client_socket.send("Invalid command arguments. Use 'all' or 'USERID' as second parameter".encode('utf-8'))
            elif command[0] == 'who':
                if username is not None:
                    online_users = ', '.join(logged_in_users)
                    client_socket.send(f"{online_users}".encode('utf-8'))
                else:
                    client_socket.send("Denied. Please login first.".encode('utf-8'))
            elif command[0] == 'logout':
                if username is not None:
                    print(f"{username} logout.")
                    broadcast(f'{username} left.', client_socket)
                    client_socket.send(f"{username} left.".encode('utf-8'))
                    logged_in_users.remove(username)
                    client_usernames.remove(username)
                    username_sockets.pop(username)
                    username = None
                    client_sockets.remove(client_socket)
                    client_socket.close()
                else:
                    client_socket.send("Denied. Not logged in.".encode('utf-8'))
            else:
                client_socket.send("Invalid command.".encode('utf-8'))
        except:
            print(f"Client: {username} forcefully closed")
            broadcast(f'{username}: logout', client_socket)
            if username is not None:
                logged_in_users.remove(username)
                client_usernames.remove(username)
                username_sockets.pop(username)
            username = None
            break

def isUsername(usernamelocal):
    for i in range(len(client_usernames)):
        if usernamelocal == client_usernames[i]:
            return True
    return False

def isLoggedIn(usernamelocal):
    for i in range(len(logged_in_users)):
        if usernamelocal == logged_in_users[i]:
            return True
    return False

def broadcast(message, sender_socket):
    for client_socket in client_sockets:
        try:
            if client_socket != sender_socket and client_socket in username_sockets.values():
                client_socket.send(message.encode('utf-8'))
        except:
            pass

def send_private_message(target_username, message):
    if target_username in username_sockets:
        target_socket = username_sockets[target_username]
        target_socket.send(message.encode('utf-8'))


def accept_clients(server):
    while len(client_sockets) < MAXCLIENTS:
        client_socket, addr = server.accept()
        client_sockets.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 12542))
    server.listen(MAXCLIENTS)
    read_user_accounts()
    print("My chat room server. Version Two.\n")

    accept_clients(server)

if __name__ == '__main__':
    main()
