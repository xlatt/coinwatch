#!/bin/env python
import ssl
import socket

main_coins  = ["BTC", "btc", "ETH", "eth"]
alt_coins   = ["HPB", "hpb"]

class Market:
    tcp_socket  = 0
    ssl_wraper  = 0
    address     = ""
    api_key     = ""
    secret_key  = ""

    def __init__(self, address, api_key, secret_key):
        self.address = address
        self.api_key = api_key
        self.secret_key = secret_key

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.address, 443))
        self.ssl_wraper = ssl.wrap_socket(self.tcp_socket, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)

    def __del__(self):
        self.ssl_wraper.close()

    # Relative to USD
    def rt_usd(self, coin):
        self.ssl_wraper.sendall("GET /api/v1/ticker?symbol="+coin+"_usd HTTP/1.1\r\nHost: "+self.address+"\r\nConnection: keep-alive\r\n\r\n")

        resp = self.ssl_wraper.recv(4096)
        if not resp:
            print("Failed to obtain info about "+coin)
            self.ssl_wraper.close()
            return

        print resp

    # Relative to BTC
    def rt_btc(self, coin):
        self.ssl_wraper.sendall("GET /api/v1/ticker?symbol="+coin+"_btc HTTP/1.1\r\nHost: "+self.address+"\r\nConnection: keep-alive\r\n\r\n")

        resp = self.ssl_wraper.recv(4096)
        if not resp:
            print("Failed to obtain info about "+coin)
            self.ssl_wraper.close()
            return

        print resp

    def coin_info(self, coin):
        if coin in main_coins:
            self.rt_usd(coin)
        elif coin in alt_coins:
            self.rt_btc(coin)

    def last_price(self, coin_info):
        raise "last price unimplemented"

m = Market("api.allcoin.com", "", "")
m.coin_info("btc")
m.coin_info("hpb")
