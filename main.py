import threading
import socket
import sys 
import json 
import time
import random

import udp
from config import seed, ip_seed, port_seed
from datetime import datetime
from pydantic import BaseModel

my_ip = None
my_port = None
udp_hole_time = 10


class Message(BaseModel):
    user_from: str
    user_to: str
    timestamp: str
    data_type: str
    data: str

    def new_message(self, user_from='', user_to='', timestamp='', data_type='', data=''):
        self.user_from = user_from
        self.user_to = user_to
        self.timestamp = timestamp
        self.data_type = data_type
        self.data = data


class Node:
    seed = seed
    peers = {}
    myid = ""
    udp_socket = {}
    api_receive_socket = {}
    api_translate_socket = {}
    keep_alive_socket = {}

    buffer = list()

    def rece(self):

        while 1:
            data, addr = udp.recembase(self.udp_socket)
            action = json.loads(data)
            print(action)
            # print(action["type"])
        #     self.dispatch(action, addr)
        # def dispatch(self, action,addr):
            if action['type'] == 'newpeer':
                print("A new peer is coming")
                self.peers[action['data']] = addr
                # print(addr)
                udp.sendJS(self.udp_socket, addr, {
                "type": 'peers',
                "data": self.peers
                })

            if action['type'] == 'peers':
                print("Received a bunch of peers")
                self.peers.update(action['data'])
                # introduce youself. 
                udp.broadcastJS(self.udp_socket, {
                    "type": "introduce",
                    "data": self.myid
                }, self.peers)

            if action['type'] == 'introduce':
                print("Get a new friend.")
                self.peers[action['data']] = addr

            if action['type'] == 'input':
                message = Message(user_from=udp.get_id(addr[0], self.peers),
                                  user_to='All',
                                  timestamp=str(datetime.now()),
                                  data_type=action['type'],
                                  data=action['data'])
                self.buffer.append(message.dict())
                print(action['data'])  

            if action['type'] == 'exit':
                if(self.myid == action['data']):
                #cannot be closed too fast.  
                    time.sleep(0.5) 
                    break
                    # self.udp_socket.close()
                value, key = self.peers.pop(action['data'])
                print(action['data'] + " is left.")
            
    def startpeer(self):
        udp.sendJS(self.udp_socket, self.seed, {
            "type": "newpeer",
            "data": self.myid
        })

    def send(self):
        while True:
            #msg_input = input("$:")
            data, addr = udp.recembase(self.api_receive_socket)
            msg_input = json.loads(data)['data']
            if msg_input == "/exit":
                udp.broadcastJS(self.udp_socket, {
                    "type": "exit",
                    "data": self.myid
                }, self.peers)
                break
            if msg_input == "/get_peers":
                print(self.peers)
                continue
            l = msg_input.split()
            if l[-1] in self.peers.keys():
                toA = self.peers[l[-1]]
                s = ' '.join(l[:-1]) 
                udp.sendJS(self.udp_socket, toA, {
                    "type": "input",
                    "data": s
                })
            else:
                udp.broadcastJS(self.udp_socket, {
                    "type": "input",
                    "data": msg_input
                }, self.peers)
                continue

    def api_server_handler(self):
        while True:
            data, addr = udp.recembase(self.api_translate_socket)
            udp.sendmbase(self.api_translate_socket, addr, udp.jsonify_mes_buf(self.buffer))
            self.buffer.clear()
            print(self.buffer)
            print(udp.jsonify_mes_buf(self.buffer))

    def keep_alive(self):
        time.sleep(udp_hole_time)
        addr = (ip_seed, port_seed)
        alive_message = {'type': 'keep_alive',
                         'data': 'I`m alive'}

        while True:
            time.sleep(udp_hole_time)
            udp.sendJS(self.udp_socket, addr, alive_message)


def main():
    global my_ip, my_port
    # определяем локальный ip адрес:
    my_ip = udp.extract_ip()
    my_port = random.randint(10000, 60000)  # Присвоение порта
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((my_ip, my_port))

    print(f'Адрес вашего сервера: {my_ip}:{my_port}')

    sock_receive_api = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Сокет для приёма сообщений от API сервера
    sock_receive_api.bind(('127.0.0.1', 55555))
    sock_translate_api = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Сокет для приёма сообщений от API сервера
    sock_translate_api.bind(('127.0.0.1', 44444))
    sock_keep_alive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    peer = Node()
    peer.myid = 'Dima'
    peer.udp_socket = udp_socket
    peer.api_receive_socket = sock_receive_api
    peer.api_translate_socket = sock_translate_api
    #peer.keep_alive_socket = sock_keep_alive
    # print(fromA, peer.myid)
    peer.startpeer()  # Отправляет сообщение о новом подключенном пире

    t1 = threading.Thread(target=peer.rece, args=())
    t2 = threading.Thread(target=peer.send, args=())
    t3 = threading.Thread(target=peer.api_server_handler, args=())
    t4 = threading.Thread(target=peer.keep_alive, args=())

    t1.start()
    t2.start()
    t3.start()
    t4.start()


if __name__ == '__main__':
    main()           

# usage:
# python main.py 8891 id1
# python main.py 8892 id2
# python main.py 8893 id3