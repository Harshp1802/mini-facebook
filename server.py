import socket
import time
import datetime
import thread

MAX_USERS = 1000
server_ip = "127.0.0.1" # Server ip
server_port   = 12345 # Server Port

DATABASE = {"user1": 
                {
                "Password": "pass",
                "socket_details": "",
                "is_online": False,
                "friends": [],
                "posts_visible_friends": [],
                "posts_global": [],
                "posts_private": [],
                }
            } # Read from the file


def home_screen(username, socket_client):
    
    while(True):
        socket_client.send(
            """
            Welcome to Mini-Face: (Reply with)
            1: Friends
            2: Messages
            0: Exit Mini-Face
            """)
        option = socket_client.recv(1024)
        if(option == "1"):
            friend_options(username, socket_client)
        elif(option == "2"):
            messages = 0 # Message options
        elif(option == "0"):
            return
        else:
            socket_client.send("Invalid Option!")


def friend_options(username, socket_client):
    socket_client.send(
        """
        Friend Options        
        1: See your Friends
        2: Find new Friends
        0: Go to Home Screen
        """)
    option = socket_client.recv(1024)
    if(option == "0"):
        return
    if(option == "1"):
        friend_list = DATABASE[username]["friends"]
        response = "Your Friend List: \n"
        for i in range(len(friend_list)):
            if(DATABASE[friend_list[i]]["is_online"]):
                status = "ONLINE"
            else:
                status = "Away"
            each = str(i+1) + ". " + friend_list[i] + ":\t" + status + "\n"
            response += each
        socket_client.send(response)



def check_username(username):
    if(username in DATABASE.keys()):
        return(0)
    return(1)
def add_client(username,password):
    DATABASE[username]["Password"] = password
    # Save to file

def login(socket_client):

    socket_client.send(
        """
        Welcome to Mini-Face: (Reply with)
        1: Login
        2: Register
        """)
    response = socket_client.recv(1024)
    if(response == "1"):
        socket_client.send("Username: ")
        username = socket_client.recv(1024)
        socket_client.send("Password: ")
        password = socket_client.recv(1024)
        if(check_username(username) == 0 and DATABASE[username]["Password"] == password):
            socket_client.send("Login Succesfull")
            return username
        else:
            socket_client.send("Invalid Username/Password")
            time.sleep(1)
            user = login(socket_client)
            return user


    else:
        success = 0
        while(success != 1):
            socket_client.send("Please Enter New Username: ")
            username = socket_client.recv(1024)
            if(check_username(username) == 0):
                socket_client.send("Username already Taken")
                continue
            socket_client.send("Please Enter New Password: ")
            password = socket_client.recv(1024)
            socket_client.send("Please Confirm New Password: ")
            password_C = socket_client.recv(1024)
            if(password != password_C):
                socket_client.send("Password does not match")
            else:
                success = 1
        add_client(username,password)
        return username

def client_thread(socket_client, address):

    user = login(socket_client)
    DATABASE[user]["is_online"] = True
    DATABASE[user]["socket_details"] = socket_client
    home_screen(user, socket_client)
    socket_client.send("Thank you for using Mini-Face")
    time.sleep(2)
    socket_client.close()
    
    

if(__name__ == "__main__"): 

    socket_tcp = socket.socket(family = socket.AF_INET,type =socket.SOCK_STREAM)

    # Creating Socket for TCP
    socket_tcp.bind((server_ip, server_port)) # Binding is necessary in TCP
    socket_tcp.listen(MAX_USERS) # Listents to the clients sending connection request

    # creating thread for each new client
    while(True):
        socket_client, address = socket_tcp.accept()
        print("Client Connected:", address)

        thread.start_new_thread(client_thread, (socket_client, address))
        
        

    
