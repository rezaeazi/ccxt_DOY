import Exchange from './abstract/wallex.js';
export default class wallex extends Exchange {
    describe() {
        return this.deepExtend(super.describe(), {
            'id': 'wallex',
            'name': 'Wallex',
            'countries': ['IR'],
            'version': 'v1',
            'rateLimit': 200,
            'certified': false,
            'has': {
                'CORS': undefined,
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'option': undefined,
                'cancelOrder': true,
                'createOrder': true,
                'fetchBalance': true,
                'fetchMarkets': true,
                'fetchMyTrades': false,
                'fetchOHLCV': true,
                'fetchOpenOrders': true,
                'fetchOrder': true,
                'fetchOrderBook': true,
                'fetchOrders': true,
                'fetchTicker': true,
                'fetchTickers': true,
                'fetchTrades': true,
                'fetchTradingFee': false,
                'fetchTradingFees': false,
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
                        'v2/trades/{symbol}', // Hypothetical endpoint for trades
                        'v1/udf/history',
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
            'timeframes': {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '1h': 60,
                '4h': 240,
                '8h': 480,
                '12h': 720,
                '1d': 1,
                '2d': 2,
                '3d': 3,
            },
            'requiredCredentials': {
                'apiKey': true,
                'secret': false,
            },
            'options': {
                'defaultType': 'spot',
            },
        });
    }
    sign(path, api = 'public', method = 'GET', params = {}, headers = {}, body = undefined) {
        let url = this.urls['api'][api] + '/' + this.implodeParams(path, params);
        const query = this.omit(params, this.extractParams(path));
        if (Object.keys(query).length) {
            if (method === 'GET') {
                url += '?' + this.urlencode(query);
            }
        }
        if (Object.keys(headers).length === 0) {
            headers = {};
        }
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
        if (api === 'private') {
            this.checkRequiredCredentials();
            headers['x-api-key'] = this.apiKey;
            if (method === 'POST' || method === 'DELETE') {
                headers['Content-Type'] = 'application/json';
                body = this.json(query);
            }
        }
        return { 'url': url, 'method': method, 'body': body, 'headers': headers };
    }
    async fetchMarkets(params = {}) {
        const response = await this.request('v1/markets', 'public', 'GET', params);
        const result = this.safeDict(response, 'result', {});
        const symbols = this.safeDict(result, 'symbols', {});
        const keys = Object.keys(symbols);
        const markets = [];
        for (let i = 0; i < keys.length; i++) {
            const id = keys[i];
            const market = this.safeDict(symbols, id, {});
            const base = this.safeString(market, 'baseAsset');
            const quote = this.safeString(market, 'quoteAsset');
            if ((base === undefined) || (quote === undefined)) {
                continue;
            }
            markets.push({
                'id': id,
                'symbol': base + '/' + quote,
                'base': base,
                'quote': quote,
                'baseId': base,
                'quoteId': quote,
                'type': 'spot',
                'spot': true,
                'active': true,
                'precision': {
                    'amount': this.safeInteger(market, 'stepSize'),
                    'price': this.safeInteger(market, 'tickSize'),
                },
                'limits': {
                    'amount': { 'min': this.safeNumber(market, 'minQty'), 'max': undefined },
                    'price': { 'min': undefined, 'max': undefined },
                    'cost': { 'min': undefined, 'max': undefined },
                },
                'info': market,
            });
        }
        return markets;
    }
    parseTicker(ticker, market = undefined) {
        const timestamp = this.milliseconds();
        const symbol = this.safeString(market, 'symbol');
        const stats = this.safeDict(ticker, 'stats', {});
        const last = this.safeNumber(stats, 'lastPrice');
        return this.safeTicker({
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'high': this.safeNumber(stats, '24h_highPrice'),
            'low': this.safeNumber(stats, '24h_lowPrice'),
            'bid': this.safeNumber(stats, 'bidPrice'),
            'ask': this.safeNumber(stats, 'askPrice'),
            'last': last,
            'close': last,
            'baseVolume': this.safeNumber(stats, '24h_volume'),
            'quoteVolume': this.safeNumber(stats, '24h_quoteVolume'),
            'info': ticker,
        }, market);
    }
    async fetchTicker(symbol, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        const response = await this.request('v1/markets', 'public', 'GET', params);
        const result = this.safeDict(response, 'result', {});
        const symbols = this.safeDict(result, 'symbols', {});
        const data = this.safeDict(symbols, market['id'], {});
        return this.parseTicker(data, market);
    }
    async fetchTickers(symbols = undefined, params = {}) {
        await this.loadMarkets();
        const response = await this.request('v1/markets', 'public', 'GET', params);
        const result = this.safeDict(response, 'result', {});
        const symbolsData = this.safeDict(result, 'symbols', {});
        const keys = Object.keys(symbolsData);
        const tickers = {};
        for (let i = 0; i < keys.length; i++) {
            const id = keys[i];
            const market = this.safeValue(this.markets_by_id, id);
            if (market !== undefined) {
                const ticker = this.parseTicker(symbolsData[id], market);
                tickers[market['symbol']] = ticker;
            }
        }
        return tickers;
    }
    async fetchBalance(params = {}) {
        await this.loadMarkets();
        const response = await this.request('v1/account/balances', 'private', 'GET', params);
        const result = this.safeDict(response, 'result', {});
        const balances = { 'info': response };
        const values = Object.values(result);
        for (let i = 0; i < values.length; i++) {
            const item = values[i];
            if ((item === null) || (typeof item !== 'object')) {
                continue;
            }
            const balance = item;
            const code = this.safeString(balance, 'asset');
            if (code === undefined) {
                continue;
            }
            const total = this.safeNumber(balance, 'balance');
            const free = this.safeNumber(balance, 'available');
            const used = this.safeNumber(balance, 'freeze');
            balances[code] = { 'free': free, 'used': used, 'total': total };
        }
        return this.safeBalance(balances);
    }
    async fetchOHLCV(symbol, timeframe = '5m', since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        const resolutionMap = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '1h': '60',
            '4h': '240',
            '8h': '480',
            '12h': '720',
            '1d': '1D',
            '2d': '2D',
            '3d': '3D',
        };
        const request = {
            'symbol': market['id'],
            'resolution': resolutionMap[timeframe],
        };
        if (since !== undefined) {
            request['from'] = Math.floor(since / 1000);
        }
        if (limit !== undefined) {
            request['to'] = Math.floor(this.milliseconds() / 1000);
        }
        const response = await this.request('v1/udf/history', 'public', 'GET', this.extend(request, params));
        const result = [];
        if (response && response.t && response.o && response.h && response.l && response.c && response.v) {
            for (let i = 0; i < response.t.length; i++) {
                result.push([
                    response.t[i] * 1000,
                    response.o[i],
                    response.h[i],
                    response.l[i],
                    response.c[i],
                    response.v[i],
                ]);
            }
        }
        return result;
    }
    async createOrder(symbol, type, side, amount, price = undefined, params = {}) {
        await this.loadMarkets();
        const market = this.market(symbol);
        const request = {
            'symbol': market['id'],
            'side': side,
            'type': type, // limit or market
            'quantity': this.amountToPrecision(symbol, amount),
        };
        if (price !== undefined) {
            request['price'] = this.priceToPrecision(symbol, price);
        }
        const response = await this.request('v1/account/orders', 'private', 'POST', this.extend(request, params));
        const orderData = this.safeDict(response, 'result', response);
        return this.parseOrder(orderData, market);
    }
    async cancelOrder(id, symbol = undefined, params = {}) {
        const request = { 'client_id': id };
        const response = await this.request('v1/account/orders', 'private', 'DELETE', this.extend(request, params));
        return response;
    }
    parseOrder(order, market = undefined) {
        const id = this.safeString(order, 'clientOrderId');
        const timestamp = this.safeInteger(order, 'transactTime');
        const symbol = this.safeString(market, 'symbol');
        return this.safeOrder({
            'id': id,
            'clientOrderId': id,
            'info': order,
            'timestamp': timestamp,
            'datetime': this.iso8601(timestamp),
            'status': this.safeStringLower(order, 'status'),
            'symbol': symbol,
            'type': this.safeStringLower(order, 'type'),
            'side': this.safeStringLower(order, 'side'),
            'price': this.safeNumber(order, 'price'),
            'amount': this.safeNumber(order, 'origQty'),
            'filled': this.safeNumber(order, 'executedQty'),
            'remaining': undefined,
            'cost': undefined,
            'fee': undefined,
            'trades': undefined,
        }, market);
    }
    async fetchOpenOrders(symbol = undefined, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets();
        let market = undefined;
        if (symbol !== undefined) {
            market = this.market(symbol);
        }
        const response = await this.request('v1/account/openOrders', 'private', 'GET', params);
        const result = this.safeDict(response, 'result', {});
        const orders = this.safeList(result, 'orders', []);
        return this.parseOrders(orders, market, since, limit);
    }
}
