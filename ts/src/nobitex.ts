import Exchange from './abstract/nobitex.js';
import { OrderNotFound, NotSupported } from './base/errors.js';
import type {
    Balances,
    Dict,
    Int,
    MarketInterface,
    OHLCV,
    Order,
    OrderBook,
    Str,
    Ticker,
    Tickers,
    Trade,
} from './base/types.js';

export default class nobitex extends Exchange {
    override describe (): any {
        return this.deepExtend (super.describe (), {
            'id': 'nobitex',
            'name': 'Nobitex',
            'countries': [ 'IR' ],
            'rateLimit': 100,
            'certified': false,
            'has': {
                'CORS': undefined,
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'option': false,
                'fetchMarkets': true,
                'fetchTicker': true,
                'fetchTickers': true,
                'fetchOrderBook': true,
                'fetchOHLCV': false,
                'fetchTrades': true,
                'fetchBalance': true,
                'createOrder': true,
                'fetchOrder': true,
                'cancelOrder': true,
                'fetchOpenOrders': true,
                'fetchClosedOrders': true,
                'fetchOrders': true,
                'fetchMyTrades': true,
                'fetchTradingFee': false,
                'fetchTradingFees': false,
            },
            'urls': {
                'logo': 'https://nobitex.ir/assets/images/logo.svg',
                'api': {
                    'public': 'https://apiv2.nobitex.ir',
                    'private': 'https://apiv2.nobitex.ir',
                },
                'www': 'https://nobitex.ir',
                'doc': [ 'https://apidocs.nobitex.ir' ],
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
            'requiredCredentials': {
                'apiKey': true,
                'secret': false,
            },
            'options': {
                'defaultType': 'spot',
            },
        });
    }

    override sign (path: string, api: string = 'public', method: string = 'GET', params: Dict = {}, headers: Dict = {}, body: Str = undefined): any {
        let url = this.urls['api'][api] + '/' + this.implodeParams (path, params);
        const query = this.omit (params, this.extractParams (path));
        if (Object.keys (query).length) {
            if (method === 'GET') {
                url += '?' + this.urlencode (query);
            }
        }
        if (Object.keys (headers).length === 0) {
            headers = {};
        }
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';
        if (api === 'private') {
            this.checkRequiredCredentials ();
            headers['Authorization'] = 'Token ' + this.apiKey;
            if (method === 'POST') {
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
            }
        }
        return { 'url': url, 'method': method, 'body': body, 'headers': headers };
    }

    override async fetchMarkets (params = {}): Promise<MarketInterface[]> {
        const response = await this.request ('market/stats', 'public', 'GET', params);
        const stats = this.safeDict (response, 'stats', {});
        const keys = Object.keys (stats);
        const markets: MarketInterface[] = [];
        for (let i = 0; i < keys.length; i++) {
            const id = keys[i];
            const parts = id.split ('-');
            if (parts.length !== 2) {
                continue;
            }
            const baseId = parts[0];
            const quoteId = parts[1];
            const base = this.safeCurrencyCode (baseId);
            const quote = this.safeCurrencyCode (quoteId);
            markets.push ({
                'id': id,
                'symbol': base + '/' + quote,
                'base': base,
                'quote': quote,
                'settle': undefined,
                'baseId': baseId,
                'quoteId': quoteId,
                'settleId': undefined,
                'type': 'spot',
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'option': false,
                'active': true,
                'contract': false,
                'linear': undefined,
                'inverse': undefined,
                'subType': undefined,
                'taker': undefined,
                'maker': undefined,
                'contractSize': undefined,
                'expiry': undefined,
                'expiryDatetime': undefined,
                'strike': undefined,
                'optionType': undefined,
                'precision': {
                    'amount': this.parseNumber ('0.000001'),
                    'price': this.parseNumber ('1'),
                    'cost': undefined,
                },
                'limits': {
                    'leverage': { 'min': undefined, 'max': undefined },
                    'amount': { 'min': undefined, 'max': undefined },
                    'price': { 'min': undefined, 'max': undefined },
                    'cost': { 'min': undefined, 'max': undefined },
                },
                'marginModes': {
                    'isolated': false,
                    'cross': false,
                },
                'created': undefined,
                'info': stats[id],
            });
        }
        return markets;
    }

    override parseTicker (ticker: Dict, market: MarketInterface | undefined = undefined): Ticker {
        const timestamp = this.milliseconds ();
        const symbol = this.safeString (market, 'symbol');
        return this.safeTicker ({
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'high': this.safeNumber (ticker, 'dayHigh'),
            'low': this.safeNumber (ticker, 'dayLow'),
            'bid': this.safeNumber (ticker, 'bestBuy'),
            'bidVolume': undefined,
            'ask': this.safeNumber (ticker, 'bestSell'),
            'askVolume': undefined,
            'vwap': undefined,
            'open': this.safeNumber (ticker, 'dayOpen'),
            'close': this.safeNumber (ticker, 'latest'),
            'last': this.safeNumber (ticker, 'latest'),
            'previousClose': undefined,
            'change': undefined,
            'percentage': this.safeNumber (ticker, 'dayChange'),
            'average': undefined,
            'baseVolume': this.safeNumber (ticker, 'volumeSrc'),
            'quoteVolume': this.safeNumber (ticker, 'volumeDst'),
            'info': ticker,
        }, market);
    }

    override async fetchTicker (symbol: string, params = {}): Promise<Ticker> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const request: Dict = {
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
        };
        const response = await this.request ('market/stats', 'public', 'GET', this.extend (request, params));
        const stats = this.safeDict (response, 'stats', {});
        const tickerKey = market['baseId'] + '-' + market['quoteId'];
        const ticker = this.safeDict (stats, tickerKey, {});
        return this.parseTicker (ticker, market);
    }

    override async fetchTickers (symbols: Str[] | undefined = undefined, params = {}): Promise<Tickers> {
        await this.loadMarkets ();
        const result: Tickers = {};
        for (const symbol in this.markets) {
            const market = this.markets[symbol];
            const info = this.safeDict (market, 'info');
            if (info !== undefined) {
                result[symbol] = this.parseTicker (info, market);
            }
        }
        return result;
    }

    override async fetchOrderBook (symbol: string, limit: Int = undefined, params = {}): Promise<OrderBook> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const requestSymbol = market['baseId'].toUpperCase () + market['quoteId'].toUpperCase ();
        const response = await this.request ('v3/orderbook/' + requestSymbol, 'public', 'GET', params);
        return this.parseOrderBook (response, market['symbol']);
    }

    override async fetchOHLCV (symbol: string, timeframe: string = '1d', since: Int = undefined, limit: Int = undefined, params = {}): Promise<OHLCV[]> {
        throw new NotSupported (this.id + ' fetchOHLCV() is not supported by the Nobitex API.');
    }

    override async fetchTrades (symbol: string, since: Int = undefined, limit: Int = undefined, params = {}): Promise<Trade[]> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const requestSymbol = market['baseId'].toUpperCase () + market['quoteId'].toUpperCase ();
        const response = await this.request ('v2/trades/' + requestSymbol, 'public', 'GET', params);
        return this.parseTrades (response, market, since, limit);
    }

    override async fetchBalance (params = {}): Promise<Balances> {
        await this.loadMarkets ();
        const response = await this.request ('users/wallets/list', 'private', 'POST', params);
        const wallets = this.safeList (response, 'wallets', []);
        const result: Dict = { 'info': response };
        for (let i = 0; i < wallets.length; i++) {
            const wallet = wallets[i];
            const currencyId = this.safeString (wallet, 'currency');
            const code = this.safeCurrencyCode (currencyId);
            // استفاده از safeNumber به جای safeString و تفریق استاندارد
            const total = this.safeNumber (wallet, 'balance');
            const free = this.safeNumber (wallet, 'activeBalance');
            let used = undefined;
            if (total !== undefined && free !== undefined) {
                used = total - free;
            }
            result[code] = {
                'free': free,
                'used': used,
                'total': total,
            };
        }
        return this.safeBalance (result);
    }

    parseOrderStatus (status: Str): Str {
        const statuses: Dict = {
            'open': 'open',
            'active': 'open',
            'done': 'closed',
            'filled': 'closed',
            'canceled': 'canceled',
            'cancelled': 'canceled',
        };
        return this.safeString (statuses, status, status);
    }

    override parseOrder (order: Dict, market: MarketInterface | undefined = undefined): Order {
        const id = this.safeString (order, 'id');
        const timestamp = this.safeTimestamp (order, 'createdAt');
        const symbol = this.safeString (market, 'symbol');
        return this.safeOrder ({
            'id': id,
            'clientOrderId': undefined,
            'info': order,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'lastTradeTimestamp': undefined,
            'status': this.parseOrderStatus (this.safeString (order, 'status')),
            'symbol': symbol,
            'type': this.safeString (order, 'type'),
            'timeInForce': undefined,
            'side': this.safeStringLower (order, 'type'),
            'price': this.safeNumber (order, 'price'),
            'amount': this.safeNumber (order, 'amount'),
            'filled': this.safeNumber (order, 'filledAmount'),
            'remaining': undefined,
            'cost': undefined,
            'average': undefined,
            'trades': [],
            'fee': undefined,
        }, market);
    }

    override async createOrder (symbol: string, type: string, side: string, amount: number, price: number | undefined = undefined, params = {}): Promise<Order> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const request: Dict = {
            'type': type,
            'srcCurrency': market['baseId'],
            'dstCurrency': market['quoteId'],
            'amount': amount,
            'side': side,
        };
        if (price !== undefined) {
            request['price'] = price;
        }
        const response = await this.request ('market/orders/add', 'private', 'POST', this.extend (request, params));
        const order = this.safeDict (response, 'order', response);
        return this.parseOrder (order, market);
    }

    override async cancelOrder (id: string, symbol: Str = undefined, params = {}): Promise<Order> {
        await this.loadMarkets ();
        const request: Dict = {
            'order': id,
            'status': 'canceled',
        };
        const response = await this.request ('market/orders/update-status', 'private', 'POST', this.extend (request, params));
        return response;
    }

    override async fetchOrder (id: string, symbol: Str = undefined, params = {}): Promise<Order> {
        await this.loadMarkets ();
        const orders = await this.fetchOrders (symbol, undefined, undefined, params);
        for (let i = 0; i < orders.length; i++) {
            if (orders[i]['id'] === String (id)) {
                return orders[i];
            }
        }
        throw new OrderNotFound ('Order not found: ' + String (id));
    }

    override async fetchOrders (symbol: Str = undefined, since: Int = undefined, limit: Int = undefined, params = {}): Promise<Order[]> {
        await this.loadMarkets ();
        let market = undefined;
        const request: Dict = {};
        if (symbol !== undefined) {
            market = this.market (symbol);
            request['srcCurrency'] = market['baseId'];
            request['dstCurrency'] = market['quoteId'];
        }
        const response = await this.request ('market/orders/list', 'private', 'POST', this.extend (request, params));
        const orders = this.safeList (response, 'orders', []);
        return this.parseOrders (orders, market, since, limit);
    }

    override async fetchOpenOrders (symbol: Str = undefined, since: Int = undefined, limit: Int = undefined, params = {}): Promise<Order[]> {
        const request: Dict = { 'status': 'open' };
        return this.fetchOrders (symbol, since, limit, this.extend (request, params));
    }

    override async fetchClosedOrders (symbol: Str = undefined, since: Int = undefined, limit: Int = undefined, params = {}): Promise<Order[]> {
        const request: Dict = { 'status': 'done' };
        return this.fetchOrders (symbol, since, limit, this.extend (request, params));
    }

    override async fetchMyTrades (symbol: Str = undefined, since: Int = undefined, limit: Int = undefined, params = {}): Promise<Trade[]> {
        const request: Dict = { 'status': 'done' };
        const orders = await this.fetchOrders (symbol, since, limit, this.extend (request, params));
        return orders as unknown as Trade[];
    }
}