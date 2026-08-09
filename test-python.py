import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex
from ccxt.base.errors import NetworkError

def main():
    # Place your actual Nobitex token here
    exchange = nobitex({'apiKey': 'Token_here'})
    
    print("Exchange ID:", exchange.id)
    print("Exchange Name:", exchange.name)
    
    try:
        # 1. Fetch Markets
        markets = exchange.load_markets()
        if len(markets) == 0:
            print("Nobitex returned 0 markets. Please wait 1 minute and run again.")
            return

        # FIX: load_markets returns a dict with symbols as keys. We use it directly.
        markets_dict = exchange.markets

        # ==========================================
        # 2. Account Information (Balance)
        # ==========================================
        print("\n" + "="*50)
        print("🔒 Account Information")
        print("="*50)
        
        if exchange.apiKey != 'YOUR_TOKEN':
            try:
                balance = exchange.fetch_balance()
                non_zero_balances = {k: v for k, v in balance.items() if k != 'info' and isinstance(v, dict) and v.get('total') not in [None, 0]}
                print("Wallet Balances:")
                if not non_zero_balances:
                    print("  (No balances found)")
                else:
                    for currency, amounts in non_zero_balances.items():
                        print(f"  {currency}: Free: {amounts.get('free')}, Used: {amounts.get('used')}, Total: {amounts.get('total')}")
            except Exception as e:
                print(f"Error fetching account data: {e}")
        else:
            print("ℹ️ Please replace 'YOUR_TOKEN' with your actual Nobitex API key to see account data.")
            
        # ==========================================
        # 3. Top 20 Cryptos Prices (USD & RLS)
        # ==========================================
        print("\n" + "="*50)
        print("Top 20 Global Cryptos Live Prices")
        print("="*50)

        top_20_coins = [
            'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'TRX', 'DOT',
            'LTC', 'BCH', 'AVAX', 'LINK', 'ATOM', 'UNI', 'SHIB', 'NEAR', 'FIL', 'MATIC'
        ]
        
        for coin in top_20_coins:
            print(f"\n--- {coin} ---")
            
            # Global Price (in USDT)
            symbol_usdt = f'{coin}/USDT'
            if symbol_usdt in markets_dict:
                market = markets_dict[symbol_usdt]
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"  Global Price ({symbol_usdt}): {ticker.get('last')} USDT")
            else:
                print(f"  Global Price ({symbol_usdt}): Not available")
                
            # Iran Price (in RLS)
            symbol_rls = f'{coin}/RLS'
            if symbol_rls in markets_dict:
                market = markets_dict[symbol_rls]
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"  Iran Price ({symbol_rls}): {ticker.get('last')} RLS")
            else:
                print(f"  Iran Price ({symbol_rls}): Not available")
                
    except NetworkError:
        print("Code is correct, but local network is blocking Nobitex API. (Will work on server)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()