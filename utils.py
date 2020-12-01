import socket
import time
from datetime import datetime
import pickle
import numpy as np
from collections import defaultdict 
import database

def get_pending_requests(username,socket_client):
    f_reqs = database.DATABASE[username]["pending_friend_requests"].copy()
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
                database.DATABASE[username]['friends'].append(f_reqs[r_no-1])
                database.DATABASE[f_reqs[r_no-1]]['friends'].append(username)
            database.DATABASE[username]['pending_friend_requests'].remove(f_reqs[r_no-1])
            # print(DATABASE)

    else:
        response = "No Pending Requests...\nPress a key to go back"
        socket_client.send(response.encode())

def get_feed(username,socket_client):
    response = "Your Feed\n\n"
    my_feed = []
    my_friends = database.DATABASE[username]['friends'].copy()
    for friend in my_friends:
        for post in database.DATABASE[friend]['posts_global']:
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
            response += "End of Posts\n0: Go Back\n"
            socket_client.send(response.encode())
            break
        else:
            response += "0: Go Back\n1: See Previous Posts\n"
            socket_client.send(response.encode())
            response = ''
            answer = socket_client.recv(1024).decode()
            if(answer=="0"):
                break

def upload_post(username,socket_client):
    response = "Please Type the content of the post (Max 125 characters)\n"
    socket_client.send(response.encode())
    post_content = socket_client.recv(1024).decode()
    response = "Do you want the post to be global or private?\np: Private\t(reply with p)\ndefault: global"
    socket_client.send(response.encode())
    post_visibility = socket_client.recv(1024).decode()
    post_timestamp = datetime.now()
    post = [post_content,post_timestamp]
    if post_visibility == 'p':
        database.DATABASE[username]['posts_private'].append(post)
    else:   
        database.DATABASE[username]['posts_global'].append(post)
    socket_client.send("Post uploaded, check Timeline\n".encode())

def get_timeline(username,socket_client):
    response = 'Timeline: \n\n'
    my_posts = []
    for i in database.DATABASE[username]['posts_global']:
        my_posts.append(i)
    for i in database.DATABASE[username]['posts_private']:
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
    return
   
def search_user(username,socket_client,user_list):
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
    # search_result = search_result - np.array(database.DATABASE[username]['friends']) # delete client's friends
    
    for i in search_result:
        each = str(count+1) + ". " + i + "\n"
        response += each
        count+=1
    if(count == 0):
        response = "No results found"
        socket_client.send(response.encode())
    else:
        response += "Enter number to send friend request\n"
        socket_client.send(response.encode())
        friend_number = int(socket_client.recv(1024).decode())

        if username not in database.DATABASE[ search_result[friend_number-1] ]['pending_friend_requests']:       # check if already exists
            database.DATABASE[ search_result[friend_number-1] ]['pending_friend_requests'].append(username)

def get_friends_of_friends(username,socket_client):
    fof = []
    for i in database.DATABASE[username]['friends']:
        for j in database.DATABASE[i]['friends']:
            fof.append(j)
    fof = np.array(fof)
    fof = np.unique(fof)
    self_index = np.argwhere(fof==username)
    fof = np.delete(fof,self_index)         # delete self
    fof = list(fof)
    for i in database.DATABASE[username]['friends']:
        if(i in fof):
            fof.remove(i) # delete client's friends
    
    if(len(fof)!=0):
        response = "Results:\n"
        for i in range(len(fof)):
            each = str(i+1) + ". " + fof[i] + "\n"
            response += each
        response += "Enter number to send friend request\n"
        socket_client.send(response.encode())
        friend_number = int(socket_client.recv(1024).decode())
        if username not in database.DATABASE[ fof[friend_number-1] ]['pending_friend_requests']:     # check if already exists
            database.DATABASE[ fof[friend_number-1] ]['pending_friend_requests'].append(username)
    else:
        response = "Nothing Found\n Press any key to continue\n"
        socket_client.send(response.encode())

def see_friends(username,socket_client):
    friend_list = database.DATABASE[username]["friends"].copy()
    response = "Friend List: \n"

    friend_list.sort()    
    flag_end = False
    while(True):
        ten_friends = []
        for i in range(10):
            try:
                each = friend_list.pop(0)
                ten_friends.append(each)
                if(database.DATABASE[each]["is_online"]):
                    status = "ONLINE"
                else:
                    status = "Away" 
                response += str(i+1) + ". " + each + ":\t" + status + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Friend List\n"
        response += "0: Go Back\nEnter number to check Friend timeline friend\n"
        if(not flag_end):
            response+= "Enter 11 to see more friends\n"
        response+= "Enter Friend No. to see his Timeline\n"
        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        if(int(answer)>0 and int(answer)<11):
            r = "Showing Timeline of " + ten_friends[int(answer)-1] 
            r+= "\nPress Enter\n"
            socket_client.send(r.encode())
            get_timeline(ten_friends[int(answer)-1],socket_client)
            friend_list = database.DATABASE[username]["friends"].copy() 
            continue
        if(answer=="0" or flag_end):
            break
    return

def check_username(username, user_list):
    if(username in user_list):
        return(0)
    return(1)

def add_client(user_list,username,password):
    database.DATABASE[username] = {
                "Password": "",
                "is_online": False,
                "friends": [],
                "pending_friend_requests" : [],
                "posts_visible_friends": [],
                "posts_global": [],
                "posts_private": [],
                "messages": defaultdict(list)
                }
    database.DATABASE[username]["Password"] = password
    user_list.append(username)

    write_database("database.pkl")

def login(user_list,socket_client):
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
        if(check_username(username, user_list) == 0 and database.DATABASE[username]["Password"] == password):
            socket_client.send("Login Succesfull\nPress a key to continue".encode())
            return username
        else:
            socket_client.send("Invalid Username/Password\n Press any key to continue\n".encode())
            # time.sleep(0.5)
            user = login(user_list, socket_client)
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
                socket_client.send("Password does not match\n".encode())
            else:
                success = 1
        add_client(user_list,username,password)
        return username

def write_database(save_dir):
    f = open(save_dir, "wb")
    pickle.dump(database.DATABASE,f)
    f.close()

def delete_post(username,socket_client):
    response = 'Your Timeline\n\n'
    my_posts = []
    for i in database.DATABASE[username]['posts_global']:
        my_posts.append(i)
    for i in database.DATABASE[username]['posts_private']:
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
        response += "0: Go Back\nenter post number to delete\n"
        if(not flag_end):
            response+= "enter 5 to see next posts\n"
        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        
        try:
            post = four_posts[int(answer)-1]
            try:
                database.DATABASE[username]['posts_global'].remove(post)
            except:
                database.DATABASE[username]['posts_private'].remove(post)
            socket_client.send("Post successfully removed\n".encode())
            flag_end = True
        except:
            pass
        
        if(answer=="0" or flag_end):
            break

def remove_friend(username,socket_client):
    response = 'Your Friends\n'
    print(database.DATABASE)
    my_friends = database.DATABASE[username]["friends"].copy()
    # my_friends.sort()    

    flag_end = False
    while(True):
        ten_friends = []
        for i in range(10):
            try:
                each = my_friends.pop(0)
                ten_friends.append(each)
                response += str(i+1) + ". " + each + "\n"
            except Exception as e:
                flag_end = True
                print(e)
                continue
        if(flag_end):
            response += "End of Friend List\n"
        response += "0: Go Back\nenter number to remove friend\n"
        if(not flag_end):
            response+= "enter 11 to see more friends\n"
        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        
        if(int(answer)> 0 and int(answer)<11):
            f = ten_friends[int(answer)-1]
            database.DATABASE[username]['friends'].remove(f)
            database.DATABASE[f]['friends'].remove(username)
            socket_client.send("Friend successfully removed\n".encode())
            flag_end = True
        
        if(answer=="0" or flag_end):
            break

def chat_session(username, friend ,socket_client):
    my_messages = database.DATABASE[username]['messages'][friend].copy()
    my_messages = sorted(my_messages,key= lambda x: x[2],reverse=True) # sort by datetime
    print(my_messages)
    
    while(True):
        flag_end = False
        response = '\n'
        for i in range(4):
            try:
                each = my_messages.pop(0)
                response = response + "{}:\t".format(each[0])
                response = response + each[1] + "\n"
                response = response + str(each[2]) + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Messages\n"
        else:
            response += "1: See Previous Messages\n"
        response += "0: Go Back\n"
        response += "2: Send Message\nr: refresh"
        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        if(answer=="0"):
            break
        elif(answer=="r"):
            my_messages = database.DATABASE[username]['messages'][friend].copy()
            my_messages = sorted(my_messages,key= lambda x: x[2],reverse=True) # sort by datetime
            continue
        elif(answer=="2"):
            socket_client.send("Enter Message to send (Max. 100 char)\n".encode())
            msg = socket_client.recv(1024).decode()
            database.DATABASE[username]['messages'][friend].append([username,msg,datetime.now()])
            database.DATABASE[friend]['messages'][username].append([username,msg,datetime.now()])
            my_messages = database.DATABASE[username]['messages'][friend].copy()
            my_messages = sorted(my_messages,key= lambda x: x[2],reverse=True) # sort by datetime
            continue
                        
def messages_options(username, socket_client):
    friend_list = database.DATABASE[username]["friends"].copy()
    response = "Friend List: \n"

    friend_list.sort()    
    flag_end = False
    while(True):
        ten_friends = []
        for i in range(10):
            try:
                each = friend_list.pop(0)
                ten_friends.append(each)
                if(database.DATABASE[each]["is_online"]):
                    status = "ONLINE"
                else:
                    status = "Away" 
                response += str(i+1) + ". " + each + ":\t" + status + "\n"
            except:
                flag_end = True
                continue
        if(flag_end):
            response += "End of Friend List\n"
        response += "0: Go Back\n"
        if(not flag_end):
            response+= "Enter 11 to see more friends\n"
        response+= "Enter Friend No. to open chat\n"
        socket_client.send(response.encode())
        response = ''
        answer = socket_client.recv(1024).decode()
        if(int(answer)>0 and int(answer)<11):
            chat_session(username, ten_friends[int(answer)-1],socket_client)
            friend_list = database.DATABASE[username]["friends"].copy() 
            continue
        if(answer=="0" or flag_end):
            break
    return


