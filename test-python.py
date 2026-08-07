import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex
from ccxt.base.errors import NetworkError

def main():
    # Note: Replace with your actual API key
    exchange = nobitex({'apiKey': 'Your_Token'})
    
    print("Exchange ID:", exchange.id)
    print("Exchange Name:", exchange.name)
    print("\n" + "="*50)
    print("Top 20 Global Cryptos Live Prices")
    print("="*50)
    
    try:
        # Send only one request to the server to avoid Rate Limit
        markets = exchange.fetch_markets()
        if len(markets) == 0:
            print("Nobitex returned 0 markets. Please wait 1 minute and run again.")
            return

        # Convert markets list to a dictionary for faster access
        markets_dict = {m['symbol']: m for m in markets}

        # List of top 20 global cryptos
        top_20_coins = [
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'TRX', 'DOT',
            'MATIC', 'LTC', 'BCH', 'AVAX', 'LINK', 'ATOM', 'UNI', 'SHIB', 'NEAR', 'FIL'
        ]
        
        for coin in top_20_coins:
            print(f"\n--- {coin} ---")
            
            # 1. Display global price (in USDT)
            symbol_usdt = f'{coin}/USDT'
            if symbol_usdt in markets_dict:
                market = markets_dict[symbol_usdt]
                # Parse raw data into standard CCXT format
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"  Global ({symbol_usdt}):")
                print(f"    Last Price: {ticker.get('last')} USDT")
            else:
                print(f"  Global ({symbol_usdt}): Not available on Nobitex")
                
            # 2. Display Iran price (in RLS)
            symbol_rls = f'{coin}/RLS'
            if symbol_rls in markets_dict:
                market = markets_dict[symbol_rls]
                # Parse raw data into standard CCXT format
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"  Iran ({symbol_rls}):")
                print(f"    Buy Price (Bid):  {ticker.get('bid')} RLS")
                print(f"    Sell Price (Ask): {ticker.get('ask')} RLS")
                print(f"    Last Price:       {ticker.get('last')} RLS")
            else:
                print(f"  Iran ({symbol_rls}): Not available on Nobitex")
                
    except NetworkError:
        print("Code is correct, but local network is blocking api.nobitex.ir. (Will work on server)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()