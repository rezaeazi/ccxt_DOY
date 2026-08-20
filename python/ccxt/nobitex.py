from ccxt.base.exchange import Exchange
from ccxt.base.errors import AuthenticationError, OrderNotFound, NotSupported

class nobitex(Exchange):
    def describe(self):
        return self.deep_extend(super(nobitex, self).describe(), {
            'id': 'nobitex', 'name': 'Nobitex', 'countries': ['IR'], 'rateLimit': 100, 'certified': False,
            'has': {
                'CORS': None, 'spot': True, 'margin': False, 'swap': False, 'future': False,
                'fetchMarkets': True, 'fetchTicker': True, 'fetchTickers': True, 'fetchOrderBook': True,
                'fetchOHLCV': False, 'fetchTrades': True, 'fetchBalance': True, 'createOrder': True,
                'fetchOrder': True, 'cancelOrder': True, 'fetchOpenOrders': True, 'fetchClosedOrders': True,
                'fetchOrders': True, 'fetchMyTrades': True, 'fetchTransactions': True,
                'fetchTradingFee': False, 'fetchTradingFees': False,
            },
            'urls': {'logo': 'https://nobitex.ir/assets/images/logo.svg', 'api': {'public': 'https://apiv2.nobitex.ir', 'private': 'https://apiv2.nobitex.ir'}, 'www': 'https://nobitex.ir', 'doc': ['https://apidocs.nobitex.ir']},
            'api': {
                'public': {'get': ['market/stats', 'v2/trades/{symbol}', 'v3/orderbook/{symbol}', 'v2/orderbook/{symbol}', 'status']},
                'private': {
                    'get': ['users/profile', 'users/transactions-history', 'users/markets/favorite'],
                    'post': ['users/wallets/list', 'market/orders/add', 'market/orders/cancel', 'market/orders/list', 'market/orders/update-status', 'users/accounts-add']
                }
            },
            'requiredCredentials': {'apiKey': True, 'secret': False},
            'options': {'defaultType': 'spot'}
        })

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if headers is None: headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        if api == 'private':
            if not self.apiKey: raise AuthenticationError('Nobitex requires apiKey')
            headers['Authorization'] = 'Token ' + self.apiKey
            if method == 'POST': headers['Content-Type'] = 'application/json'; body = self.json(query)
        elif method == 'GET':
            if query: url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def fetch_markets(self, params={}):
        response = self.request('market/stats', 'public', 'GET', params)
        stats = self.safe_value(response, 'stats', {})
        result = []
        for id, market_data in stats.items():
            parts = id.split('-')
            if len(parts) != 2: continue
            base, quote = parts[0], parts[1]
            result.append({
                'id': id, 'symbol': base + '/' + quote, 'base': base, 'quote': quote,
                'baseId': base, 'quoteId': quote, 'type': 'spot', 'spot': True, 'active': True,
                'precision': {'amount': 8, 'price': 1},
                'limits': {'amount': {'min': 0.00000001, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': None, 'max': None}},
                'info': market_data
            })
        return result

    def parse_ticker(self, ticker, market=None):
        ts = self.milliseconds()
        return self.safe_ticker({
            'symbol': self.safe_string(market, 'symbol'), 'timestamp': ts, 'datetime': self.iso8601(ts),
            'high': self.safe_number(ticker, 'dayHigh'), 'low': self.safe_number(ticker, 'dayLow'),
            'bid': self.safe_number(ticker, 'bestBuy'), 'ask': self.safe_number(ticker, 'bestSell'),
            'last': self.safe_number(ticker, 'latest'), 'close': self.safe_number(ticker, 'latest'),
            'baseVolume': self.safe_number(ticker, 'volumeSrc'), 'quoteVolume': self.safe_number(ticker, 'volumeDst'),
            'info': ticker
        }, market)

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.request('market/stats', 'public', 'GET', self.extend({'srcCurrency': market['baseId'], 'dstCurrency': market['quoteId']}, params))
        return self.parse_ticker(self.safe_value(self.safe_value(response, 'stats', {}), market['baseId'] + '-' + market['quoteId'], {}), market)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        result = {}
        for s, m in self.markets.items():
            if self.safe_value(m, 'info') is not None: result[s] = self.parse_ticker(m['info'], m)
        return result

    def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        raise NotSupported('Nobitex API does not support OHLCV data.')

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.request('users/wallets/list', 'private', 'POST', params)
        result = {'info': response}
        for w in self.safe_value(response, 'wallets', []):
            code = self.safe_currency_code(self.safe_string(w, 'currency'))
            total = self.safe_number(w, 'balance')
            free = self.safe_number(w, 'activeBalance')
            result[code] = {'free': free, 'used': (total - free if total is not None and free is not None else None), 'total': total}
        return self.safe_balance(result)

    def parse_order_status(self, status):
        return {'open':'open','active':'open','done':'closed','filled':'closed','canceled':'canceled','cancelled':'canceled'}.get(status, status)

    def parse_order(self, order, market=None):
        ts = self.safe_integer(order, 'createdAt')
        return self.safe_order({
            'id': self.safe_string(order, 'id'), 'clientOrderId': None, 'info': order, 'timestamp': ts, 'datetime': self.iso8601(ts),
            'status': self.parse_order_status(self.safe_string(order, 'status')), 'symbol': self.safe_string(market, 'symbol'),
            'type': self.safe_string(order, 'type'), 'side': self.safe_string_lower(order, 'side'), 'price': self.safe_number(order, 'price'),
            'amount': self.safe_number(order, 'amount'), 'filled': self.safe_number(order, 'filledAmount')
        }, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        m = self.market(symbol)
        req = {'type': side, 'srcCurrency': m['baseId'], 'dstCurrency': m['quoteId'], 'amount': str(amount)}
        if type == 'limit' and price is not None: req['price'] = str(price)
        elif type == 'market': req['mode'] = 'market'
        resp = self.request('market/orders/add', 'private', 'POST', self.extend(req, params))
        if self.safe_string(resp, 'status') != 'ok': raise Exception(f"Nobitex Error: {self.safe_string(resp, 'code')} - {self.safe_string(resp, 'message')}")
        return self.parse_order(self.safe_value(resp, 'order', resp), m)

    def cancel_order(self, id, symbol=None, params={}):
        return self.request('market/orders/update-status', 'private', 'POST', self.extend({'order': id, 'status': 'canceled'}, params))

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        m = self.market(symbol) if symbol else None
        req = {}
        if m: req.update({'srcCurrency': m['baseId'], 'dstCurrency': m['quoteId']})
        return self.parse_orders(self.safe_value(self.request('market/orders/list', 'private', 'POST', self.extend(req, params)), 'orders', []), m, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders(symbol, since, limit, self.extend({'status': 'open'}, params))
    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders(symbol, since, limit, self.extend({'status': 'done'}, params))
    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders(symbol, since, limit, self.extend({'status': 'done'}, params))

    def parse_transaction(self, transaction, currency=None):
        timestamp = self.parse8601(self.safe_string(transaction, 'created_at'))
        type = self.safe_string(transaction, 'type')
        amount = self.safe_number(transaction, 'amount')
        currency_code = self.safe_currency_code(self.safe_string(transaction, 'currency'))
        return {
            'info': transaction,
            'id': self.safe_string(transaction, 'id'),
            'txid': self.safe_string(transaction, 'txHash'),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'type': type,
            'amount': amount,
            'currency': currency_code,
            'status': 'done',
            'fee': None,
            'address': None,
            'network': None,
        }

    
    def fetch_transactions(self, code=None, since=None, limit=None, params={}):
        self.load_markets()
        response = self.request('users/transactions-history', 'private', 'GET', params)
        return self.parse_transactions(self.safe_value(response, 'transactions', []), code, since, limit)
