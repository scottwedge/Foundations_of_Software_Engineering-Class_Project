"""
"""
import select
import socket
import sys
import time


class Client:
    def __init__(self):
        print("Welcome to clue! Have the server run on localhost!")
        HOST, PORT = "localhost", 4444
        player_name = input("Enter the name other players should see you as! ")

        print(player_name)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            sock.sendall(bytes(player_name, "utf-8"))
            sock.sendall(b"!")
            # Receive data from the server and shut down
            while sock:
                sock.sendall(b"?")
                turn = sock.recv(1024)
                print("Its {}'s turn!".format(turn))
                if turn == bytes(player_name, "utf-8"):
                    print("Its our turn!")
                    command = input("Enter your next move: ")
                    sock.sendall(b"T")
                    sock.sendall(bytes(command, "utf-8"))
                    validity  = sock.recv(1)   # server will respond with I or V for valid or invalid 
                    if validity == b"V":
                        print("Valid move!")
                elif turn:
                    print("Its {}'s turn!".format(turn))
                    time.sleep(5) # just so we dont spin inf
                else:
                    sock.close()


        print("Thanks for playing!")

if __name__ == "__main__":
    client = Client()