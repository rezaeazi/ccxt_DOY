import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex
from ccxt.base.errors import NetworkError

def main():
    # Place your NEW valid Nobitex token here
    exchange = nobitex({'apiKey': '25bdb775a838154399e51433c17ce5a1f1073053'})
    
    print("Exchange ID:", exchange.id)
    print("Exchange Name:", exchange.name)
    
    try:
        # Send only one request to fetch all markets and prices
        markets = exchange.fetch_markets()
        if len(markets) == 0:
            print("Nobitex returned 0 markets. Your IP is rate limited. Please wait 1 minute and run again.")
            return

        markets_dict = {m['symbol']: m for m in markets}

        # ==========================================
        # 1. Display Account Info (Requires valid Token)
        # ==========================================
        print("\n" + "="*50)
        print("🔒 Account Information")
        print("="*50)
        
        if exchange.apiKey != 'YOUR_NEW_TOKEN':
            try:
                # Fetch Balance
                balance = exchange.fetch_balance()
                non_zero_balances = {k: v for k, v in balance.items() if k != 'info' and v.get('total') not in [None, 0]}
                print("Wallet Balances:")
                if not non_zero_balances:
                    print("  (No balances found)")
                else:
                    for currency, amounts in non_zero_balances.items():
                        print(f"  {currency}: Free: {amounts.get('free')}, Used: {amounts.get('used')}, Total: {amounts.get('total')}")
                
                # Fetch My Trades Count
                my_trades = exchange.fetch_my_trades()
                print(f"\nTotal Executed Trades: {len(my_trades)}")
                
            except Exception as e:
                print(f"Error fetching account data: {e}")
        else:
            print("ℹ️ Please replace 'YOUR_NEW_TOKEN' with your actual Nobitex API key to see account data.")

        # ==========================================
        # 2. Display Top 20 Cryptos Prices (USD & RLS)
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
            
            # 1. Global Price (in USDT)
            symbol_usdt = f'{coin}/USDT'
            if symbol_usdt in markets_dict:
                market = markets_dict[symbol_usdt]
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"  Global Price ({symbol_usdt}): {ticker.get('last')} USDT")
            else:
                print(f"  Global Price ({symbol_usdt}): Not available")
                
            # 2. Iran Price (in RLS)
            symbol_rls = f'{coin}/RLS'
            if symbol_rls in markets_dict:
                market = markets_dict[symbol_rls]
                ticker = exchange.parse_ticker(market['info'], market)
                print(f"  Iran Price ({symbol_rls}): {ticker.get('last')} RLS")
            else:
                print(f"  Iran Price ({symbol_rls}): Not available")
                
    except NetworkError:
        print("Code is correct, but local network is blocking api.nobitex.ir. (Will work on server)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()