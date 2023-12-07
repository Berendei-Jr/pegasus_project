import os
import logging

def blink_led(state: bool = True):
    '''Start/stop LED blinking on STM32 board'''
    logging.debug(f'Blink led {state}')
    pass

def create_directory(dir_name: str):
    '''Create directory with given name'''

    logging.debug(f'Create directory {dir_name}')
    pass

def write_file(dir_name: str, filename: str, host_file_path: str):
    '''Copy host file to STM32 dir_name/filename'''
    logging.debug(f'Writing {os.path.join(dir_name, filename)} from {host_file_path}')

def get_frame(path: str, i):
    '''Get frame from STM32 and write it on the given path'''
    
    return os.path.join(path, f'frame_{i}.jpg')
