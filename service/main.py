from time import sleep

from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

CLIENT = OSCClient('0.0.0.0', 3002)

def print_api(message, *args):
    print("Message from service : ", message)

if __name__ == '__main__':
    SERVER = OSCThreadServer()
    SERVER.listen('localhost', port=3000, default=True)
    SERVER.bind(b'/print_api', print_api)
    while True:
        sleep(1)
