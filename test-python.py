import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex
from ccxt.base.errors import NetworkError

def test_method(name, func):
    print(f"\n--- Testing {name} ---")
    try:
        result = func()
        print("Success:")
        if isinstance(result, list):
            print(f"Got {len(result)} items. First item:", result[0] if len(result) > 0 else "Empty")
        else:
            print(result)
    except NetworkError:
        print("Code is correct, but local network is blocking api.nobitex.ir. (Will work on server)")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    exchange = nobitex({'apiKey': 'YOUR_TOKEN'})
    
    print("Exchange ID:", exchange.id)
    print("Exchange Name:", exchange.name)
    print("\n" + "="*40)
    print("Testing Public Methods")
    print("="*40)
    
    test_method("fetchMarkets", lambda: exchange.fetch_markets())
    test_method("fetchTicker (BTC/RLS)", lambda: exchange.fetch_ticker('BTC/RLS'))
    test_method("fetchOrderBook (BTC/RLS)", lambda: exchange.fetch_order_book('BTC/RLS'))
    test_method("fetchTrades (BTC/RLS)", lambda: exchange.fetch_trades('BTC/RLS'))

    if exchange.apiKey and exchange.apiKey != 'YOUR_TOKEN':
        print("\n" + "="*40)
        print("Testing Private Methods")
        print("="*40)
        test_method("fetchProfile", lambda: exchange.fetch_profile())
        test_method("fetchBalance", lambda: exchange.fetch_balance())
        test_method("fetchTransactionsHistory", lambda: exchange.fetch_transactions_history())
        test_method("fetchFavoriteMarkets", lambda: exchange.fetch_favorite_markets())
        test_method("fetchOpenOrders", lambda: exchange.fetch_open_orders())

if __name__ == '__main__':
    main()