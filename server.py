from contextlib import closing
from threading import Thread
import socket
import csv
from binascii import hexlify, unhexlify
from itertools import cycle
from time import sleep

def encodeing(incription, key):
    cipher = xor_str(incription, key)
    return (hexlify(cipher.encode())).decode()

def decoding(incription, key):
    incription = (unhexlify(incription.encode())).decode()
    return xor_str(incription, key)

def xor_str(a, b):
    return ''.join([chr(ord(x) ^ ord(y)) for x, y in zip(a, cycle(b))])

def openport_detector():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('', 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]

def generation(key_prim, key_publ_m):
    key_publ_s = int(conn.recv(1024))
    if check(key_publ_s):
        msg = str(key_publ_m)
        sleep(0.1)
        conn.send(msg.encode('utf-8'))
    else:
        print("Error: KeyNotCorrect")
        global flag
        flag = False
        return (False)

    key_part_s = int(conn.recv(1024))
    key_part_m = calc_key(key_publ_s, key_prim, key_publ_m)
    msg = str(key_part_m)
    sleep(0.1)
    conn.send(msg.encode('utf-8'))

    key_full_m = calc_key(key_part_s, key_prim, key_publ_m)
    with open('server_key' + str(addr) + '.txt', 'w') as f:
        f.write(str(key_full_m))
    return key_full_m

def calc_key(key_g, key_ab, key_p):
    return key_g ** key_ab % key_p

def reciver():
    global flag
    while flag:
        try:
            inp = decoding(conn.recv(1024).decode('utf-8'), key_full_m)
            if inp == 'exit':
                print('client out')
                flag = False
            else:
                print('client:', inp)
        except OSError:
            flag = False

def check(key_publ_s):
    i = False
    with open('key_list.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] == str(key_publ_s):
                i = True
    return i

flag = True
sock = socket.socket()
num = 53480
print('Your port:', num)
try:
    sock.bind(('', num))
except OSError:
    num = openport_detector()
    print('Ошибка. Выбранный вами код сервера уже занят, код сервера будет изменён автоматически. Новый код: ', num)
    sock.bind(('', num))

print('Server activate')
sock.listen(3)
i = 0
conn, addr = sock.accept()
try:
    file = open('keyserv' + str(addr) + '.txt', 'r')
    key_full_m = file.read()
    file.close()
except:
    key_publ_m = 151
    key_prim = 157

    key_full_m = str(generation(key_prim, key_publ_m))

if flag:
    print('user addr:', addr)
    port = openport_detector()
    msg = encodeing(str(port), key_full_m)
    conn.send(msg.encode('utf-8'))

    conn.close()
if flag:
    sock = socket.socket()
    sock.bind(('', int(port)))
    sock.listen(3)
    addr2 = ''
    while True:
        conn, addr2 = sock.accept()
        if addr2 == addr:
            break
        else:
            conn.close()
    stream = Thread(target=reciver())
    stream.start()
    while flag:
        msg = input('input your message: ')
        if msg == 'exit':
            flag = False
        try:
            msg = encodeing(msg, key_full_m)
            conn.send(msg.encode('utf-8'))
        except ConnectionResetError:
            flag = False

conn.close()