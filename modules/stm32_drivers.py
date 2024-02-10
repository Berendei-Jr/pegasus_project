import os
import logging
import socket
import time

LED_STATUS_OFF = 0
LED_STATUS_ON = 1
LED_STATUS_BLINK_FAST = 2
LED_STATUS_BLINK_SLOW = 3

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
serv_sock.bind(('', 3333))
serv_sock.listen(10)
client_sock: None

def stm32_init():
    client_sock, client_addr = serv_sock.accept()
    logging.debug(f'Stm connected in {client_addr}')

def blink_led(state: int = 2):
    '''Start/stop LED blinking on STM32 board'''

    if (state == LED_STATUS_OFF):
        client_sock.sendall("l0")
    elif (state == LED_STATUS_ON):
        client_sock.sendall("l1")
    elif (state == LED_STATUS_BLINK_FAST):
        client_sock.sendall("lf")  
    elif (state == LED_STATUS_BLINK_SLOW):
        client_sock.sendall("ls")
    else:
        logging.debug(f'Error blinking state {state}')
        return
    data = client_sock.recv(1024)
    if (data != b'ok'):
        logging.debug(f'Error blinking file on stm32 {data}')
        return
    logging.debug(f'Blink led {state}')

def create_directory(dir_name: str):
    '''Create directory with given name'''

    client_sock.sendall(("m" + dir_name).encode("utf-8"))
    data = client_sock.recv(1024)
    if (data != b'ok'):
        logging.debug(f'Error creating dir on stm32 {data}')
        return

    logging.debug(f'Create directory {dir_name}')

def write_file(dir_name: str, filename: str, host_file_path: str):
    '''Copy host file to STM32 dir_name/filename'''

    client_sock.sendall(("o"+os.path.join(dir_name, filename)).encode("utf-8"))
    data = client_sock.recv(1024)
    if (data != b'ok'):
        logging.debug(f'Error creating file on stm32 {data}')
        return

    f = open(host_file_path, "rb")

    i = 0
    startTime = time.time()
    while (data := f.read(460)):
        client_sock.send(b'w'+data)
        i+=1
        # print(i)
        data = client_sock.recv(1024)
        if (data != b'ok'): logging.debug(f'Sending error {data}')
    logging.debug(f'Sending done. Spent time: {time.time()-startTime}s')

    f.close()
    client_sock.sendall("c".encode("utf-8"))
    data = client_sock.recv(1024)
    if (data != b'ok'):
        logging.debug(f'error closing file on stm32 {data}')
        return
    logging.debug(f'Writing {os.path.join(dir_name, filename)} from {host_file_path}')

def get_frame(path: str, i):
    '''Get frame from STM32 and write it on the given path'''
    return os.path.join(path, f'frame_{i}.jpg')
