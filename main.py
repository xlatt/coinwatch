#!/bin/env python
import ssl
import socket
from enum import Enum

main_coins  = ["BTC", "btc", "ETH", "eth"]
alt_coins   = ["HPB", "hpb"]


# Query types for which QueryBuilder can build API queries
class QueryType(Enum):
    PRICE_TICKER = 1
    MARKET_DEPTH = 2


# Build API query for market
class QueryBuilder():

    # Build API query
    # Arguments:
    #   market - address on which market will respond for API query
    #   qtype  - defining which query should be build
    #   arg    - touple of variable length containig specific arguments for query
    # Return:
    #   query in string format
    def build(self, market, qtype, *arg):
        if qtype == QueryType.PRICE_TICKER:
            return "GET /api/v1/ticker?symbol="+arg[0]+"_"+arg[1]+" HTTP/1.1\r\nHost: "+market+"\r\nConnection: keep-alive\r\n\r\n"


# Represents market and holds functionality for comunincating with market
class Market:
    tcp_socket      = 0
    ssl_wraper      = 0
    address         = ""
    api_key         = ""
    secret_key      = ""
    market_query    = None


    def __init__(self, address, api_key, secret_key):
        self.address = address
        self.api_key = api_key
        self.secret_key = secret_key
        self.market_query = QueryBuilder()

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.address, 443))
        self.ssl_wraper = ssl.wrap_socket(self.tcp_socket, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)


    def __del__(self):
        self.ssl_wraper.close()

    # Send API query to market and parse response
    # Arguments:
    #   query - String query obtained from QueryBuilder.build()
    # Return:
    #   On sucess:  resp - Parsed response without HTTP headers
    #   On fail:    None
    def query_market(self, query):
        self.ssl_wraper.sendall(query)

        resp = self.ssl_wraper.recv(4096)
        if not resp:
            print("Market "+self.address+" did not respod for query: "+query)
            self.ssl_wraper.close()
            return None
        # todo strip http header and return
        print resp


    # Get currency info
    # API reference: https://api.allcoin.com/api/v1/ticker
    #
    # Arguments:
    #   coin - String containing 3 letter identifier of currency
    # Return:
    #   JSON formated currency info
    #   For more info see: https://www.allcoin.com/About/APIReference/
    def currency_info(self, coin):
        if coin in main_coins:
            q = self.market_query.build(self.address, QueryType.PRICE_TICKER, coin, "usd")
            self.query_market(q)
        elif coin in alt_coins:
            q = self.market_query.build(self.address, QueryType.PRICE_TICKER, coin, "btc")
            self.query_market(q)


    def last_price(self, coin_info):
        raise "last price unimplemented"


#######################
#        MAIN         #
#######################
m = Market("api.allcoin.com", "", "")
m.currency_info("btc")
m.currency_info("hpb")
