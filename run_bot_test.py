import time
from bot_manager import TradingBotManager

def main():
    print("Select Exchange to connect:")
    print("1. Nobitex")
    print("2. Wallex")
    ex_choice = input("Enter 1 or 2: ").strip()

    if ex_choice == '1':
        exchange_id = 'nobitex'
    elif ex_choice == '2':
        exchange_id = 'wallex'
    else:
        print("❌ Invalid choice. Exiting.")
        return

    NOBITEX_TOKEN = 'Your_Token_Here'.strip() # میتوانید توکن والکس یا نوبیتکس را اینجا بگذارید
    
    print(f"🚀 Initializing Bot Manager for {exchange_id}...")
    bot = TradingBotManager(exchange_id=exchange_id, api_key=NOBITEX_TOKEN)
    
    while True:
        print("\n" + "="*40)
        print(f"📋 TEST CONTROL PANEL ({exchange_id.upper()})")
        print("="*40)
        print("1. Place an Order (Live Price Verification)")
        print("2. View Open Orders")
        print("3. Cancel ALL Open Orders")
        print("4. View Trade History & PnL")
        print("5. Exit")
        print("="*40)
        
        choice = input("Select an option (1-5): ")
        
        if choice == '1':
            symbol = input("Enter Symbol (e.g., BTC/USDT): ").upper()
            live_price = bot.get_live_price(symbol)
            if not live_price:
                continue
            side = input("Enter Side (buy/sell): ").lower()
            amount = float(input("Enter Amount (e.g., 0.002): "))
            
            user_price_input = input(f"Enter your Limit Price (Press Enter to auto-use ~1% {'below' if side == 'buy' else 'above'} live price): ").strip().lower()
            if user_price_input == "" or user_price_input == "auto":
                limit_price = live_price * 0.99 if side == 'buy' else live_price * 1.01
                print(f"Auto-calculated Limit Price: {limit_price:,.2f}")
            else:
                limit_price = float(user_price_input)
                
            print(f"\nPlacing {side} order at limit price: {limit_price:,.2f}")
            order = bot.place_order(symbol, side, amount, limit_price, simulate=True)
            
            if order and order.get('id'):
                print(f"✅ Success! Order ID: {order.get('id')}")
                time.sleep(1)
            else:
                print("❌ Order failed.")
            
        elif choice == '2':
            bot.get_open_orders()
            
        elif choice == '3':
            print("\n⏳ Cancelling all open orders...")
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