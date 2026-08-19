import Exchange from './abstract/wallex.js';
import type { Balances, Dict, Int, MarketInterface, OHLCV, Order, Str, Ticker, Tickers } from './base/types.js';
export default class wallex extends Exchange {
    describe(): any;
    sign(path: string, api?: string, method?: string, params?: Dict, headers?: Dict, body?: Str): any;
    fetchMarkets(params?: {}): Promise<MarketInterface[]>;
    parseTicker(ticker: Dict, market?: MarketInterface | undefined): Ticker;
    fetchTicker(symbol: string, params?: {}): Promise<Ticker>;
    fetchTickers(symbols?: Str[] | undefined, params?: {}): Promise<Tickers>;
    fetchBalance(params?: {}): Promise<Balances>;
    fetchOHLCV(symbol: string, timeframe?: string, since?: any, limit?: any, params?: {}): Promise<OHLCV[]>;
    createOrder(symbol: string, type: string, side: string, amount: number, price?: number | undefined, params?: {}): Promise<Order>;
    cancelOrder(id: string, symbol?: Str, params?: {}): Promise<Order>;
    parseOrder(order: Dict, market?: MarketInterface | undefined): Order;
    fetchOpenOrders(symbol?: Str, since?: Int, limit?: Int, params?: {}): Promise<Order[]>;
}
