import socket

def input_server():
    #Enter your Ip address server
    target_host = input("Enter your target domain/IP address server: ").strip()
    port = int(input("Enter number port: ").strip())
    return target_host, port

if __name__ == "__main__":
    target_host, target_port = input_server()
    #Create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Connect to client
    client.connect((target_host, target_port))
    #Create the HTTP request with the user-provided hostname
    request = f"\r\nGET / HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
    #Send some data
    client.send(request.encode())
    #Receive some data
    response = client.recv(4096)

    print(response.decode())
    client.close()
