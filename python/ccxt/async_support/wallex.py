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
                'CORS': None, 'spot': True, 'margin': False, 'swap': False, 'future': False,
                'fetchMarkets': True, 'fetchTicker': True, 'fetchTickers': True, 'fetchOrderBook': True,
                'fetchOHLCV': True, 'fetchTrades': True, 'fetchBalance': True, 'createOrder': True,
                'cancelOrder': True, 'fetchOpenOrders': True, 'fetchOrders': True, 'fetchOrder': True,
                'fetchMyTrades': False, 'fetchTradingFee': False, 'fetchTradingFees': False,
            },
            'timeframes': {
                '1m': '1', '5m': '5', '15m': '15', '30m': '30', '1h': '60', '2h': '120',
                '4h': '240', '6h': '360', '8h': '480', '12h': '720', '1d': '1D', '2d': '2D', '3d': '3D', '1w': '1W',
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
                    'get': ['v1/markets', 'v1/udf/history'],
                },
                'private': {
                    'get': ['v1/account/balances', 'v1/account/openOrders'],
                    'post': ['v1/account/orders'],
                    'delete': ['v1/account/orders'],
                },
            },
            'requiredCredentials': {'apiKey': True, 'secret': False},
            'options': {'defaultType': 'spot'},
        })

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if headers is None:
            headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        if api == 'private':
            self.check_required_credentials()
            headers['x-api-key'] = self.apiKey
            if method in ['POST', 'DELETE']:
                headers['Content-Type'] = 'application/json'
                body = self.json(query)
        elif method == 'GET':
            if query:
                url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def fetch_markets(self, params={}):
        response = await self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols = self.safe_value(result, 'symbols', {})
        keys = list(symbols.keys())
        markets = []
        for i in range(0, len(keys)):
            id = keys[i]
            market = self.safe_value(symbols, id, {})
            base = self.safe_string(market, 'baseAsset')
            quote = self.safe_string(market, 'quoteAsset')
            if base is None or quote is None:
                continue
            markets.append({
                'id': id, 'symbol': base + '/' + quote, 'base': base, 'quote': quote,
                'baseId': base, 'quoteId': quote, 'type': 'spot', 'spot': True, 'active': True,
                'precision': {
                    'amount': self.safe_integer(market, 'stepSize') or 8,
                    'price': self.safe_integer(market, 'tickSize') or 8,
                },
                'limits': {
                    'amount': {'min': 0.00000001, 'max': None},
                    'price': {'min': 0.00000001, 'max': None},
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
            'symbol': symbol, 'timestamp': timestamp, 'datetime': self.iso8601(timestamp),
            'high': self.safe_number(stats, '24h_highPrice'), 'low': self.safe_number(stats, '24h_lowPrice'),
            'bid': self.safe_number(stats, 'bidPrice'), 'ask': self.safe_number(stats, 'askPrice'),
            'last': last, 'close': last, 'baseVolume': self.safe_number(stats, '24h_volume'),
            'quoteVolume': self.safe_number(stats, '24h_quoteVolume'), 'info': ticker,
        }, market)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols = self.safe_value(result, 'symbols', {})
        data = self.safe_value(symbols, market['id'], {})
        return self.parse_ticker(data, market)

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        resolution = self.safe_string(self.timeframes, timeframe)
        if resolution is None:
            raise NotSupported(self.id + ' fetchOHLCV does not support timeframe ' + timeframe)
        now = self.seconds()
        duration = self.parse_timeframe(timeframe)
        candles_limit = 500 if limit is None else limit
        from_ts = (now - int(duration * candles_limit)) if since is None else int(since / 1000)
        request = {'symbol': market['id'], 'resolution': resolution, 'from': from_ts, 'to': now}
        response = await self.request('v1/udf/history', 'public', 'GET', self.extend(request, params))
        t = self.safe_list(response, 't', [])
        o = self.safe_list(response, 'o', [])
        h = self.safe_list(response, 'h', [])
        l = self.safe_list(response, 'l', [])
        c = self.safe_list(response, 'c', [])
        v = self.safe_list(response, 'v', [])
        result = []
        for i in range(0, len(t)):
            result.append([self.safe_timestamp(t, i), self.safe_number(o, i), self.safe_number(h, i), self.safe_number(l, i), self.safe_number(c, i), self.safe_number(v, i)])
        return self.filter_by_since_limit(result, since, limit, 0)

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.request('v1/account/balances', 'private', 'GET', params)
        result = self.safe_value(response, 'result', {})
        balances = {'info': response}
        values = list(result.values())
        for i in range(0, len(values)):
            item = values[i]
            if item is None or not isinstance(item, dict):
                continue
            code = self.safe_string(item, 'asset')
            if code is None:
                continue
            balances[code] = {'free': self.safe_number(item, 'available'), 'used': self.safe_number(item, 'freeze'), 'total': self.safe_number(item, 'balance')}
        return self.safe_balance(balances)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {'symbol': market['id'], 'side': side, 'type': type, 'quantity': self.amount_to_precision(symbol, amount)}
        if price is not None:
            request['price'] = self.price_to_precision(symbol, price)
        response = await self.request('v1/account/orders', 'private', 'POST', self.extend(request, params))
        order_data = self.safe_value(response, 'result', response)
        return self.parse_order(order_data, market)

    async def cancel_order(self, id, symbol=None, params={}):
        request = {'client_id': id}
        return await self.request('v1/account/orders', 'private', 'DELETE', self.extend(request, params))

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'clientOrderId')
        timestamp = self.safe_integer(order, 'transactTime')
        symbol = self.safe_string(market, 'symbol')
        return self.safe_order({
            'id': id, 'clientOrderId': id, 'info': order, 'timestamp': timestamp, 'datetime': self.iso8601(timestamp),
            'status': self.safe_string_lower(order, 'status'), 'symbol': symbol, 'type': self.safe_string_lower(order, 'type'),
            'side': self.safe_string_lower(order, 'side'), 'price': self.safe_number(order, 'price'),
            'amount': self.safe_number(order, 'origQty'), 'filled': self.safe_number(order, 'executedQty'),
        }, market)

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol) if symbol is not None else None
        response = await self.request('v1/account/openOrders', 'private', 'GET', params)
        result = self.safe_value(response, 'result', {})
        orders = self.safe_value(result, 'orders', [])
        return self.parse_orders(orders, market, since, limit)