from ccxt.base.exchange import Exchange

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
                'fetchOrderBook': True,
                'fetchTrades': True,
                'fetchBalance': True,
                'createOrder': True,
                'cancelOrder': True,
                'fetchOpenOrders': True,
            },
            'urls': {
                'logo': 'https://nobitex.ir/assets/images/logo.svg',
                'api': {
                    'public': 'https://api.nobitex.ir',
                    'private': 'https://api.nobitex.ir',
                },
                'www': 'https://nobitex.ir',
                'doc': [
                    'https://apidocs.nobitex.ir',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'v2/trades/{symbol}',
                        'v3/orderbook/{symbol}',
                        'market/stats',
                        'status',
                    ],
                },
                'private': {
                    'get': [
                        'users/profile',
                    ],
                    'post': [
                        'users/wallets/list',
                        'market/orders/add',
                        'market/orders/cancel',
                        'market/orders/list',
                    ],
                },
            },
        })

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        
        if query:
            if method == 'GET':
                url += '?' + self.urlencode(query)
        
        if headers is None:
            headers = {}
            
        # اضافه کردن User-Agent برای دور زدن مسدودی‌های سرویس دهنده
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        if api == 'private':
            self.check_required_credentials()
            headers['Authorization'] = 'Token ' + self.apiKey
        
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def fetch_markets(self, params={}):
        response = self.request('market/stats', 'public', 'GET', params)
        stats = self.safe_value(response, 'stats', {})
        keys = list(stats.keys())
        result = []

        for i in range(0, len(keys)):
            id = keys[i]
            parts = id.split('-')
            if len(parts) != 2:
                continue
            baseId = parts[0]
            quoteId = parts[1]
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'settle': None,
                'baseId': baseId,
                'quoteId': quoteId,
                'settleId': None,
                'type': 'spot',
                'spot': True,
                'margin': False,
                'swap': False,
                'future': False,
                'option': False,
                'active': True,
                'contract': False,
                'linear': None,
                'inverse': None,
                'contractSize': None,
                'expiry': None,
                'expiryDatetime': None,
                'strike': None,
                'optionType': None,
                'precision': {
                    'amount': self.parse_number('0.000001'),
                    'price': self.parse_number('1'),
                },
                'limits': {
                    'leverage': {'min': None, 'max': None},
                    'amount': {'min': None, 'max': None},
                    'price': {'min': None, 'max': None},
                    'cost': {'min': None, 'max': None},
                },
                'info': stats[id],
            })
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = None
        marketId = self.safe_string(market, 'id')
        symbol = self.safe_string(market, 'symbol')
        if symbol is None:
            symbol = marketId
        last = self.safe_string(ticker, 'latest')
        open = self.safe_string(ticker, 'open')
        high = self.safe_string(ticker, 'high')
        low = self.safe_string(ticker, 'low')
        close = last
        baseVolume = self.safe_string(ticker, 'dayVolume')
        quoteVolume = self.safe_string(ticker, 'dayVolumePrice')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.parse_number(high),
            'low': self.parse_number(low),
            'bid': None,
            'bidVolume': None,
            'ask': None,
            'askVolume': None,
            'vwap': None,
            'open': self.parse_number(open),
            'close': self.parse_number(close),
            'last': self.parse_number(last),
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.parse_number(baseVolume),
            'quoteVolume': self.parse_number(quoteVolume),
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
        tickerKey = market['baseId'] + '-' + market['quoteId']
        ticker = self.safe_value(stats, tickerKey, {})
        return self.parse_ticker(ticker, market)