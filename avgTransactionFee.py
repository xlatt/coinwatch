import ssl
import socket


class ConnectToTransactionFeeServer:
    tcp_socket = 0
    ssl_wrapper = 0
    address = ""
    api_key = ""
    secret_key = ""

    def __init__(self, address):
        self.address = address

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.address,443))
        self.ssl_wrapper = ssl.wrap_socket(self.tcp_socket, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)

    def __del__(self):
        self.ssl_wrapper.close()
