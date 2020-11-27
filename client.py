import time
import socket

HOST = "127.0.0.1"
PORT = 12345

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect((HOST, PORT))
print("Connected to Server")

while 1:
    p, addr = socket_client.recvfrom(4096+1024)
    p = p.decode('utf-8')

    if(p=="Thank you for using Mini-Face"):
        print(p)
        time.sleep(0.5)
        break
    
    print(p)

    reply = input()

    socket_client.send(reply.encode())

socket_client.close()
