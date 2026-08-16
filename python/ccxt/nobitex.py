# -*- coding: utf-8 -*-

from ccxt.base.exchange import Exchange
from ccxt.base.errors import AuthenticationError, OrderNotFound, NotSupported

class nobitex(Exchange):

    def describe(self):
        return self.deep_extend(super(nobitex, self).describe(), {
            'id': 'nobitex',
            'name': 'Nobitex',
            'countries': ['IR'],
            'rateLimit': 100,
            'certified': False,
            'has': {
                'CORS': None,
                'spot': True,
                'margin': False,
                'swap': False,
                'future': False,
                'fetchMarkets': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchOrderBook': True,
                'fetchOHLCV': False,
                'fetchTrades': True,
                'fetchBalance': True,
                'createOrder': True,
                'fetchOrder': True,
                'cancelOrder': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
                'fetchOrders': True,
                'fetchMyTrades': True,
                'fetchTradingFee': False,
                'fetchTradingFees': False,
            },
            'urls': {
                'logo': 'https://nobitex.ir/assets/images/logo.svg',
                'api': {
                    'public': 'https://apiv2.nobitex.ir',
                    'private': 'https://apiv2.nobitex.ir',
                },
                'www': 'https://nobitex.ir',
                'doc': ['https://apidocs.nobitex.ir'],
            },
            'api': {
                'public': {
                    'get': [
                        'market/stats',
                        'v2/trades/{symbol}',
                        'v3/orderbook/{symbol}',
                        'v2/orderbook/{symbol}',
                        'status',
                    ],
                },
                'private': {
                    'get': [
                        'users/profile',
                        'users/transactions-history',
                        'users/markets/favorite',
                    ],
                    'post': [
                        'users/wallets/list',
                        'market/orders/add',
                        'market/orders/cancel',
                        'market/orders/list',
                        'market/orders/update-status',
                        'users/accounts-add',
                    ],
                },
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': False,
            },
            'options': {
                'defaultType': 'spot',
            },
        })

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        
        if headers is None:
            headers = {}
            
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        if api == 'private':
            if not self.apiKey:
                raise AuthenticationError('Nobitex requires apiKey')
            
            headers['Authorization'] = 'Token ' + self.apiKey
                
            if method == 'POST':
                # Nobitex strictly requires JSON format for POST methods
                headers['Content-Type'] = 'application/json'
                body = self.json(query)
                
        elif method == 'GET':
            if query:
                url += '?' + self.urlencode(query)
                
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
    
    def fetch_markets(self, params={}):
        response = self.request('market/stats', 'public', 'GET', params)
        stats = self.safe_value(response, 'stats', {})
        keys = list(stats.keys())
        result = []

        for i in range(0, len(keys)):
            market_id = keys[i]
            parts = market_id.split('-')
            if len(parts) != 2:
                continue
                
            base_id = parts[0]
            quote_id = parts[1]
            base = self.safe_currency_code(base_id)
            quote = self.safe_currency_code(quote_id)
            symbol = base + '/' + quote
            
            result.append({
                'id': market_id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': base_id,
                'quoteId': quote_id,
                'type': 'spot',
                'spot': True,
                'active': True,
                'precision': {'amount': 8, 'price': 1},
                'limits': {
                    'amount': {'min': 0.00000001, 'max': None},
                    'price': {'min': 0.00000001, 'max': None},
                    'cost': {'min': None, 'max': None},
                },
                'info': stats[market_id],
            })
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = self.safe_string(market, 'symbol')
        
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_number(ticker, 'dayHigh'),
            'low': self.safe_number(ticker, 'dayLow'),
            'bid': self.safe_number(ticker, 'bestBuy'),
            'bidVolume': None,
            'ask': self.safe_number(ticker, 'bestSell'),
            'askVolume': None,
            'vwap': None,
            'open': self.safe_number(ticker, 'dayOpen'),
            'close': self.safe_number(ticker, 'latest'),
            'last': self.safe_number(ticker, 'latest'),
            'previousClose': None,
            'change': None,
            'percentage': self.safe_number(ticker, 'dayChange'),
            'average': None,
            'baseVolume': self.safe_number(ticker, 'volumeSrc'),
            'quoteVolume': self.safe_number(ticker, 'volumeDst'),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
        }
        response = self.request('market/stats', 'public', 'GET', self.extend(request, params))
        stats = self.safe_value(response, 'stats', {})
        market_id = market['baseId'] + '-' + market['quoteId']
        ticker = self.safe_value(stats, market_id, {})
        return self.parse_ticker(ticker, market)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        result = {}
        for symbol in self.markets:
            market = self.markets[symbol]
            info = self.safe_value(market, 'info')
            if info is not None:
                result[symbol] = self.parse_ticker(info, market)
        return result

    def parse_order_book(self, orderbook, symbol, timestamp=None):
        bids = self.safe_value(orderbook, 'bids', [])
        asks = self.safe_value(orderbook, 'asks', [])
        parsed_bids = []
        for bid in bids:
            if len(bid) >= 2:
                parsed_bids.append([self.parse_number(bid[0]), self.parse_number(bid[1])])
        parsed_asks = []
        for ask in asks:
            if len(ask) >= 2:
                parsed_asks.append([self.parse_number(ask[0]), self.parse_number(ask[1])])
        return {
            'symbol': symbol,
            'bids': parsed_bids,
            'asks': parsed_asks,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'nonce': None,
        }

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request_symbol = market['baseId'].upper() + market['quoteId'].upper()
        response = self.request('v3/orderbook/' + request_symbol, 'public', 'GET', params)
        timestamp = self.milliseconds()
        return self.parse_order_book(response, symbol, timestamp)

    def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        raise NotSupported('Nobitex API does not support OHLCV data.')

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_timestamp(trade, 'time')
        price = self.safe_number(trade, 'price')
        amount = self.safe_number(trade, 'volume')
        side = self.safe_string_lower(trade, 'type')
        if side not in ['buy', 'sell']:
            side = None
        cost = None
        if price is not None and amount is not None:
            cost = price * amount
        return {
            'id': self.safe_string(trade, 'id'),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': self.safe_string(market, 'symbol'),
            'order': None,
            'type': None,
            'side': side,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request_symbol = market['baseId'].upper() + market['quoteId'].upper()
        response = self.request('v2/trades/' + request_symbol, 'public', 'GET', params)
        trades = self.safe_value(response, 'trades', response)
        return self.parse_trades(trades, market, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.request('users/wallets/list', 'private', 'POST', params)
        wallets = self.safe_value(response, 'wallets', [])
        result = {'info': response}
        for wallet in wallets:
            currency_id = self.safe_string(wallet, 'currency')
            code = self.safe_currency_code(currency_id)
            free = self.safe_number(wallet, 'activeBalance')
            total = self.safe_number(wallet, 'balance')
            used = None
            if total is not None and free is not None:
                used = total - free
            result[code] = {'free': free, 'used': used, 'total': total}
        return self.safe_balance(result)

    def parse_order_status(self, status):
        statuses = {
            'open': 'open',
            'active': 'open',
            'done': 'closed',
            'filled': 'closed',
            'canceled': 'canceled',
            'cancelled': 'canceled',
        }
        return statuses.get(status, status)

    def parse_order(self, order, market=None):
        # اصلاح باگ سال 58 هزار با safe_integer
        timestamp = self.safe_integer(order, 'createdAt')
        return {
            'id': self.safe_string(order, 'id'),
            'clientOrderId': None,
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'status': self.parse_order_status(self.safe_string(order, 'status')),
            'symbol': self.safe_string(market, 'symbol'),
            'type': self.safe_string(order, 'type'),
            'timeInForce': None,
            'side': self.safe_string_lower(order, 'side'),
            'price': self.safe_number(order, 'price'),
            'amount': self.safe_number(order, 'amount'),
            'filled': self.safe_number(order, 'filledAmount'),
            'remaining': None,
            'cost': None,
            'average': None,
            'trades': [],
            'fee': None,
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'type': side,
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
            'amount': str(amount),
        }
        
        if type == 'limit':
            if price is not None:
                request['price'] = str(price)
        elif type == 'market':
            request['mode'] = 'market'
            
        response = self.request('market/orders/add', 'private', 'POST', self.extend(request, params))
        
        # بررسی ارورهای نوبیتکس
        status = self.safe_string(response, 'status')
        if status != 'ok':
            code = self.safe_string(response, 'code')
            message = self.safe_string(response, 'message')
            raise Exception(f"Nobitex Error: {code} - {message}")
            
        order = self.safe_value(response, 'order', response)
        return self.parse_order(order, market)

    def cancel_order(self, id, symbol=None, params={}):
        request = {'order': id, 'status': 'canceled'}
        response = self.request('market/orders/update-status', 'private', 'POST', self.extend(request, params))
        return response

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        orders = self.fetch_orders(symbol=symbol, params=params)
        for order in orders:
            if order['id'] == str(id):
                return order
        raise OrderNotFound('Order not found: ' + str(id))

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        request = {}
        if symbol:
            market = self.market(symbol)
            request['srcCurrency'] = market['baseId']
            request['dstCurrency'] = market['quoteId']
        response = self.request('market/orders/list', 'private', 'POST', self.extend(request, params))
        orders = self.safe_value(response, 'orders', [])
        return self.parse_orders(orders, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        request = {'status': 'open'}
        return self.fetch_orders(symbol, since, limit, self.extend(request, params))

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        request = {'status': 'done'}
        return self.fetch_orders(symbol, since, limit, self.extend(request, params))

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        request = {'status': 'done'}
        return self.fetch_orders(symbol, since, limit, self.extend(request, params))

    def fetch_trading_fee(self, symbol, params={}):
        raise NotSupported('Nobitex API does not support dynamic trading fees.')

    def fetch_trading_fees(self, params={}):
        raise NotSupported('Nobitex API does not support dynamic trading fees.')

    def fetch_profile(self, params={}):
        return self.request('users/profile', 'private', 'GET', params)

    def fetch_transactions_history(self, params={}):
        response = self.request('users/transactions-history', 'private', 'GET', params)
        return self.safe_value(response, 'transactions', [])

    def fetch_favorite_markets(self, params={}):
        return self.request('users/markets/favorite', 'private', 'GET', params)