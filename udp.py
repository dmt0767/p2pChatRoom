import socket
import threading
import sys
import json
# send string , to address.
from config import seed, port_seed, ip_seed
from time import sleep


def extract_ip(manual=False):
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    manual_ip = "10.17.0.203"
    if manual:
        return manual_ip
    else:
        try:
            st.connect(('10.255.255.255', 1))
            IP = st.getsockname()[0]
        except Exception:
            IP = manual_ip
        finally:
            st.close()
    return IP


def get_id(ip, d: dict):
    print(d)
    for key in d:
        if d[key][0] == ip:
            return key
    return 'None'


def jsonify_mes_buf(buffer: list):
    '''
    ans = dict()
    for i, message in enumerate(buffer):
        ans[i] = message
    '''

    return json.dumps({'messages': buffer})


def sendmbase(udp_socket, toA, message ):
    udp_socket.sendto(message.encode(),(toA[0],toA[1]))


# receive message, 
# return message, and addr. 
def recembase(udp_socket):
    data, addr = udp_socket.recvfrom(1024)
    return data.decode(), addr 


def sendJS(udp_socket,toA,message):
    sendmbase(udp_socket, toA, json.dumps(message))


def broadcastms(udp_socket,message, peers):
    for p in peers.values():
        sendmbase(udp_socket,p,message)


def broadcastJS(udp_socket,message, peers):
    for user_id, ip in zip(peers.keys(), peers.values()):
        if user_id == 'Server':
            ip = (ip_seed, port_seed)
            sendJS(udp_socket, ip, message)


def rece(udp_socket):
    while 1:
        data,addr = recembase(udp_socket)
        print(data)


def send(udp_socket):
    while 1:
        msg = input("please input message and port:")
        l = msg.split()
        port = int(l[-1])
        s = ' '.join(l[:-1])
        toA = ('127.0.0.1', port)
        sendmbase(udp_socket, toA, s)


def main():
    
    port = int(sys.argv[1]) #从命令行获取端口号
    fromA = ("127.0.0.1", port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((fromA[0],fromA[1]))
    t1 = threading.Thread(target=rece, args=(udp_socket,))
    t2 = threading.Thread(target=send, args=(udp_socket,))
    t1.start()
    t2.start()
 
 
if __name__ == '__main__':
    main()        

# usage:
# python p2pUdp.py 10001 
# python p2pUdp.py 10002
# hello 10001
# world 10002 