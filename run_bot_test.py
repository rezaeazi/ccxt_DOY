import time
from bot_manager import TradingBotManager

def main():
    NOBITEX_TOKEN = 'Your_Token_Here'.strip()
    
    if NOBITEX_TOKEN == 'YOUR_TOKEN_HERE':
        print("❌ Please place your Nobitex Token in the code!")
        return
        
    print("🚀 Initializing Bot Manager...")
    bot = TradingBotManager(api_key=NOBITEX_TOKEN)
    
    while True:
        print("\n" + "="*40)
        print("📋 TEST CONTROL PANEL (Simulation Enabled)")
        print("="*40)
        print("1. Place a Smart Limit Order")
        print("2. View Open Orders")
        print("3. Cancel ALL Open Orders")
        print("4. View Trade History & PnL")
        print("5. Exit")
        print("="*40)
        
        choice = input("Select an option (1-5): ")
        
        if choice == '1':
            symbol = input("Enter Symbol (e.g., BTC/USDT): ").upper()
            side = input("Enter Side (buy/sell): ").lower()
            amount = float(input("Enter Amount (e.g., 0.002): "))
            
            try:
                ticker = bot.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                if not current_price:
                    print("❌ Could not fetch current price.")
                    continue
                    
                print(f"Current market price for {symbol}: {current_price}")
                
                if side == 'buy':
                    limit_price = current_price * 0.99
                else:
                    limit_price = current_price * 1.01
                    
                print(f"Placing {side} order at limit price: {limit_price:,.2f}")
                
                # Enable simulation mode (simulate=True)
                order = bot.place_order(symbol, side, amount, limit_price, simulate=True)
                
                if order and order.get('id'):
                    print(f"✅ Success! Order ID: {order.get('id')}")
                    time.sleep(1)
                else:
                    print("❌ Order failed.")
            except Exception as e:
                print(f"❌ Error: {e}")
            
        elif choice == '2':
            bot.get_open_orders()
            
        elif choice == '3':
            print("\n⏳ Cancelling all open orders...")
            # Clear simulated orders if they exist
            if hasattr(bot, 'sim_orders'):
                bot.sim_orders = []
                print("✅ Simulated orders cleared.")
            bot.cancel_all_open_orders()
            
        elif choice == '4':
            trades = bot.get_trade_history(limit=50)
            if trades:
                bot.calculate_pnl(trades)
            else:
                print("No trade history found.")
                
        elif choice == '5':
            print("Exiting...")
            break
            
        else:
            print("❌ Invalid choice.")

if __name__ == '__main__':
    main()