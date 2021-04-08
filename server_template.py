# Heights sockets Ex. 2.7 template - server side
# THAT'S THE GUY WITH THE PROBLEM

import socket

from PIL import ImageGrab  # for the screenshot
import glob  # for the dir
import os  # for removing something
import shutil  # for copying
import subprocess  # for execution

IP = "0.0.0.0"  # the ip of the costumer- any ip, anyone who asks
PORT = 8820  # the kind of connection

'''
number of params each command requires:
TAKE_SCREENSHOT: 1  *if you don't specify a file name,
                    ill call it 'CLIENT SCREENSHOT.png'
SEND_FILE: 1
DIR: 1
DELETE: 1
COPY: 2
EXECUTE: 1
EXIT: 0
'''


def receive_client_request(client_socket):
    # Example: 12DIR c:\cyber as input
    # will result in command = 'DIR', params = 'c:\cyber'
    data = client_socket.recv(1024)
    # removing the numbers, they're useless:
    i = 0
    for i in range(len(data)):
        if not data[i].isdigit():
            break  # I save the index where the numbers end
    result = data[i:]
    splitted = result.split(' ')
    request = splitted[0]
    splitted.pop(0)
    params = ' '.join(splitted)  # whats left of the data is the parameters
    return request, params


def check_client_request(command, params):
    # the client's code had already checked the msg include 1 of the commands
    valid = True
    right_error_msg = 0
    error_msg = ['what is that command..?',
                 'no parameters..',
                 'The file/s you entered does not exist!',
                 'The directory you entered does not exist!',
                 'BYE']
    path = params

    if command == 'EXIT':
        valid = False
        right_error_msg = 4

    elif params == '':
        valid = False
        right_error_msg = 1
    # checking if the path / file/s exists

    elif not os.path.exists(path):

        # checking if this is a 2-paths var (splitted with ' ')
        if command == 'COPY':
            try:
                maybecopy = os.path.exists(path.split(' ')[0]) \
                            and os.path.exists(path.split(' ')[1])
            except IOError and IndexError:
                maybecopy = False
            if not maybecopy:  # if maybecopy == False
                valid = False
                right_error_msg = 2

        elif command == 'TAKE_SCREENSHOT':
            path = path.split('\\')[0]
            path = ''.join(path)
            if not os.path.exists(path):
                path = path.split('/')[0]
                path = ''.join(path)
                if not os.path.exists(path):
                    valid = False
                    right_error_msg = 2
                    # checking if the filetype is supported
                    filetype = path.split('.')[1]
                    if filetype != 'png' and filetype != 'jpg':
                        valid = False
                        right_error_msg = 2
            else:  # the path is k
                # checking if the filetype is supported
                filetype = path.split('.')[1]
                if filetype != 'png' and filetype != 'jpg':
                    valid = False
                    right_error_msg = 2
        elif command == 'EXECUTE':
            pass
        else:
            valid = False
            right_error_msg = 2

    return valid, error_msg[right_error_msg]


def handle_client_request(command, params):
    # sending the correct method
    if command == 'TAKE_SCREENSHOT':
        return take_screenshot(params)
    elif command == 'SEND_FILE':
        return send_file(params)
    elif command == 'DIR':
        return diri(params)
    elif command == 'DELETE':
        return delete(params)
    elif command == 'COPY':
        return copy(params)
    elif command == 'EXECUTE':
        return execute(params)


def take_screenshot(download2):
    im = ImageGrab.grab()  # !!!
    print 'grabbed'
    try:
        im.save(download2)  # !!!
    except ValueError:  # the path doesnt exist
        try:  # maybe the client just didn't specify the filename, WORKS
            lastpath = download2 + 'CLIENT_SCREENSHOT.png'
            im.save(lastpath)
        except Exception, e:
            return str(e)
    return 'successful :\')'


def send_file(filey):
    if '.' not in filey:
        return 'don\'t try to send a directory pls'
    file_type = filey.split('.')[1]
    if file_type == 'jpg' or file_type == 'png':
        read = 'rb'
    else:
        read = 'r'
    with open(filey, read) as rf:
        data = rf.read()
        lines = []
        for line in data:
            lines.append(line)
        print 'finished reading'
    return lines


def diri(dir2sho):
    show = dir2sho + '*.*'
    # what comes after the . means types of file i wanna show
    files_list = glob.glob(show)  # !!!
    return str(files_list)


def delete(dir2del):
    os.remove(dir2del)  # !!!
    return 'successful :\')'


def copy(copys):
    copys = copys.split(' ')
    try:
        shutil.copy(copys[0], copys[1])
    except IOError and IndexError, e:
        # no such file exists (either one of them)
        return str(e)
    return 'successful :\')'


def execute(calling):
    try:
        subprocess.call(calling)
    except Exception, e:
        return e
    return 'successful :\')'


def send_response_to_client(response, client_socket):
    # The protocol should be able to handle short responses as well as files
    client_socket.send(response)
    return 'successful :)'


def main():
    # open socket with client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()

    # handle requests until user asks to exit
    done = False
    while not done:
        command, params = receive_client_request(client_socket)
        print 'command: ' + command
        print 'params: ' + str(params) + '\n'
        valid, error_msg = check_client_request(command, params)
        if command == 'EXIT':
            done = True
        if valid:
            response = handle_client_request(command, params)

            if type(response) == str:  # the method returned a string
                send_response_to_client(response, client_socket)
            elif type(response) == list:
                # the method returned a list, its SEND_FILE
                for line in response:  # sending the file
                    send_response_to_client(line, client_socket)
                send_response_to_client('DONE', client_socket)
                print 'finished sending'
            else:
                send_response_to_client('??' + str(type(response)),
                                        client_socket)
        else:
            print 'server said: not valid'  # the validation test has failed
            send_response_to_client(error_msg, client_socket)

    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    main()
