import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.nobitex import nobitex

API_KEY = '040dff9101b461a49cb50db31bf582875466f9f4'

exchange = nobitex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Nobitex...")
    exchange.load_markets()
    
    symbol = '1K_SHIB/RLS'
    
    # ۱. گرفتن موجودی 1K_SHIB
    print("\n--- Fetching 1K_SHIB Balance ---")
    balance = exchange.fetch_balance()
    # در نوبیتکس ممکن است ارز در کیف پول به صورت 1K_SHIB یا SHIB ذخیره شده باشد
    shib_free = balance.get('1K_SHIB', {}).get('free', 0)
    if shib_free == 0:
        shib_free = balance.get('SHIB', {}).get('free', 0)
        
    print(f"Available 1K_SHIB Balance: {shib_free}")
    
    if shib_free == 0 or shib_free < 1:
        print("❌ No 1K_SHIB available to sell. Make sure you have it in your wallet.")
        sys.exit()
        
    # ۲. گرفتن قیمت لحظه‌ای
    print(f"\n--- Fetching {symbol} Price ---")
    ticker = exchange.fetch_ticker(symbol)
    live_price = ticker['last']
    print(f"Live price for {symbol}: {live_price:,.2f}")
    
    # ۳. محاسبه قیمت لیمیت (1% پایین‌تر از بازار برای فروش، تا فورا پر شود)
    limit_price = int(live_price * 0.99)
    
    print(f"\nPlacing REAL SELL order: {int(shib_free)} {symbol} @ {limit_price:,.2f} RLS")
    
    # ۴. ثبت سفارش فروش
    order = exchange.create_order(symbol, 'limit', 'sell', int(shib_free), limit_price)
    print("\n✅ Sell Order Success! Order ID:", order.get('id'))
    print("Check your Nobitex account to see your RLS balance increase!")

except Exception as e:
    print(f"\n❌ Error: {e}")
