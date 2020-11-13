import socket
import time
import datetime
import _thread
import pickle
import numpy as np
from collections import defaultdict


MAX_USERS = 1000
server_ip = "127.0.0.1" # Server ip
server_port   = 12345 # Server Port

'''
DATABASE = {"user1": 
                {
                "Password": "pass",
                "socket_details": "",
                "is_online": False,
                "friends": [],
                "pending_friend_requests" : [],
                "posts_visible_friends": [],
                "posts_global": [],
                "posts_private": [],
                }
            } # Read from the file
'''

f = open("database.pkl","rb")
DATABASE = pickle.load(f)
user_list = []
for i in DATABASE:
    user_list.append(i)
f.close()
'''
def home_screen(username, socket_client):
    
    while(True):
        user_home = "Welcome to Mini-Face:\n"
        f_reqs = DATABASE[username]["pending_friend_requests"]
        if(f_reqs):    
            user_home += "Pending Friend Requests:\n"
            for i in range(len(f_reqs)):
                each = str(i+1) + ". " + f_reqs[i] + "\n"
                user_home += each
            user_home += "Select a request, 0 to ignore all\n"
            socket_client.send(user_home)
            r_no = socket_client.recv(1024)
            if(r_no!=0):
                response = str(r_no) + ". " + f_reqs[r_no-1] + "\n"
                response += "Accept(y) or Delete(n)"
                socket_client.send(response)
                ans = socket_client.recv(1024)
                
                if(ans=='y'):
                    DATABASE[username]['friends'].append(f_reqs[r_no])
                    DATABASE[f_reqs[r_no]]['friends'].append(username)
                DATABASE[username]['pending_friend_requests'].remove(f_reqs)
        
        home_options(username, socket_client)
'''
def home_screen(username, socket_client):
    while(True):
        socket_client.send(
            """
            Welcome to Mini-Face
            Options: (Reply with)
            1: Friends
            2: Messages
            3: Pending Friend Requests
            0: Exit Mini-Face
            """.encode())
        option = socket_client.recv(1024).decode()
        if(option == "1"):
            friend_options(username, socket_client)
        elif(option == "2"):
            messages = 0 # Message options
        elif(option == "3"):
            f_reqs = DATABASE[username]["pending_friend_requests"]
            response = ''
            if(f_reqs):    
                response += "Pending Friend Requests:\n"
                for i in range(len(f_reqs)):
                    each = str(i+1) + ". " + f_reqs[i] + "\n"
                    response += each
                response += "Select a request, 0 to ignore all\n"
                socket_client.send(response.encode())
                r_no = int(socket_client.recv(1024).decode())
                if(r_no!=0):
                    response = str(r_no) + ". " + f_reqs[r_no-1] + "\n"
                    response += "Accept(y) or Delete(n)"
                    socket_client.send(response.encode())
                    ans = socket_client.recv(1024).decode()
                    
                    if(ans=='y'):
                        DATABASE[username]['friends'].append(f_reqs[r_no-1])
                        DATABASE[f_reqs[r_no-1]]['friends'].append(username)
                    DATABASE[username]['pending_friend_requests'].remove(f_reqs[r_no-1])
            else:
                response = "No Pending Requests...\nPress a key to go back"
                socket_client.send(response.encode())

        elif(option == "0"):
            return
        else:
            socket_client.send("Invalid Option!".encode())

def find_friend(username, socket_client):
    while True:    
        socket_client.send(
            """
            Find Friends        
            1: Search for Friends
            2: See Friends of Friends
            0: Go to Friend Options
            """.encode())
        option = socket_client.recv(1024).decode()
        if(option == "0"):
            return
        if(option == "1"):
            socket_client.send("Enter the search query:\n".encode())
            query = socket_client.recv(1024).decode()
            response = "Search Results: \n"
            count = 0
            search_result = []
            for i in user_list:
                if i.find(query) != -1:
                    search_result.append(i)
            search_result = np.array(search_result)
            self_index = np.argwhere(search_result==username)
            search_result = np.delete(search_result,self_index)         # delete self
            search_result = np.delete(search_result,np.argwhere(search_result in DATABASE[username]['friends'])) # delete client's friends
            
            for i in search_result:
                each = str(count+1) + ". " + i + "\n"
                response += each
                count+=1
            if(count == 0):
                response = "No results found"
            else:
                response += "Enter number to send friend request\n"
            socket_client.send(response.encode())
            friend_number = int(socket_client.recv(1024).decode())

            if username not in DATABASE[ search_result[friend_number-1] ]['pending_friend_requests']:       # check if already exists
                DATABASE[ search_result[friend_number-1] ]['pending_friend_requests'].append(username)

        if(option == "2"):
            if(len(DATABASE[username]['friends'] < 2)):
                response = "Make more friends!"
                socket_client.send(response.encode())
            else:
                fof = []
                for i in DATABASE[username]['friends']:
                    for j in DATABASE[i]['friends']:
                        fof.append(j)
                fof = np.array(fof)
                fof = np.unique(fof)
                self_index = np.argwhere(fof==username)
                fof = np.delete(fof,self_index)         # delete self
                fof = fof - np.array(DATABASE[username]['friends']) # delete client's friends

                response = "Results:\n"
                for i in range(len(fof)):
                    each = str(i+1) + ". " + fof[i] + "\n"
                    response += each
                response += "Enter number to send friend request\n"
                socket_client.send(response.encode())
                friend_number = int(socket_client.recv(1024).decode())

                if username not in DATABASE[ fof[friend_number-1] ]['pending_friend_requests']:     # check if already exists
                    DATABASE[ fof[friend_number-1] ]['pending_friend_requests'].append(username)
    

def friend_options(username, socket_client):
    while True:    
        socket_client.send(
            """
            Friend Options        
            1: See your Friends
            2: Find new Friends
            3: Remove Friends
            0: Go to Home Screen
            """.encode())
        option = socket_client.recv(1024).decode()
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
            response += "Enter a key to go back"
            socket_client.send(response.encode())
        if(option == "2"):
            find_friend(username, socket_client)


def check_username(username):
    if(username in user_list):
        return(0)
    return(1)
def add_client(username,password):
    DATABASE[username] = {
                "Password": "",
                "is_online": False,
                "friends": [],
                "pending_friend_requests" : [],
                "posts_visible_friends": [],
                "posts_global": [],
                "posts_private": [],
                }
    DATABASE[username]["Password"] = password
    user_list.append(username)

    # Save to file
    f = open("database.pkl", "wb")
    pickle.dump(DATABASE,f)
    f.close()


def login(socket_client):
    username = ''
    password = ''
    socket_client.send(
        """
        Welcome to Mini-Face: (Reply with)
        1: Login
        2: Register
        """.encode())
    response = socket_client.recv(1024).decode()
    if(response == "1"):
        socket_client.send("Username: ".encode())
        username = socket_client.recv(1024).decode()
        socket_client.send("Password: ".encode())
        password = socket_client.recv(1024).decode()
        if(check_username(username) == 0 and DATABASE[username]["Password"] == password):
            socket_client.send("Login Succesfull\nPress a key to continue".encode())
            return username
        else:
            socket_client.send("Invalid Username/Password".encode())
            time.sleep(1)
            user = login(socket_client)
            return user


    else:
        success = 0
        while(success != 1):
            socket_client.send("Please Enter New Username: ".encode())
            username = socket_client.recv(1024).decode()
            if(check_username(username) == 0):
                socket_client.send("Username already Taken".encode())
                continue
            socket_client.send("Please Enter New Password: ".encode())
            password = socket_client.recv(1024).decode()
            socket_client.send("Please Confirm New Password: ".encode())
            password_C = socket_client.recv(1024).decode()
            if(password != password_C):
                socket_client.send("Password does not match".encode())
            else:
                success = 1
        add_client(username,password)
        return username

def client_thread(socket_client, address):

    user = login(socket_client)
    DATABASE[user]["is_online"] = True
    home_screen(user, socket_client)
    DATABASE[user]["is_online"] = False
    print("closing thread: ", address)
    socket_client.send("Thank you for using Mini-Face".encode())
    time.sleep(0.5)
    socket_client.close()
    
    

if(__name__ == "__main__"): 

    socket_tcp = socket.socket(family = socket.AF_INET,type =socket.SOCK_STREAM)

    # Creating Socket for TCP
    socket_tcp.bind((server_ip, server_port)) # Binding is necessary in TCP
    socket_tcp.listen(MAX_USERS) # Listents to the clients sending connection request

    print("Server is up and running")

    # creating thread for each new client
    while(True):
        socket_client, address = socket_tcp.accept()
        print("Client Connected:", address)

        _thread.start_new_thread(client_thread, (socket_client, address))
        
        

    
