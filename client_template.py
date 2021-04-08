# Heights sockets Ex. 2.7 template - client side
# THAT'S THE PROGRAMMER TRYING TO FIX THE PROBLEM

import socket

IP = "127.0.0.1"  # the ip of the server im connecting 2
PORT = 8820  # the kind of connection


def valid_request(request):
    if ('TAKE_SCREENSHOT' not in request) and ('SEND_FILE' not in request) \
            and ('DIR' not in request) and ('DELETE' not in request) \
            and ('COPY' not in request) and ('EXECUTE' not in request) \
            and ('EXIT' not in request):
        return False
    else:
        return True


def send_request_to_server(my_socket, request):
    # Send the request to the server. The length of the request and the request
    # Example: '04EXIT', '12DIR c:\cyber'
    num = len(request)
    my_socket.send(str(num) + request)


def handle_server_response(my_socket, request):
    # Receive response from server and handle it, according to the request
    response = my_socket.recv(1024)
    if 'SEND_FILE' not in request:
        print response
    else:  # the request was 'SEND_FILE'
        if 'no parameters..' in response \
                or 'The file/s you entered does not exist!' in response:
            print response
        else:  # if this message wasn't included in response, request is valid
            # we're gonna have to receive the file in parts
            response = [response]
            while 'DONE' not in response[-1]:  # until it received 'done' msg
                response.append(my_socket.recv(1024))
            # now i need to remove the last response, 'DONE' msg.
            response = response[:-1]
            # FINDING THE TYPE OF FILE:
            request = request.split('.')
            file_type = request[1]
            if file_type == 'jpg' or file_type == 'png':
                write = 'wb'
            else:
                write = 'w'

            with open(r'd:\CLIENT_FILE.' + file_type, write) as wf:
                for char in response:
                    wf.write(char)
            print 'successful omg im so exited'


def main():
    # open socket with the server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    # print instructions
    print('Welcome to remote computer application. Available commands are:')
    print('TAKE_SCREENSHOT\nSEND_FILE\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')

    done = False
    # loop until user requested to exit
    while not done:
        try:
            request = raw_input("Please enter command:\n")
        except EOFError:
            request = 'what?? error in the input'

        if valid_request(request):
            send_request_to_server(my_socket, request)
            handle_server_response(my_socket, request)
            if request == 'EXIT':
                done = True
        else:
            print 'request is not valid, try again'
    my_socket.close()


if __name__ == '__main__':
    main()
