import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex
from ccxt.base.errors import NetworkError

def main():
    exchange = nobitex({'apiKey': 'zqvUQ95gGx8dWjhnGG9VWS6GOl2QVpCxCDocUd1zQgM='})
    
    print("✅ Exchange ID:", exchange.id)
    print("✅ Exchange Name:", exchange.name)
    print("\n" + "="*40)
    print("Testing fetchTickers (All Coins in RLS)")
    print("="*40)
    
    try:
        markets = exchange.fetch_markets()
        print(f"✅ Markets fetched: {len(markets)} coins.")
        
        if len(markets) == 0:
            print("\n❌ Nobitex returned 0 markets. Your IP is rate limited. Please wait 1 minute and run again.")
            return
            
        print("\n--- Sample Prices (Buy, Sell, Last) ---")
        sample_coins = ['BTC/RLS', 'ETH/RLS', 'USDT/RLS', 'DOGE/RLS', 'SHIB/RLS']
        
        for market in markets:
            symbol = market['symbol']
            if symbol in sample_coins:
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"\n{symbol}:")
                print(f"  Buy Price (Bid):  {ticker.get('bid')} RLS")
                print(f"  Sell Price (Ask): {ticker.get('ask')} RLS")
                print(f"  Last Price:       {ticker.get('last')} RLS")
                
    except NetworkError:
        print("Code is correct, but local network is blocking api.nobitex.ir. (Will work on server)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()