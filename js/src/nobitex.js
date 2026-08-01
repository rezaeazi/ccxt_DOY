import Exchange from './base/Exchange.js';

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
                'fetchOrderBook': true,
                'fetchTrades': true,
                'fetchBalance': true,
                'createOrder': true,
                'cancelOrder': true,
                'fetchOpenOrders': true,
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

        if (api === 'private') {
            this.checkRequiredCredentials();
            headers = {
                'Authorization': 'Token ' + this.apiKey,
            };
        }

        return { 'url': url, 'method': method, 'body': body, 'headers': headers };
    }

    async fetchMarkets(params = {}) {
        const response = await this.publicGetMarketStats(params);
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
        const timestamp = undefined;
        const marketId = this.safeString(market, 'id');
        let symbol = this.safeString(market, 'symbol');
        if (symbol === undefined) {
            symbol = marketId;
        }
        
        const last = this.safeString(ticker, 'latest');
        const open = this.safeString(ticker, 'open');
        const high = this.safeString(ticker, 'high');
        const low = this.safeString(ticker, 'low');
        const close = last;
        const baseVolume = this.safeString(ticker, 'dayVolume');
        const quoteVolume = this.safeString(ticker, 'dayVolumePrice');
        
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'high': this.parseNumber(high),
            'low': this.parseNumber(low),
            'bid': this.parseNumber(undefined),
            'bidVolume': this.parseNumber(undefined),
            'ask': this.parseNumber(undefined),
            'askVolume': this.parseNumber(undefined),
            'vwap': undefined,
            'open': this.parseNumber(open),
            'close': this.parseNumber(close),
            'last': this.parseNumber(last),
            'previousClose': undefined,
            'change': undefined,
            'percentage': undefined,
            'average': undefined,
            'baseVolume': this.parseNumber(baseVolume),
            'quoteVolume': this.parseNumber(quoteVolume),
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
        
        const response = await this.publicGetMarketStats(this.extend(request, params));
        const stats = this.safeValue(response, 'stats', {});
        
        const tickerKey = market['baseId'] + '-' + market['quoteId'];
        const ticker = this.safeValue(stats, tickerKey, {});
        
        return this.parseTicker(ticker, market);
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
            'symbol': market['baseId'].toLowerCase() + market['quoteId'].toLowerCase(),
        };
        
        const response = await this.publicGetV3OrderbookSymbol(this.extend(request, params));
        const orderbook = this.parseOrderBook(response, market['symbol']);
        
        return orderbook;
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
            'symbol': market['baseId'].toLowerCase() + market['quoteId'].toLowerCase(),
        };
        const response = await this.publicGetV2TradesSymbol(this.extend(request, params));
        return this.parseTrades(response, market, since, limit);
    }

    async fetchBalance(params = {}) {
        await this.loadMarkets();
        const response = await this.privatePostUsersWalletsList(params);
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

    parseOrder(order, market = undefined) {
        const id = this.safeString(order, 'id');
        const timestamp = this.safeTimestamp(order, 'time');
        const symbol = this.safeString(market, 'symbol');
        const amount = this.safeString(order, 'amount');
        const price = this.safeString(order, 'price');
        const side = this.safeStringLower(order, 'type');
        
        return {
            'info': order,
            'id': id,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': this.parseNumber(price),
            'amount': this.parseNumber(amount),
            'filled': undefined,
            'remaining': undefined,
            'status': 'open',
            'fee': undefined,
        };
    }

    async createOrder(symbol, type, side, amount, price = undefined, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        
        const request = {
            'type': side,
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
            'amount': amount,
            'price': price,
        };
        
        const response = await this.privatePostMarketOrdersAdd(this.extend(request, params));
        
        return this.parseOrder(response, market);
    }

    async cancelOrder(id, symbol = undefined, params = {}) {
        await this.loadMarkets();
        const request = {
            'order': id,
        };
        const response = await this.privatePostMarketOrdersCancel(this.extend(request, params));
        return response;
    }

    async fetchOpenOrders(symbol = undefined, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets();
        let market = undefined;
        if (symbol !== undefined) {
            market = this.market(symbol);
        }
        const request = {
            'status': 'open',
        };
        if (market !== undefined) {
            request['srcCurrency'] = market['baseId'];
            request['dstCurrency'] = market['quoteId'];
        }
        const response = await this.privatePostMarketOrdersList(this.extend(request, params));
        const orders = this.safeValue(response, 'orders', []);
        return this.parseOrders(orders, market, since, limit);
    }
}