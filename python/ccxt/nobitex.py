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
                    'private': 'https://apiv2.nobitex.ir', 
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
                        'users/transactions-history',
                        'users/markets/favorite',
                    ],
                    'post': [
                        'users/wallets/list',
                        'market/orders/add',
                        'market/orders/cancel',
                        'market/orders/list',
                        'users/accounts-add',
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

    def parse_order_book(self, orderbook, symbol):
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
            'timestamp': None,
            'datetime': None,
            'nonce': None,
        }

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request_symbol = market['baseId'].lower() + market['quoteId'].lower()
        response = self.request('v3/orderbook/' + request_symbol, 'public', 'GET', params)
        return self.parse_order_book(response, market['symbol'])

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_timestamp(trade, 'time')
        price = self.safe_string(trade, 'price')
        amount = self.safe_string(trade, 'volume')
        side = self.safe_string_lower(trade, 'type')
        if side != 'buy' and side != 'sell':
            side = None
        symbol = self.safe_string(market, 'symbol')
        cost = self.parse_number(self.number_to_string(self.multiply(price, amount))) if price and amount else None
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': self.safe_string(trade, 'id'),
            'type': None,
            'side': side,
            'price': self.parse_number(price),
            'amount': self.parse_number(amount),
            'cost': cost,
            'fee': None,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request_symbol = market['baseId'].lower() + market['quoteId'].lower()
        response = self.request('v2/trades/' + request_symbol, 'public', 'GET', params)
        return self.parse_trades(response, market, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.request('users/wallets/list', 'private', 'POST', params)
        wallets = self.safe_value(response, 'wallets', [])
        result = {'info': response}

        for i in range(0, len(wallets)):
            wallet = wallets[i]
            currencyId = self.safe_string(wallet, 'currency')
            code = self.safe_currency_code(currencyId)
            total = self.safe_string(wallet, 'balance')
            free = self.safe_string(wallet, 'activeBalance')
            used = self.number_to_string(self.subtract(total, free)) if total and free else None
            
            account = {
                'free': self.parse_number(free),
                'used': self.parse_number(used),
                'total': self.parse_number(total),
            }
            if code in result:
                result[code] = self.deep_extend(result[code], account)
            else:
                result[code] = account
                
        return self.safe_balance(result)

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'id')
        timestamp = self.safe_timestamp(order, 'time')
        symbol = self.safe_string(market, 'symbol')
        amount = self.safe_string(order, 'amount')
        price = self.safe_string(order, 'price')
        side = self.safe_string_lower(order, 'type')
        
        return {
            'info': order,
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': self.parse_number(price),
            'amount': self.parse_number(amount),
            'filled': None,
            'remaining': None,
            'status': 'open',
            'fee': None,
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        
        request = {
            'type': side,
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
            'amount': amount,
            'price': price,
        }
        
        response = self.request('market/orders/add', 'private', 'POST', self.extend(request, params))
        return self.parse_order(response, market)

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'order': id,
        }
        response = self.request('market/orders/cancel', 'private', 'POST', self.extend(request, params))
        return response

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        request = {
            'status': 'open',
        }
        if market is not None:
            request['srcCurrency'] = market['baseId']
            request['dstCurrency'] = market['quoteId']
        response = self.request('market/orders/list', 'private', 'POST', self.extend(request, params))
        orders = self.safe_value(response, 'orders', [])
        return self.parse_orders(orders, market, since, limit)


    def fetch_profile(self, params={}):
        return self.request('users/profile', 'private', 'GET', params)

    def fetch_transactions_history(self, params={}):
        response = self.request('users/transactions-history', 'private', 'GET', params)
        transactions = self.safe_value(response, 'transactions', [])
        return transactions

    def fetch_favorite_markets(self, params={}):
        return self.request('users/markets/favorite', 'private', 'GET', params)