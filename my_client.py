import socket


def send_to_socket(data, socket_ip: str, socket_port: int, wait_for_answer=False):
    test_socket_ip = (socket_ip, socket_port)
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.sendto(str(data).encode(), test_socket_ip)
    if wait_for_answer:
        data = sock.recvfrom(1024)
        sock.close()
        return data
    return


send_to_socket('test', '83.239.95.114', 46970, wait_for_answer=True)
