import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

API_KEY = '20103|Am0Xf2b7IEBP1lsS6GOXRjWWVl0bKYoZSiZI3gMN'

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()
    
    symbol = 'PEPE/USDT'
    
    print("\n--- Fetching USDT Balance ---")
    balance = exchange.fetch_balance()
    usdt_free = float(balance.get('USDT', {}).get('free', 0))
    print(f"Available USDT Balance: {usdt_free}")
    
    if usdt_free < 1:
        print("❌ Not enough USDT balance to buy PEPE.")
        sys.exit()
        
    # ۱. قیمت درخواستی شما
    limit_price = 0.00000252
    print(f"\nUsing requested Limit Price: {limit_price}")
    
    # ۲. محاسبه حداکثر مقدار پپه‌ای که می‌توان با موجودی خرید
    # استفاده از 95% موجودی برای احتیاط در کارمزد
    spend_usdt = usdt_free * 0.95
    buy_amount = spend_usdt / limit_price
    
    print(f"Calculated Buy Amount: {buy_amount} PEPE")
    print(f"Placing REAL BUY order: {buy_amount} {symbol} @ {limit_price} USDT")
    
    # ۳. ثبت سفارش واقعی
    order = exchange.create_order(symbol, 'limit', 'buy', buy_amount, limit_price)
    print("\n✅ Order Success! Order ID:", order.get('id'))
    print("Check your Wallex account to see the PEPE balance!")

except Exception as e:
    print(f"\n❌ Error: {e}")
