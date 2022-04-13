import threading
import socket
import sys
import json
import time
import random

import udp
from config import seed, port_seed, ip_seed
from datetime import datetime
from pydantic import BaseModel

from Crypto.PublicKey import RSA
code = 'army trooper'
key = RSA.generate(2048)

encrypted_key = key.exportKey(
    passphrase=code,
    pkcs=8,
    protection="scryptAndAES128-CBC"
)  # Приватный ключ

public_key = key.publickey().exportKey()  # Публичный ключ


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

    buffer = list()

    def rece(self):

        while 1:
            data, addr = udp.recembase(self.udp_socket)
            action = json.loads(data)
            print(action)

            if action['type'] == 'keep_alive':
                print(f'{addr} is alive!')
            if action['type'] == 'newpeer':
                print("A new peer is coming")
                self.peers[action['data']] = (addr, action['public_key'])
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
                    "data": self.myid,
                    "public_key": public_key.decode()
                }, self.peers)

            if action['type'] == 'introduce':
                print("Get a new friend.")
                self.peers[action['data']] = (addr, action['public_key'])

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
                    # cannot be closed too fast.
                    time.sleep(0.5)
                    break
                    # self.udp_socket.close()
                value, key = self.peers.pop(action['data'])
                print(action['data'] + " is left.")

    def startpeer(self):
        udp.sendJS(self.udp_socket, self.seed, {
            "type": "newpeer",
            "data": self.myid,
            "public_key": public_key.decode()
        })

    def send(self):
        while True:
            msg_input = input("$:")
            #data, addr = udp.recembase(self.api_receive_socket)
            #msg_input = json.loads(data)['data']
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


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((ip_seed, port_seed))

    print(f'Адрес вашего сервера: {ip_seed}:{port_seed}')

    sock_receive_api = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Сокет для приёма сообщений от API сервера
    sock_receive_api.bind(('127.0.0.1', 55556))
    sock_translate_api = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Сокет для приёма сообщений от API сервера
    sock_translate_api.bind(('127.0.0.1', 44445))

    peer = Node()
    peer.myid = 'Server'
    peer.udp_socket = udp_socket
    peer.api_receive_socket = sock_receive_api
    peer.api_translate_socket = sock_translate_api
    # print(fromA, peer.myid)
    peer.startpeer()  # Отправляет сообщение о новом подключенном пире

    t1 = threading.Thread(target=peer.rece, args=())
    t2 = threading.Thread(target=peer.send, args=())
    t3 = threading.Thread(target=peer.api_server_handler, args=())

    t1.start()
    t2.start()
    t3.start()


if __name__ == '__main__':
    main()
