import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

API_KEY = 'YOUR_WALLEX_API_KEY'

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()
    
    symbol = 'PEPE/USDT'
    market = exchange.market(symbol)
    wallex_symbol = market['id']  # گرفتن نام نماد دقیق والکس (مثلا PEPEUSDT)
    
    print("\n--- Fetching USDT Balance ---")
    balance = exchange.fetch_balance()
    usdt_free = float(balance.get('USDT', {}).get('free', 0))
    print(f"Available USDT Balance: {usdt_free}")
    
    if usdt_free < 1:
        print("❌ Not enough USDT balance to buy PEPE.")
        sys.exit()
        
    # ۱. قیمت دقیق درخواستی شما (به صورت استرینگ برای جلوگیری از ارور e-06)
    limit_price = "0.00000252"
    
    # ۲. محاسبه حداکثر مقدار پپه و تبدیل به عدد صحیح (Integer)
    spend_usdt = usdt_free * 0.95  # استفاده از 95% موجودی برای احتیاط در کارمزد
    buy_amount = int(spend_usdt / float(limit_price))  # حذف کامل اعشار
    buy_amount_str = str(buy_amount)
    
    print(f"\nCalculated Buy Amount: {buy_amount_str} PEPE (Integer)")
    print(f"Placing REAL BUY order: {buy_amount_str} {symbol} @ {limit_price} USDT")
    
    # ۳. ارسال مستقیم درخواست به API والکس (دور زدن توابع CCXT)
    request_body = {
        'symbol': wallex_symbol,
        'side': 'buy',
        'type': 'limit',
        'quantity': buy_amount_str,
        'price': limit_price
    }
    
    response = exchange.request('v1/account/orders', 'private', 'POST', request_body)
    order_id = response.get('result', {}).get('clientOrderId')
    
    print("\n✅ Order Success! Order ID:", order_id)
    print("Check your Wallex account to see the PEPE balance!")

except Exception as e:
    print(f"\n❌ Error: {e}")
