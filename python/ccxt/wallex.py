from ccxt.base.exchange import Exchange
from ccxt.base.errors import AuthenticationError, OrderNotFound, NotSupported

class wallex(Exchange):
    def describe(self):
        return self.deep_extend(super(wallex, self).describe(), {
            'id': 'wallex',
            'name': 'Wallex',
            'countries': ['IR'],
            'version': 'v1',
            'rateLimit': 200,
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
                'cancelOrder': True,
                'fetchOpenOrders': True,
                'fetchOrders': True,
                'fetchOrder': True,
                'fetchMyTrades': False,
                'fetchTradingFee': False,
                'fetchTradingFees': False,
            },
            'urls': {
                'logo': 'https://wallex.ir/assets/images/logo.svg',
                'api': {
                    'public': 'https://api.wallex.ir',
                    'private': 'https://api.wallex.ir',
                },
                'www': 'https://wallex.ir',
                'doc': ['https://developers.wallex.ir/'],
            },
            'api': {
                'public': {
                    'get': [
                        'v1/markets',
                    ],
                },
                'private': {
                    'get': [
                        'v1/account/balances',
                        'v1/account/openOrders',
                    ],
                    'post': [
                        'v1/account/orders',
                    ],
                    'delete': [
                        'v1/account/orders',
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
                raise AuthenticationError('Wallex requires apiKey')
            headers['x-api-key'] = self.apiKey
            if method == 'POST' or method == 'DELETE':
                headers['Content-Type'] = 'application/json'
                body = self.json(query)
        elif method == 'GET':
            if query:
                url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def fetch_markets(self, params={}):
        response = self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols = self.safe_value(result, 'symbols', {})
        keys = list(symbols.keys())
        markets = []
        for i in range(len(keys)):
            id = keys[i]
            market = self.safe_value(symbols, id, {})
            base = self.safe_string(market, 'baseAsset')
            quote = self.safe_string(market, 'quoteAsset')
            if base is None or quote is None:
                continue
            markets.append({
                'id': id,
                'symbol': base + '/' + quote,
                'base': base,
                'quote': quote,
                'baseId': base,
                'quoteId': quote,
                'type': 'spot',
                'spot': True,
                'active': True,
                'precision': {
                    'amount': self.safe_integer(market, 'stepSize'),
                    'price': self.safe_integer(market, 'tickSize'),
                },
                'limits': {
                    'amount': {'min': self.safe_number(market, 'minQty'), 'max': None},
                    'price': {'min': None, 'max': None},
                    'cost': {'min': None, 'max': None},
                },
                'info': market,
            })
        return markets

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = self.safe_string(market, 'symbol')
        stats = self.safe_value(ticker, 'stats', {})
        last = self.safe_number(stats, 'lastPrice')
        return self.safe_ticker({
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_number(stats, '24h_highPrice'),
            'low': self.safe_number(stats, '24h_lowPrice'),
            'bid': self.safe_number(stats, 'bidPrice'),
            'ask': self.safe_number(stats, 'askPrice'),
            'last': last,
            'close': last,
            'baseVolume': self.safe_number(stats, '24h_volume'),
            'quoteVolume': self.safe_number(stats, '24h_quoteVolume'),
            'info': ticker,
        }, market)

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols = self.safe_value(result, 'symbols', {})
        data = self.safe_value(symbols, market['id'], {})
        return self.parse_ticker(data, market)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        response = self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols_data = self.safe_value(result, 'symbols', {})
        keys = list(symbols_data.keys())
        tickers = {}
        for i in range(len(keys)):
            id = keys[i]
            market = self.safe_value(self.markets_by_id, id)
            if market is not None:
                ticker = self.parse_ticker(symbols_data[id], market)
                tickers[market['symbol']] = ticker
        return tickers

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.request('v1/account/balances', 'private', 'GET', params)
        result = self.safe_value(response, 'result', {})
        balances = {'info': response}
        values = list(result.values())
        for i in range(len(values)):
            item = values[i]
            if item is None or not isinstance(item, dict):
                continue
            balance = item
            code = self.safe_string(balance, 'asset')
            if code is None:
                continue
            total = self.safe_number(balance, 'balance')
            free = self.safe_number(balance, 'available')
            used = self.safe_number(balance, 'freeze')
            balances[code] = {'free': free, 'used': used, 'total': total}
        return self.safe_balance(balances)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'side': side,
            'type': type,
            'quantity': self.amount_to_precision(symbol, amount),
        }
        if price is not None:
            request['price'] = self.price_to_precision(symbol, price)
        response = self.request('v1/account/orders', 'private', 'POST', self.extend(request, params))
        order_data = self.safe_value(response, 'result', response)
        return self.parse_order(order_data, market)

    def cancel_order(self, id, symbol=None, params={}):
        request = {'client_id': id}
        response = self.request('v1/account/orders', 'private', 'DELETE', self.extend(request, params))
        return response

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'clientOrderId')
        timestamp = self.safe_integer(order, 'transactTime')
        symbol = self.safe_string(market, 'symbol')
        return self.safe_order({
            'id': id,
            'clientOrderId': id,
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'status': self.safe_string_lower(order, 'status'),
            'symbol': symbol,
            'type': self.safe_string_lower(order, 'type'),
            'side': self.safe_string_lower(order, 'side'),
            'price': self.safe_number(order, 'price'),
            'amount': self.safe_number(order, 'origQty'),
            'filled': self.safe_number(order, 'executedQty'),
            'remaining': None,
            'cost': None,
            'fee': None,
            'trades': None,
        }, market)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        response = self.request('v1/account/openOrders', 'private', 'GET', params)
        result = self.safe_value(response, 'result', {})
        orders = self.safe_value(result, 'orders', [])
        return self.parse_orders(orders, market, since, limit)