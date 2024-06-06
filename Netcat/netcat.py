import argparse #module support for command line interface
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

#Class socket object
class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Set the socket option
        #Set option at the socket level, specify the level argument as SOL_SOCKET
        #SO_REUSEADDR  allow reusing of the local address
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        #If setting up a listener, call listen method
        #Else call send method
        if self.args.listen:
            self.listen()
        else:
            self.send()
    
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        #self.socket.connect(("172.20.10.2", 1234))
        #If have buffer, send it to target
        if self.buffer:
            self.socket.send(self.buffer)
        #Hand with CTRL + C command 
        try:
            while True:
                recv_len = 1
                response = ''
                #Read data from socket until no more data available
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    #If no more data, break
                    if recv_len < 4096:
                        break
                #Print response and pause to get input
                if response:
                    print(response)
                    buffer = input("> ")
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("User terminated.")
            self.socket.close()
            sys.exit()

    def listen(self):
        print(f"Server listen on {self.args.target}:{self.args.port}")
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            #Accept connect from client
            client_socket, client_add = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket, )
            )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else: 
                    break
            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            message = f'Save file {self.args.upload}'
            client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'Stone: #> ')
                    while('\n' not in cmd_buffer.decode()):
                        cmd_buffer += client_socket.recv(64)
                    print(f"Command {cmd_buffer.decode()}")
                    response = execute(cmd_buffer.decode()) #Error
                    print("Oke execute")
                    if(response):
                        client_socket.send(response.encode())
                    cmd_buffer=b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    else:
        #Execute command on the target then return again result
        #shplex.split(cmd) split string command to list argument. Example ls -l to ["ls", "-l"]
        #stderr=subprocess.STDOUT to capture standard error in the result
        output = subprocess.check_output(shlex.split(cmd), #Error is here
                                         stderr=subprocess.STDOUT,
                                         shell=True)
        return output.decode()

if __name__ == "__main__":
    #Define container for argument specification and option that has in Netcat tool
    parser = argparse.ArgumentParser(
        description= "Stone Netcat Tool",
        #Indicate that description and epilog are already correctly and should not ne line-wrapped
        formatter_class = argparse.RawDescriptionHelpFormatter,
        #Display when Users invokes --help command
        epilog=textwrap.dedent("""Example:
            netcat.py -t 192.168.1.100 -p 1234 -l -c #Command Shell
            netcat.py -t 192.168.1.100 -p 1234 -l -u=mytest.txt #Upload to file
            netcat.py -t 192.168.1.100 -p 1234 -l -e=\"cat /etc/passwd\" #Execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.100 -p 1234 # echo text to server port 1234
            netcat.py -t 192.168.1.100 -p 1234 # connect to server
        """))
    #Attack individual argument specification to the parser
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=1234, help='specified port')
    parser.add_argument('-t', '--target', default='172.20.10.2', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    #Run the parser(phân tích cú pháp) an places the extracted data in a argparse.Namespace
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        #Interactive input
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()
