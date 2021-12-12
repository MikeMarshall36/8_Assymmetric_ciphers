import socket
from threading import Thread
from binascii import hexlify, unhexlify
from itertools import cycle
from time import sleep

def incription(incript, key):
    cipher = xor_str(incript, key)
    return (hexlify(cipher.encode())).decode()

def decription(incript, key):
    incript = (unhexlify(incript.encode())).decode()
    return xor_str(incript, key)

def xor_str(a, b):
    return ''.join([chr(ord(x) ^ ord(y)) for x, y in zip(a, cycle(b))])


def generation(key_prim, key_publ_m):
    msg = str(key_publ_m)
    sleep(0.1)
    sock.send(msg.encode('utf-8'))
    try:
        key_publ_s = int(sock.recv(1024))
    except ValueError:
        print("Error: KeyNotCorrect")
        global flag
        flag = False
        return (False)
    key_part_m = calc_key(key_publ_m, key_prim, key_publ_s)
    msg = str(key_part_m)
    sleep(0.1)
    sock.send(msg.encode('utf-8'))
    key_part_s = int(sock.recv(1024))
    key_full_m = calc_key(key_part_s, key_prim, key_publ_s)
    with open('key' + str(pr) + '.txt', 'w') as f:
        f.write(str(key_full_m))
    return key_full_m

def calc_key(key_g, key_ab, key_p):
    return key_g ** key_ab % key_p


def recever():
    global flag
    while flag:
        try:
            inp = decription(sock.recv(1024).decode('utf-8'), key_full_s)
            if inp == 'exit':
                print('server out')
                flag = False
            else:
                print('server:', inp)
        except OSError:
            flag = False

flag = True

sock = socket.socket()
pr = 5170
try:
    sock.bind(('', pr))
except OSError:
    print('Addr error')
    flag = False
if flag:
    sock.setblocking(1)
    port_num = 53480
    try:
        sock.connect(('localhost', port_num))
        print('connection with server')
    except ConnectionRefusedError:
        print('Server not online')
        flag = False
if flag:
    try:
        file = open('key' + str(pr) + '.txt', 'r')
        key_full_s = file.read()
        file.close()
    except:
        key_prim = 199
        key_publ_m = 197
        i = 0
        key_full_s = str(generation(key_prim, key_publ_m))

if flag:
    port = decription(sock.recv(1024).decode('utf-8'), key_full_s)
    sock.close()
if flag:
    sock = socket.socket()
    sock.bind(('', pr))
    sock.setblocking(1)
    sock.connect(('localhost', int(port)))
    stream = Thread(target=recever)
    stream.start()
    while flag:
        msg = input('input your message: ')
        if msg == 'exit':
            flag = False
        try:
            msg = incription(msg, key_full_s)
            sock.send(msg.encode('utf-8'))
        except ConnectionResetError:
            flag = False
sock.close()