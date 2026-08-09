import Exchange from './abstract/nobitex.js';
import type { Balances, Dict, Int, MarketInterface, OHLCV, Order, OrderBook, Str, Ticker, Tickers, Trade } from './base/types.js';
export default class nobitex extends Exchange {
    describe(): any;
    sign(path: string, api?: string, method?: string, params?: Dict, headers?: Dict, body?: Str): any;
    fetchMarkets(params?: {}): Promise<MarketInterface[]>;
    parseTicker(ticker: Dict, market?: MarketInterface | undefined): Ticker;
    fetchTicker(symbol: string, params?: {}): Promise<Ticker>;
    fetchTickers(symbols?: Str[] | undefined, params?: {}): Promise<Tickers>;
    fetchOrderBook(symbol: string, limit?: Int, params?: {}): Promise<OrderBook>;
    fetchOHLCV(symbol: string, timeframe?: string, since?: Int, limit?: Int, params?: {}): Promise<OHLCV[]>;
    fetchTrades(symbol: string, since?: Int, limit?: Int, params?: {}): Promise<Trade[]>;
    fetchBalance(params?: {}): Promise<Balances>;
    parseOrderStatus(status: Str): Str;
    parseOrder(order: Dict, market?: MarketInterface | undefined): Order;
    createOrder(symbol: string, type: string, side: string, amount: number, price?: number | undefined, params?: {}): Promise<Order>;
    cancelOrder(id: string, symbol?: Str, params?: {}): Promise<Order>;
    fetchOrder(id: string, symbol?: Str, params?: {}): Promise<Order>;
    fetchOrders(symbol?: Str, since?: Int, limit?: Int, params?: {}): Promise<Order[]>;
    fetchOpenOrders(symbol?: Str, since?: Int, limit?: Int, params?: {}): Promise<Order[]>;
    fetchClosedOrders(symbol?: Str, since?: Int, limit?: Int, params?: {}): Promise<Order[]>;
    fetchMyTrades(symbol?: Str, since?: Int, limit?: Int, params?: {}): Promise<Trade[]>;
}
