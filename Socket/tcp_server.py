import socket
import threading 

#Change your IP address
IP = "127.0.0.0"
PORT = 1234

#Handle request from client
def client_handler(client_socket):
    try:
        with client_socket as socket:
            request = socket.recv(1024)
            print(f'[*] Received: {request.decode("utf-8")}')
            socket.send(b'ACK')
    except:
        print("Error handle")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Pass IP address and port that we want server to listen
    server.bind((IP, PORT))
    #Maximum connection is 5
    server.listen(5)
    print(f'[*] Server listen on: {IP}:{PORT}')

    while True:
        #Get client socket and address from client
        client, address = server.accept()
        print(f"[*] Accept connect from {address[0]}:{address[1]}")
        #Multiprocessing, 
        #You can process multiple request from difference user in a dependence way
        client_handle = threading.Thread(target=client_handler, args=(client,))
        client_handle.start()
if __name__ == '__main__':
    main()
