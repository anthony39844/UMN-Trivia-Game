# Fall 2025 CSCI 4211: Introduction to Computer Networks

# This program serves as the client of the trivia game application.
# Written in Python v3.

import sys
from socket import *
import json
from time import sleep

# The server's information when the clients and server run on the same
# machine.
LOCAL_HOST = "localhost"
LOCAL_PORT = 5001

# The server's information when the server runs in the cloud and the clients
# are remote.
REMOTE_HOST = ""
REMOTE_PORT = -1

class Client:
    '''
    Initializes any class variables and data structures.

    Parameters
    ----------
    - server_host : str
        - The IPv4 address or hostname of the server (e.g., "100.50.200.5" or 
          "localhost"). Its value is determined by which command line option
          was used to run the client (i.e., 1 or 2).
    - server_port : int
        - The TCP port number the server will run on (e.g., 5001). Its value 
          is determined by which command line option was used to run the 
          client (i.e., 1 or 2).
    '''
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        return

    '''
    Connects to the server and facilitates the trivia game with the server
    based on the general interaction described in Section 2 in the 
    instructions.
    '''
    def run(self):
        print("=====================================================================")
        print("                    University of Minnesota Trivia                   ")
        print("=====================================================================\n")
            
        print("\n------------------------- GAME INSTRUCTIONS -------------------------")
        print("  • Five random trivia questions about the University of Minnesota")
        print("    will be proposed to you along with possible answers.\n")
        
        print("  • Select your answer by entering the associated number (e.g., '1').\n")
        
        print("  • After all five questions have been answered, you will receive")
        print("    your total score.")

        while(1):
        
            print("\nWould you like to start a new game? [y/n]: ")

            # Get the user's response.
            while (1):
                print("Input: ", end = "")
                st = input()
                if ((st != "y") and (st != "Y") and (st != "n") and (st != "N")):
                    continue
                else:
                    break
            
            # If the input is "n" or "N", then quit the program.
            if ((st == "n") or (st == "N")):
                print("\nClient is exiting...")
                sys.exit(0)

            # Create a TCP socket and connect to the server.
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))    

            print(f"\nWelcome to the Trivia Game!\n")

            end = False
            count = 1
            while not end:
                # Receive question
                data = self.client_socket.recv(1024).decode().split('\n')
                if not data:
                    break

                # Process each message from the server
                for line in data:
                    # Print question and options
                    if line.startswith("QUESTION:"):
                        question, options = line.split("OPTIONS:")
                        print("------------------------------------------------------------------------------------------")
                        print(f"Question {count}: {question[len('QUESTION:'):]}") 
                        print("------------------------------------------------------------------------------------------")
                        count += 1
                        for option in options.split("END:"):
                            print(f"{option}")

                        # Get user's answer
                        while True:
                            answer = input("Your answer: ")
                            if not answer:
                                continue
                            self.client_socket.sendall(answer.encode())
                            break

                    # Print feedback of the answer
                    elif line.startswith("FEEDBACK:"):
                        print(line[len("FEEDBACK:"):] + "\n")

                    # End the game
                    elif line.startswith("GAMEOVER:"):
                        print("\n----------------------------- GAME OVER -----------------------------")
                        print(line[len("GAMEOVER:"):] + "\n")
                        print("Thanks for playing!\n")
                        end = True
                        break

            # Close the socket.
            self.client_socket.close()
        return  

'''
This is the main() function that first executes when client.py runs. It
initializes the client instance and then runs it. 

NOTE: Do not modify this function.
'''
if (__name__ == '__main__'):
    # Check if an arçgument was provided on the command line. If not, then
    # print a usage message and exit the program.
    if (len(sys.argv) != 2):
        print("\nusage: python3 client.py [1 | 2]\n")
        sys.exit(1)

    # Check the value of the provided command line argument and initialize the
    # server instance accordingly. If the value is invalid, then print a usage 
    # message and exit the program.
    option = sys.argv[1]
    if (option == "1"):
        client = Client(LOCAL_HOST, LOCAL_PORT)
    elif (option == "2"):
        client = Client(REMOTE_HOST, REMOTE_PORT)
    else:
        print("\nusage: python3 client.py [1 | 2]\n")
        sys.exit(1)
    
    client.run()