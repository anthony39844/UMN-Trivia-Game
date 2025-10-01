# Fall 2025 CSCI 4211: Introduction to Computer Networks

# This program serves as the server of the trivia game application.
# Written in Python v3.

import sys, os
import socket
from threading import Thread
import time
import json
import random
import signal

# The server's information when the clients and server run on the same
# machine.
LOCAL_HOST = "localhost"
LOCAL_PORT = 5001

# The server's information when the server runs in the cloud and the clients
# are remote.
REMOTE_HOST = "0.0.0.0"
REMOTE_PORT = 5001

with open("trivia_questions.json", "r") as file:
    questions = json.load(file)

class Server:
    '''
    Initializes any class variables and data structures and reads necessary
    files.

    Parameters
    ----------
    - server_host : str
        - The IPv4 address or hostname of the server (e.g., "100.50.200.5" or 
          "localhost"). Its value is determined by which command line option
          was used to run the server (i.e., 1 or 2).
    - server_port : int
        - The TCP port number the server will run on (e.g., 5001). Its value 
          is determined by which command line option was used to run the 
          server (i.e., 1 or 2).
    '''
    def __init__(self, server_host, server_port):
        self.host = server_host
        self.port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        return

    '''
    Thread target function
    '''
    def handle_client(self, connection_socket, client_address):
        # print(f"Starting thread for {client_address}")
        self.trivia_game(connection_socket, client_address)


    '''
    The server facilitates the trivia game with the client based on the
    general interaction described in Section 2 in the instructions.

    Parameters
    ----------
    - connection_socket : socket
        - The open socket connected to the client that wants to play the
          trivia game.
    - client_address : (), tuple
        - Identifying information about the client connection (i.e., the 
          host and port number). There's no requirement for this parameter to
          be used in this function. However, it's useful when printing 
          debugging information to the server's terminal to differentiate
          between multiple clients.
    '''
    def trivia_game(self, client_socket, client_address):  
        while True:

            try:
                start_signal = client_socket.recv(1024).decode().strip()
            except ConnectionResetError:
                break  # Client disconnected

            if start_signal.lower() != 'start':
                break  # Client wants to quit

            score = 0
            available_keys = list(questions.keys())

            # send questions
            for _ in range(5):
                # Pick a random question
                key = random.choice(available_keys)
                q, options, answer = questions[key]

                # Format the question as a string
                question_text = f"QUESTION:{q} OPTIONS:"
                for i, option in enumerate(options, start=1):
                    question_text += f"{i}. {option}END:"
                question_text += "\n"

                # Send question to client
                client_socket.sendall(question_text.encode())

                # Receive client's answer
                guess = client_socket.recv(1024).decode().strip()

                # Check answer
                if guess == answer:
                    score += 1
                    client_socket.sendall("FEEDBACK:CORRECT!\n".encode())
                else:
                    client_socket.sendall(f"FEEDBACK:WRONG! The answer was '{questions[key][1][int(answer) - 1]}'\n".encode())
                
                # Remove the used question
                available_keys.remove(key)

            # End the game
            client_socket.sendall(f"GAMEOVER:Total score: {score}\n".encode())


        return

    '''
    Configures the server socket and waits to receive a new client connection.
    Once a client connection is accepted, the server handles the client and 
    facilitates a trivia game with it.
    '''
    def run(self):
        print(f"Server is running on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.socket.accept()
            print(f"Accepted connection from {client_address}")
            # Start a new thread for each client
            client_thread = Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()


    '''
    The server's signal handler. If Ctrl+C is pressed while the server is
    running, then the server will shutdown gracefully. This will allow you to
    immediately restart the server using the same port and a provide an easier
    testing process.

    NOTE: Do not modify this function beyond the listed TODO statement below.
    '''
    def signal_handler(self, sig, frame):
        print('\nReceived signal: ', sig)
        print('Performing cleanup...')
        # TODO: Add your cleanup code here (e.g., closing files, releasing 
        # resources, etc.).
        if self.socket:
            self.socket.close()
        print('Exiting gracefully.')
        sys.exit(0)

'''
This is the main() function that first executes when server.py runs. It
initializes the server instance and then runs it. 

NOTE: Do not modify this function.
'''
if (__name__ == '__main__'):
    # Check if an argument was provided on the command line. If not, then
    # print a usage message and exit the program.
    if (len(sys.argv) != 2):
        print("\nusage: python3 server.py [1 | 2]\n")
        sys.exit(1)

    # Check the value of the provided command line argument and initialize the
    # server instance accordingly. If the value is invalid, then print a usage 
    # message and exit the program.
    option = sys.argv[1]
    if (option == "1"):
        server = Server(LOCAL_HOST, LOCAL_PORT)
    elif (option == "2"):
        server = Server(REMOTE_HOST, REMOTE_PORT)
    else:
        print("\nusage: python3 server.py [1 | 2]\n")
        sys.exit(1)
    
    # Configure the server's signal handler to handle when Ctrl+C is pressed.
    signal.signal(signal.SIGINT, server.signal_handler)
    server.run()