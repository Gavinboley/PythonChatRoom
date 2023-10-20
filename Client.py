"""
Project Part One

Name: Gavin Boley

Pawprint: gzbkxc
Student Number:12582542

Date: 10/19/2023

Program Description: A simple chat room application that consists of a server script for handling user accounts and client connections, and two client scripts that allow users to connect to the server, send messages, and interact in a multi-user chat room environment.
"""
import socket
import threading

def receive_messages(client):
    while True:
        try:
            response = client.recv(1024).decode('utf-8')
            if not response:
                print("Connection to the server has been lost.")
                break
            print(response)
        except:
            print("Connection to the server has been lost.")
            exit()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("My chat room client. Version Two")
        client.connect(('127.0.0.1', 12542))

        message_thread = threading.Thread(target=receive_messages, args=(client,))
        message_thread.daemon = True
        message_thread.start()

        while True:
            command = input()

            command_parts = command.split()
            if command_parts[0] in ['login', 'newuser', 'send', 'logout', 'who']:
                if command_parts[0] == 'login' and len(command_parts) == 3:
                    client.send(command.encode('utf-8'))
                elif command_parts[0] == 'newuser' and (len(command_parts) == 3) and (3 <= len(command_parts[1]) <= 32) and (4 <= len(command_parts[2]) <= 8):
                    client.send(command.encode('utf-8'))
                elif command_parts[0] == 'send' and len(command_parts) >= 3 and len(' '.join(command_parts[2:])) <= 256:
                    client.send(command.encode('utf-8'))
                elif command_parts[0] == 'logout' and len(command_parts) == 1:
                    client.send(command.encode('utf-8'))
                elif command_parts[0] == 'who' and len(command_parts) == 1:
                    client.send(command.encode('utf-8'))
                else:
                    print("Invalid command arguments.")
                    continue
            else:
                print("Invalid command.")
                continue

    except ConnectionRefusedError:
        print("Server could not be found. Please restart the client.")
    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        client.close()

if __name__ == '__main__':
    main()

