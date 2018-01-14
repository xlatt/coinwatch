#!/bin/env python
import ssl
import socket
import json
from enum import Enum

main_currency = ["BTC", "btc", "ETH", "eth"]
alt_currency  = ["HPB", "hpb"]


# Query types for which QueryBuilder can build API queries
class QueryType(Enum):
    PRICE_TICKER = 1
    MARKET_DEPTH = 2
    TRADE_SELL = 3   # amount api_key price sign symbol type
    TRADE_BUY = 4
    TRADE_CANCEL = 5


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
        elif qtype == QueryType.TRADE_SELL:
            return "POST /api/v1/trade\r\nHost: "+market+"\r\n\r\namount="+arg[0]+"&api_key="+arg[1]+"&price="+arg[2]+"&sign="+arg[3]+"&symbol="+arg[4]+"&type=sell"
        elif qtype == QueryType.TRADE_BUY:
            raise "QueryType.TRADE_BUY unimplementd"
        elif qtype == QueryType.TRADE_CANCEL:
            return "QueryType.TRADE_CANCEL unimplementd"


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
        self.ssl_wraper = ssl.wrap_socket(self.tcp_socket, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2)


    def __del__(self):
        self.ssl_wraper.close()


    # Send API query to market and parse response
    # Arguments:
    #   query - String query obtained from QueryBuilder.build()
    # Return:
    #   On sucess:  resp - Parsed response without HTTP headers
    #   On fail:    None
    def query_market(self, query):
        self.ssl_wraper.sendall(query.encode())

        resp = self.ssl_wraper.recv(4096).decode()
        if not resp:
            print("Market "+self.address+" did not respod for query: "+query)
            self.ssl_wraper.close()
            return None

        header_delim = resp.find("\r\n\r\n")
        payload = resp[header_delim+4:]
        return json.loads(payload)


    # Get currency info
    # API reference: https://api.allcoin.com/api/v1/ticker
    #
    # Arguments:
    #   cofi - Currency of Interest. For this currency we want statistics
    #   cotc - Currency to compare. Currency stats will be comapred against this currency
    #   both arguments cotains 3 letter identifier (btc, ltc, hpb, usd, ...)
    # Return:
    #   JSON parsed to python dictionary
    #   For more info see: https://www.allcoin.com/About/APIReference/
    def currency_info(self, cofi, ctoc):
        q = self.market_query.build(self.address, QueryType.PRICE_TICKER, cofi, ctoc)
        return self.query_market(q)

    # Get last price of currency from market.
    #
    # Argument:
    #   currency - three letter identifier of currency (btc, ltc, hpb, ...)
    # Return:
    #   Last price of currency compared to USD or Bitcoin. Values is float.
    def last_price(self, currency):
        info = None
        if currency in main_currency:
            info = self.currency_info(currency, "usd")
        elif currency in alt_currency:
            info = self.currency_info(currency, "btc")
        else:
            print("Unknow currency: "+currency)
            return None

        return info['ticker']['last']


    # Sell security at given price or with current price
    #
    # Arguments:
    #   what - Three letter symbol of currency which should be sold
    #   amount - amount of security to be sold
    #   at_price - price at which security should be sold. If 0 it will be sold with current price
    # Return:
    #   On sucess: Order id in string format
    #   On failure: None
    def sell(self, what, amount, at_price=0):
        if at_price == 0:
            at_price = self.last_price(what)
            if not at_price:
                return None

        # TODO sign quey with secret_key
        q = self.market_query.build(self.address, QueryType.TRADE_SELL, amount, self.api_key, at_price, "TODO sign", what)
        response = self.query_market(q)

        if not response or response['result'] == "false":
            return None
        else:
            return response['order_id']


    def buy(self):
        raise "buy unimplementd"


    def cancel(self, api_key, order_id, sign, symbol):
        raise "cancel unimplementd"



#######################
#        MAIN         #
#######################
m = Market("api.allcoin.com", "", "")

p = m.last_price("btc")
if p:
    print(p)

p = m.last_price("hpb")
if p:
    print(p)

m.last_price("dfsdf")
