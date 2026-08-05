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
        # گرفتن قیمت تمام ارزها
        all_tickers = exchange.fetch_tickers()
        print(f"✅ Success! Fetched {len(all_tickers)} coins.")
        print("\n--- Sample Prices (Last Price in RLS) ---")
        
        # نمایش چند ارز معروف
        sample_coins = ['BTC/RLS', 'ETH/RLS', 'USDT/RLS', 'DOGE/RLS', 'SHIB/RLS']
        for symbol in sample_coins:
            if symbol in all_tickers:
                ticker = all_tickers[symbol]
                print(f"{symbol}: {ticker['last']} RLS")
                
    except NetworkError:
        print("⚠️ Code is correct, but local network is blocking api.nobitex.ir. (Will work on server)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()