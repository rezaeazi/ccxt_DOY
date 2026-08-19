import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

API_KEY = 'Am0Xf2b7IEBP1lsS6GOXRjWWVl0bKYoZSiZI3gMN'

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()
    
    # ۱. گرفتن موجودی تومان (TMN)
    print("\n--- Fetching TMN Balance ---")
    balance = exchange.fetch_balance()
    tmn_free = balance.get('TMN', {}).get('free', 0)
    print(f"Available TMN Balance: {tmn_free:,.2f}")
    
    if tmn_free < 10000:
        print("⚠️ Warning: Your TMN balance is very low. The order might fail due to insufficient funds.")
        
    # ۲. گرفتن قیمت لحظه‌ای USDT/TMN
    symbol = 'USDT/TMN'
    print(f"\n--- Fetching {symbol} Price ---")
    ticker = exchange.fetch_ticker(symbol)
    live_price = ticker['last']
    print(f"Live price for {symbol}: {live_price:,.2f} TMN")
    
    # ۳. محاسبه مقدار خرید (مثلاً خرید 1 USDT برای تست)
    buy_amount = 1  # خرید 1 تتر
    
    # قیمت لیمیت را 1% بالاتر از بازار می‌گذاریم تا سفارش فورا پر شود (Market Order تقریبی)
    limit_price = live_price * 1.01
    
    print(f"\nPlacing REAL BUY order: {buy_amount} {symbol} @ {limit_price:,.2f} TMN")
    
    # ۴. ثبت سفارش واقعی
    order = exchange.create_order(symbol, 'limit', 'buy', buy_amount, limit_price)
    print("\n✅ Order Success! Order ID:", order.get('id'))
    print("Check your Wallex account to see the USDT balance!")

except Exception as e:
    print(f"\n❌ Error: {e}")
