from ccxt.base.exchange import Exchange
from ccxt.base.errors import AuthenticationError


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

                'logo':
                    'https://nobitex.ir/assets/images/logo.svg',

                'api': {

                    'public':
                        'https://apiv2.nobitex.ir',

                    'private':
                        'https://apiv2.nobitex.ir',

                },


                'www':
                    'https://nobitex.ir',


                'doc': [
                    'https://apidocs.nobitex.ir',
                ],

            },


            'api': {

                'public': {

                    'get': {

                        'market/stats': 1,

                        'v3/orderbook/{symbol}': 1,

                        'v2/trades/{symbol}': 1,

                    },

                },


                'private': {

                    'get': {

                        'users/profile': 1,

                        'users/transactions-history': 1,

                        'users/markets/favorite': 1,

                    },


                    'post': {

                        'users/wallets/list': 1,

                        'market/orders/add': 1,

                        'market/orders/update-status': 1,

                        'market/orders/list': 1,

                    },

                },

            },

        })


    def sign(
        self,
        path,
        api='public',
        method='GET',
        params={},
        headers=None,
        body=None
    ):

        url = self.urls['api'][api] + '/' + self.implode_params(path, params)

        query = self.omit(
            params,
            self.extract_params(path)
        )


        if query and method == 'GET':
            url += '?' + self.urlencode(query)


        if headers is None:
            headers = {}


        headers['User-Agent'] = (
            'Mozilla/5.0'
        )


        if api == 'private':

            if not self.apiKey:
                raise AuthenticationError(
                    'Nobitex requires apiKey'
                )


            headers['Authorization'] = (
                'Token ' + self.apiKey
            )


        return {

            'url': url,

            'method': method,

            'body': body,

            'headers': headers,

        }



    def fetch_markets(self, params={}):

        response = self.publicGetMarketStats(params)


        stats = self.safe_value(
            response,
            'stats',
            {}
        )


        markets = []


        for market_id in stats:


            # Example:
            # BTCIRT
            # BTCRLS

            if len(market_id) < 6:
                continue


            base_id = market_id[:-3]

            quote_id = market_id[-3:]


            base = self.safe_currency_code(
                base_id
            )

            quote = self.safe_currency_code(
                quote_id
            )


            markets.append({

                'id': market_id,


                'symbol':
                    base + '/' + quote,


                'base':
                    base,


                'quote':
                    quote,


                'baseId':
                    base_id,


                'quoteId':
                    quote_id,


                'type':
                    'spot',


                'spot':
                    True,


                'active':
                    True,


                'precision': {

                    'amount': 8,

                    'price': 1,

                },


                'limits': {

                    'amount': {

                        'min': None,

                        'max': None,

                    },


                    'price': {

                        'min': None,

                        'max': None,

                    },


                    'cost': {

                        'min': None,

                        'max': None,

                    },

                },


                'info':
                    stats[market_id],

            })


        return markets


        def parse_ticker(self, ticker, market=None):

        timestamp = self.milliseconds()

        symbol = self.safe_string(
            market,
            'symbol'
        )


        return {

            'symbol': symbol,

            'timestamp': timestamp,

            'datetime':
                self.iso8601(timestamp),


            'high':
                self.safe_number(
                    ticker,
                    'dayHigh'
                ),


            'low':
                self.safe_number(
                    ticker,
                    'dayLow'
                ),


            'bid': None,

            'bidVolume': None,

            'ask': None,

            'askVolume': None,

            'vwap': None,


            'open':
                self.safe_number(
                    ticker,
                    'dayOpen'
                ),


            'close':
                self.safe_number(
                    ticker,
                    'dayClose'
                ),


            'last':
                self.safe_number(
                    ticker,
                    'latest'
                ),


            'previousClose': None,

            'change': None,

            'percentage': None,

            'average': None,


            'baseVolume':
                self.safe_number(
                    ticker,
                    'volumeSrc'
                ),


            'quoteVolume':
                self.safe_number(
                    ticker,
                    'volumeDst'
                ),


            'info':
                ticker,

        }



    def fetch_ticker(self, symbol, params={}):

        self.load_markets()

        market = self.market(symbol)


        response = self.publicGetMarketStats(
            params
        )


        stats = self.safe_value(
            response,
            'stats',
            {}
        )


        market_id = (
            market['baseId']
            +
            market['quoteId']
        )


        ticker = self.safe_value(
            stats,
            market_id,
            {}
        )


        return self.parse_ticker(
            ticker,
            market
        )



    def parse_order_book(self, orderbook, symbol, timestamp=None, nonce=None):

        bids = self.safe_value(
            orderbook,
            'bids',
            []
        )


        asks = self.safe_value(
            orderbook,
            'asks',
            []
        )


        return {

            'symbol': symbol,

            'bids':
                self.parse_bids_asks(
                    bids,
                    0,
                    1
                ),


            'asks':
                self.parse_bids_asks(
                    asks,
                    0,
                    1
                ),


            'timestamp': timestamp,

            'datetime':
                self.iso8601(timestamp),


            'nonce': nonce,

        }



    def fetch_order_book(self, symbol, limit=None, params={}):

        self.load_markets()


        market = self.market(symbol)


        request_symbol = (
            market['baseId']
            +
            market['quoteId']
        )


        response = self.publicGetV3OrderbookSymbol(
            {
                'symbol': request_symbol,
                **params
            }
        )


        timestamp = self.milliseconds()


        return self.parse_order_book(
            response,
            symbol,
            timestamp
        )



    def parse_trade(self, trade, market=None):

        timestamp = self.safe_timestamp(
            trade,
            'time'
        )


        price = self.safe_number(
            trade,
            'price'
        )


        amount = self.safe_number(
            trade,
            'volume'
        )


        side = self.safe_string_lower(
            trade,
            'type'
        )


        if side not in ['buy', 'sell']:
            side = None



        cost = None

        if price is not None and amount is not None:
            cost = price * amount



        return {

            'id':
                self.safe_string(
                    trade,
                    'id'
                ),


            'info':
                trade,


            'timestamp':
                timestamp,


            'datetime':
                self.iso8601(timestamp),


            'symbol':
                self.safe_string(
                    market,
                    'symbol'
                ),


            'order': None,


            'type': None,


            'side':
                side,


            'takerOrMaker': None,


            'price':
                price,


            'amount':
                amount,


            'cost':
                cost,


            'fee': None,

        }



    def fetch_trades(self, symbol, since=None, limit=None, params={}):

        self.load_markets()


        market = self.market(symbol)


        request_symbol = (
            market['baseId'].lower()
            +
            market['quoteId'].lower()
        )


        response = self.publicGetV2TradesSymbol(
            {
                'symbol': request_symbol,
                **params
            }
        )


        trades = self.safe_value(
            response,
            'trades',
            response
        )


        return self.parse_trades(
            trades,
            market,
            since,
            limit
        )
        
    def fetch_balance(self, params={}):

        self.load_markets()

        response = self.request(
            'users/wallets/list',
            'private',
            'POST',
            params
        )


        wallets = self.safe_value(
            response,
            'wallets',
            []
        )


        result = {
            'info': response
        }


        for wallet in wallets:

            currency_id = self.safe_string(
                wallet,
                'currency'
            )


            code = self.safe_currency_code(
                currency_id
            )


            free = self.safe_number(
                wallet,
                'activeBalance'
            )


            total = self.safe_number(
                wallet,
                'balance'
            )


            used = None

            if total is not None and free is not None:
                used = total - free



            result[code] = {

                'free': free,

                'used': used,

                'total': total,

            }


        return self.safe_balance(result)



    def parse_order(self, order, market=None):

        timestamp = self.safe_timestamp(
            order,
            'createdAt'
        )


        return {

            'id':
                self.safe_string(
                    order,
                    'id'
                ),


            'clientOrderId': None,


            'info':
                order,


            'timestamp':
                timestamp,


            'datetime':
                self.iso8601(timestamp),


            'lastTradeTimestamp': None,


            'status':
                self.parse_order_status(
                    self.safe_string(order, 'status')
                ),


            'symbol':
                self.safe_string(
                    market,
                    'symbol'
                ),


            'type':
                self.safe_string(
                    order,
                    'type'
                ),


            'timeInForce': None,


            'side':
                self.safe_string_lower(
                    order,
                    'side'
                ),


            'price':
                self.safe_number(
                    order,
                    'price'
                ),


            'amount':
                self.safe_number(
                    order,
                    'amount'
                ),


            'filled':
                self.safe_number(
                    order,
                    'filledAmount'
                ),


            'remaining': None,


            'cost': None,


            'average': None,


            'trades': [],


            'fee': None,


        }



    def parse_order_status(self, status):

        statuses = {

            'open': 'open',

            'active': 'open',

            'done': 'closed',

            'filled': 'closed',

            'canceled': 'canceled',

            'cancelled': 'canceled',

        }


        return statuses.get(
            status,
            status
        )



    def create_order(
        self,
        symbol,
        type,
        side,
        amount,
        price=None,
        params={}
    ):

        self.load_markets()


        market = self.market(symbol)


        request = {

            'type': type,

            'srcCurrency':
                market['baseId'],

            'dstCurrency':
                market['quoteId'],

            'amount':
                amount,

            'side':
                side,

        }


        if price is not None:

            request['price'] = price



        response = self.request(
            'market/orders/add',
            'private',
            'POST',
            self.extend(
                request,
                params
            )
        )


        order = self.safe_value(
            response,
            'order',
            response
        )


        return self.parse_order(
            order,
            market
        )



    def cancel_order(
        self,
        id,
        symbol=None,
        params={}
    ):

        request = {

            'order':
                id,

            'status':
                'canceled',

        }


        response = self.request(

            'market/orders/update-status',

            'private',

            'POST',

            self.extend(
                request,
                params
            )
        )


        return response



    def fetch_open_orders(
        self,
        symbol=None,
        since=None,
        limit=None,
        params={}
    ):


        self.load_markets()


        market = None


        request = {

            'status':
                'open',

        }



        if symbol:

            market = self.market(symbol)


            request.update({

                'srcCurrency':
                    market['baseId'],


                'dstCurrency':
                    market['quoteId'],

            })



        response = self.request(

            'market/orders/list',

            'private',

            'POST',

            self.extend(
                request,
                params
            )

        )



        orders = self.safe_value(
            response,
            'orders',
            []
        )



        return self.parse_orders(

            orders,

            market,

            since,

            limit

        )



    def fetch_profile(self, params={}):

        return self.request(

            'users/profile',

            'private',

            'GET',

            params

        )



    def fetch_transactions_history(self, params={}):

        response = self.request(

            'users/transactions-history',

            'private',

            'GET',

            params

        )


        return self.safe_value(

            response,

            'transactions',

            []

        )



    def fetch_favorite_markets(self, params={}):

        return self.request(

            'users/markets/favorite',

            'private',

            'GET',

            params

        )