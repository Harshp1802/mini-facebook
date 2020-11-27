import time
from datetime import datetime
import pickle
import numpy as np


def load_data(data_path):
    f = open(data_path,"rb")
    DATABASE = pickle.load(f)
    f.close()
    return DATABASE

def get_pending_requests(DATABASE,username,socket_client):
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

def get_feed(DATABASE,username,socket_client):
    response = "Your Feed\n\n"
    my_feed = []
    my_friends = DATABASE[username]['friends']
    for friend in my_friends:
        for post in DATABASE[friend]['posts_global']:
            my_feed.append([friend,post])
    my_feed = sorted(my_feed,key= lambda x: x[1][1],reverse=True)

    flag_end = False
    while(True):
        for i in range(4):
            try:
                each = my_feed.pop(0)
                response = response + "Friend: {}\n".format(each[0])
                response = response + "Post, Time: {}\n".format(str(each[1][1])) + each[1][0] + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Posts\n"
            socket_client.send(response.encode())
            break
        else:
            response += "0: Go Back\n1: See Previous Posts\n"
            socket_client.send(response.encode())
            response = ''
            answer = socket_client.recv(1024).decode()
            if(answer=="0"):
                break

def upload_post(DATABASE,username,socket_client):
    response = "Please Type the content of the post (Max 125 characters)\n"
    socket_client.send(response.encode())
    post_content = socket_client.recv(1024).decode()
    response = "Do you want the post to be global or private?\np: Private\t(reply with p)\ndefault: global"
    socket_client.send(response.encode())
    post_visibility = socket_client.recv(1024).decode()
    post_timestamp = datetime.now()
    post = [post_content,post_timestamp]
    if post_visibility == 'p':
        DATABASE[username]['posts_private'].append(post)
    else:   
        DATABASE[username]['posts_global'].append(post)
    socket_client.send("Post uploaded, check Timeline\n".encode())

def get_timeline(DATABASE,username,socket_client):
    response = 'Your Timeline\n\n'
    my_posts = []
    for i in DATABASE[username]['posts_global']:
        my_posts.append(i)
    for i in DATABASE[username]['posts_private']:
        my_posts.append(i)
    my_posts = sorted(my_posts,key= lambda x: x[1],reverse=True)
    
    flag_end = False
    while(True):
        for i in range(4):
            try:
                each = my_posts.pop(0)
                response = response + "Post, Time: {}\n".format(str(each[1])) + each[0] + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Posts\n"
            socket_client.send(response.encode())
            break
        else:
            response += "0: Go Back\n1: See Previous Posts\n"
            socket_client.send(response.encode())
            response = ''
            answer = socket_client.recv(1024).decode()
            if(answer=="0"):
                break
   
def search_user(DATABASE,username,socket_client,user_list):
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

def get_friends_of_friends(DATABASE,username,socket_client):
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

def see_friends(DATABASE,username,socket_client):
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

def check_username(username, user_list):
    if(username in user_list):
        return(0)
    return(1)

def add_client(DATABASE,user_list,username,password):
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

    write_database("database.pkl", DATABASE)

def login(DATABASE,user_list,socket_client):
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
        if(check_username(username, user_list) == 0 and DATABASE[username]["Password"] == password):
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
            socket_client.send("Please Enter New Username (Max 32 Characters): ".encode())
            username = socket_client.recv(1024).decode()
            if(check_username(username,user_list) == 0):
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
        add_client(DATABASE,user_list,username,password)
        return username

def write_database(save_dir, DATABASE):
    f = open(save_dir, "wb")
    pickle.dump(DATABASE,f)
    f.close()

def delete_post(DATABASE,username,socket_client):
    response = 'Your Timeline\n\n'
    my_posts = []
    for i in DATABASE[username]['posts_global']:
        my_posts.append(i)
    for i in DATABASE[username]['posts_private']:
        my_posts.append(i)
    my_posts = sorted(my_posts,key= lambda x: x[1],reverse=True)
    
    flag_end = False
    while(True):
        four_posts = []
        for i in range(4):
            try:
                each = my_posts.pop(0)
                four_posts.append(each)
                response = response + "Post " + str(i+1) + ", Time: {}\n".format(str(each[1])) + each[0] + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Posts\n"
        response += "0: Go Back\nenter post number to delete\nenter 5 to see next posts"
        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        
        try:
            post = four_posts[int(answer)-1]
            try:
                DATABASE[username]['posts_global'].remove(post)
            except:
                DATABASE[username]['posts_private'].remove(post)
            socket_client.send("Post successfully removed\n".encode())
            flag_end = True
        except:
            pass
        
        if(answer=="0" or flag_end):
            break

def remove_friend(DATABASE,username,socket_client):
    response = 'Your Friends\n\n'
    my_friends = []
    for i in DATABASE[username]['friends']:
        my_friends.append(i)
    my_friends.sort()    

    flag_end = False
    while(True):
        ten_friends = []
        for i in range(10):
            try:
                each = my_friends.pop(0)
                ten_friends.append(each)
                response = response + str(i+1) + ". " + each + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Friend List\n"
        response += "0: Go Back\nenter number to remove friend\nenter 11 to see more friends"

        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        
        try:
            f = ten_friends[int(answer)-1]
            DATABASE[username]['friends'].remove(f)
            socket_client.send("Friend successfully removed\n".encode())
            flag_end = True
        except:
            pass
        
        if(answer=="0" or flag_end):
            break





