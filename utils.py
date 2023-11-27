import logging
import socket

def get_logger(name:str) :
    return logging.getLogger(f"[{socket.gethostname()}]{name}")

#The logger's name is constructed by formatting a string with the hostname obtained from socket.gethostname() and the provided name parameter.