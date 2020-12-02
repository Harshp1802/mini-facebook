import time
import socket
import getpass

HOST = "10.0.0.1"
PORT = 12345

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect((HOST, PORT))
print("Connected to Server")

while 1:
    p, addr = socket_client.recvfrom(4096+1024)
    p = p.decode('utf-8')

    if(p == "Password: "):
        reply = getpass.getpass(prompt= "Password: ")
        socket_client.send(reply.encode())
        continue
    if(p == "Please Enter New Password: "):
        reply = getpass.getpass(prompt= "Please Enter New Password: ")
        socket_client.send(reply.encode())
        continue
    if(p == "Please Confirm New Password: "):
        reply = getpass.getpass(prompt="Please Confirm New Password: ")
        socket_client.send(reply.encode())
        continue
    if(p == "Thank you for using Mini-Face"):
        print(p)
        time.sleep(0.5)
        break
    
    print(p)

    reply = input()

    socket_client.send(reply.encode())

socket_client.close()
