import Exchange from './base/Exchange.js';
import { OrderNotFound, NotSupported } from './base/errors.js';

export default class nobitex extends Exchange {

    constructor(options = {}) {
        super(options);
    }

    describe() {
        return this.deepExtend(super.describe(), {
            'id': 'nobitex',
            'name': 'Nobitex',
            'countries': ['IR'],
            'rateLimit': 100,
            'certified': false,
            'has': {
                'CORS': undefined,
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'fetchMarkets': true,
                'fetchTicker': true,
                'fetchTickers': true,
                'fetchOrderBook': true,
                'fetchOHLCV': false,  // Not supported by Nobitex API
                'fetchTrades': true,
                'fetchBalance': true,
                'createOrder': true,
                'fetchOrder': true,
                'cancelOrder': true,
                'fetchOpenOrders': true,
                'fetchClosedOrders': true,
                'fetchOrders': true,
                'fetchMyTrades': true,
                'fetchTradingFee': false, // Not supported dynamically
                'fetchTradingFees': false, // Not supported dynamically
            },
            'urls': {
                'logo': 'https://nobitex.ir/assets/images/logo.svg',
                'api': {
                    'public': 'https://apiv2.nobitex.ir',
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
                        'market/orders/update-status',
                        'users/accounts-add',
                    ],
                },
            },
        });
    }

    sign(path, api = 'public', method = 'GET', params = {}, headers = undefined, body = undefined) {
        let url = this.urls['api'][api] + '/' + this.implodeParams(path, params);
        const query = this.omit(params, this.extractParams(path));
        
        if (Object.keys(query).length) {
            if (method === 'GET') {
                url += '?' + this.urlencode(query);
            }
        }

        if (headers === undefined) {
            headers = {};
        }

        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';

        if (api === 'private') {
            this.checkRequiredCredentials();
            headers['Authorization'] = 'Token ' + this.apiKey;
            if (method === 'POST') {
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
            }
        }

        return { 'url': url, 'method': method, 'body': body, 'headers': headers };
    }

    async fetchMarkets(params = {}) {
        const response = await this.request('market/stats', 'public', 'GET', params);
        const stats = this.safeValue(response, 'stats', {});
        const keys = Object.keys(stats);
        const result = [];

        for (let i = 0; i < keys.length; i++) {
            const id = keys[i];
            const parts = id.split('-');
            
            if (parts.length !== 2) {
                continue;
            }

            const baseId = parts[0];
            const quoteId = parts[1];

            const base = this.safeCurrencyCode(baseId);
            const quote = this.safeCurrencyCode(quoteId);
            const symbol = base + '/' + quote;

            result.push({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'settle': null,
                'baseId': baseId,
                'quoteId': quoteId,
                'settleId': null,
                'type': 'spot',
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'option': false,
                'active': true,
                'contract': false,
                'linear': null,
                'inverse': null,
                'contractSize': null,
                'expiry': null,
                'expiryDatetime': null,
                'strike': null,
                'optionType': null,
                'precision': {
                    'amount': this.parseNumber('0.000001'),
                    'price': this.parseNumber('1'),
                },
                'limits': {
                    'leverage': { 'min': null, 'max': null },
                    'amount': { 'min': null, 'max': null },
                    'price': { 'min': null, 'max': null },
                    'cost': { 'min': null, 'max': null },
                },
                'info': stats[id],
            });
        }

        return result;
    }

    parseTicker(ticker, market = undefined) {
        const timestamp = this.milliseconds();
        const marketId = this.safeString(market, 'id');
        let symbol = this.safeString(market, 'symbol');
        if (symbol === undefined) {
            symbol = marketId;
        }
        
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'high': this.parseNumber(this.safeString(ticker, 'dayHigh')),
            'low': this.parseNumber(this.safeString(ticker, 'dayLow')),
            'bid': this.parseNumber(this.safeString(ticker, 'bestBuy')),
            'bidVolume': undefined,
            'ask': this.parseNumber(this.safeString(ticker, 'bestSell')),
            'askVolume': undefined,
            'vwap': undefined,
            'open': this.parseNumber(this.safeString(ticker, 'dayOpen')),
            'close': this.parseNumber(this.safeString(ticker, 'latest')),
            'last': this.parseNumber(this.safeString(ticker, 'latest')),
            'previousClose': undefined,
            'change': undefined,
            'percentage': this.parseNumber(this.safeString(ticker, 'dayChange')),
            'average': undefined,
            'baseVolume': this.parseNumber(this.safeString(ticker, 'volumeSrc')),
            'quoteVolume': this.parseNumber(this.safeString(ticker, 'volumeDst')),
            'info': ticker,
        };
    }

    async fetchTicker(symbol, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        
        const request = {
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
        };
        
        const response = await this.request('market/stats', 'public', 'GET', this.extend(request, params));
        const stats = this.safeValue(response, 'stats', {});
        
        const tickerKey = market['baseId'] + '-' + market['quoteId'];
        const ticker = this.safeValue(stats, tickerKey, {});
        
        return this.parseTicker(ticker, market);
    }

    async fetchTickers(symbols = undefined, params = {}) {
        await this.loadMarkets();
        const result = {};
        for (const symbol in this.markets) {
            const market = this.markets[symbol];
            const info = this.safeValue(market, 'info');
            if (info !== undefined) {
                result[symbol] = this.parseTicker(info, market);
            }
        }
        return result;
    }

    parseOrderBook(orderbook, symbol) {
        const bids = this.safeValue(orderbook, 'bids', []);
        const asks = this.safeValue(orderbook, 'asks', []);
        
        return {
            'symbol': symbol,
            'bids': this.parseBidsAsks(bids),
            'asks': this.parseBidsAsks(asks),
            'timestamp': undefined,
            'datetime': undefined,
            'nonce': undefined,
        };
    }

    async fetchOrderBook(symbol, limit = undefined, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        
        const request = {
            'symbol': market['baseId'].toUpperCase() + market['quoteId'].toUpperCase(),
        };
        
        const response = await this.request('v3/orderbook/' + request['symbol'], 'public', 'GET', params);
        const orderbook = this.parseOrderBook(response, market['symbol']);
        
        return orderbook;
    }

    async fetchOHLCV(symbol, timeframe = '1d', since = undefined, limit = undefined, params = {}) {
        throw new NotSupported('Nobitex API does not support OHLCV data.');
    }

    parseTrade(trade, market = undefined) {
        const timestamp = this.safeTimestamp(trade, 'time');
        const price = this.safeString(trade, 'price');
        const amount = this.safeString(trade, 'volume');
        let side = this.safeStringLower(trade, 'type');
        if (side !== 'buy' && side !== 'sell') {
            side = undefined;
        }
        const symbol = this.safeString(market, 'symbol');
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'symbol': symbol,
            'id': this.safeString(trade, 'id'),
            'type': undefined,
            'side': side,
            'price': this.parseNumber(price),
            'amount': this.parseNumber(amount),
            'cost': this.parseNumber(this.numberToString(this.multiply(price, amount))),
            'fee': undefined,
        };
    }

    async fetchTrades(symbol, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        const request = {
            'symbol': market['baseId'].toUpperCase() + market['quoteId'].toUpperCase(),
        };
        const response = await this.request('v2/trades/' + request['symbol'], 'public', 'GET', params);
        return this.parseTrades(response, market, since, limit);
    }

    async fetchBalance(params = {}) {
        await this.loadMarkets();
        const response = await this.request('users/wallets/list', 'private', 'POST', params);
        const wallets = this.safeValue(response, 'wallets', []);
        const result = { 'info': response };

        for (let i = 0; i < wallets.length; i++) {
            const wallet = wallets[i];
            const currencyId = this.safeString(wallet, 'currency');
            const code = this.safeCurrencyCode(currencyId);
            const total = this.safeString(wallet, 'balance');
            const free = this.safeString(wallet, 'activeBalance');
            const used = this.numberToString(this.subtract(total, free));
            
            result[code] = {
                'free': this.parseNumber(free),
                'used': this.parseNumber(used),
                'total': this.parseNumber(total),
            };
        }
        return this.safeBalance(result);
    }

    parseOrderStatus(status) {
        const statuses = {
            'open': 'open',
            'active': 'open',
            'done': 'closed',
            'filled': 'closed',
            'canceled': 'canceled',
            'cancelled': 'canceled',
        };
        return statuses[status] || status;
    }

    parseOrder(order, market = undefined) {
        const id = this.safeString(order, 'id');
        const timestamp = this.safeTimestamp(order, 'createdAt');
        const symbol = this.safeString(market, 'symbol');
        const amount = this.safeString(order, 'amount');
        const price = this.safeString(order, 'price');
        const side = this.safeStringLower(order, 'type');
        
        return {
            'info': order,
            'id': id,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'lastTradeTimestamp': undefined,
            'status': this.parseOrderStatus(this.safeString(order, 'status')),
            'symbol': symbol,
            'type': this.safeString(order, 'type'),
            'timeInForce': undefined,
            'side': side,
            'price': this.parseNumber(price),
            'amount': this.parseNumber(amount),
            'filled': this.safeNumber(order, 'filledAmount'),
            'remaining': undefined,
            'cost': undefined,
            'average': undefined,
            'trades': [],
            'fee': undefined,
        };
    }

    async createOrder(symbol, type, side, amount, price = undefined, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        
        const request = {
            'type': type,
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
            'amount': amount,
            'side': side,
        };
        
        if (price !== undefined) {
            request['price'] = price;
        }
        
        const response = await this.request('market/orders/add', 'private', 'POST', this.extend(request, params));
        const order = this.safeValue(response, 'order', response);
        return this.parseOrder(order, market);
    }

    async cancelOrder(id, symbol = undefined, params = {}) {
        await this.loadMarkets();
        const request = {
            'order': id,
            'status': 'canceled',
        };
        const response = await this.request('market/orders/update-status', 'private', 'POST', this.extend(request, params));
        return response;
    }

    async fetchOrder(id, symbol = undefined, params = {}) {
        await this.loadMarkets();
        const orders = await this.fetchOrders(symbol, undefined, undefined, params);
        for (let i = 0; i < orders.length; i++) {
            if (orders[i]['id'] === String(id)) {
                return orders[i];
            }
        }
        throw new OrderNotFound('Order not found: ' + String(id));
    }

    async fetchOrders(symbol = undefined, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets();
        let market = undefined;
        const request = {};
        if (symbol !== undefined) {
            market = this.market(symbol);
            request['srcCurrency'] = market['baseId'];
            request['dstCurrency'] = market['quoteId'];
        }
        const response = await this.request('market/orders/list', 'private', 'POST', this.extend(request, params));
        const orders = this.safeValue(response, 'orders', []);
        return this.parseOrders(orders, market, since, limit);
    }

    async fetchOpenOrders(symbol = undefined, since = undefined, limit = undefined, params = {}) {
        const request = { 'status': 'open' };
        return this.fetchOrders(symbol, since, limit, this.extend(request, params));
    }

    async fetchClosedOrders(symbol = undefined, since = undefined, limit = undefined, params = {}) {
        const request = { 'status': 'done' };
        return this.fetchOrders(symbol, since, limit, this.extend(request, params));
    }

    async fetchMyTrades(symbol = undefined, since = undefined, limit = undefined, params = {}) {
        const request = { 'status': 'done' };
        return this.fetchOrders(symbol, since, limit, this.extend(request, params));
    }

    async fetchTradingFee(symbol, params = {}) {
        throw new NotSupported('Nobitex API does not support dynamic trading fees.');
    }

    async fetchTradingFees(params = {}) {
        throw new NotSupported('Nobitex API does not support dynamic trading fees.');
    }

    async fetchProfile(params = {}) {
        return await this.request('users/profile', 'private', 'GET', params);
    }

    async fetchTransactionsHistory(params = {}) {
        const response = await this.request('users/transactions-history', 'private', 'GET', params);
        return this.safeValue(response, 'transactions', []);
    }

    async fetchFavoriteMarkets(params = {}) {
        return await this.request('users/markets/favorite', 'private', 'GET', params);
    }
}