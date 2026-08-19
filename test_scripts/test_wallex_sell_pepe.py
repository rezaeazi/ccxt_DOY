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
    wallex_symbol = market['id']
    
    # ۱. گرفتن موجودی پپه
    print("\n--- Fetching PEPE Balance ---")
    balance = exchange.fetch_balance()
    pepe_free = float(balance.get('PEPE', {}).get('free', 0))
    print(f"Available PEPE Balance: {pepe_free}")
    
    if pepe_free < 1:
        print("❌ No PEPE available to sell!")
        print("⚠️ Make sure your previous BUY order was filled. Check your Wallex open orders.")
        sys.exit()
        
    # ۲. گرفتن قیمت لحظه‌ای و محاسبه قیمت فروش (1% بالاتر برای سود)
    print(f"\n--- Fetching {symbol} Price ---")
    ticker = exchange.fetch_ticker(symbol)
    live_price = float(ticker['last'])
    
    # محاسبه قیمت فروش و فرمت کردن آن (جلوگیری از فرمت علمی)
    sell_price_float = live_price * 1.01
    limit_price = f"{sell_price_float:.8f}".rstrip('0').rstrip('.')
    
    print(f"Live price: {live_price}")
    print(f"Sell Limit Price (1% higher): {limit_price} USDT")
    
    # ۳. محاسبه مقدار فروش (به صورت عدد صحیح)
    sell_amount = int(pepe_free)
    sell_amount_str = str(sell_amount)
    
    print(f"\nCalculated Sell Amount: {sell_amount_str} PEPE (Integer)")
    print(f"Placing REAL SELL order: {sell_amount_str} {symbol} @ {limit_price} USDT")
    
    # ۴. ارسال مستقیم درخواست فروش به والکس
    request_body = {
        'symbol': wallex_symbol,
        'side': 'sell',
        'type': 'limit',
        'quantity': sell_amount_str,
        'price': limit_price
    }
    
    response = exchange.request('v1/account/orders', 'private', 'POST', request_body)
    order_id = response.get('result', {}).get('clientOrderId')
    
    print("\n✅ Sell Order Success! Order ID:", order_id)
    print("Check your Wallex account to see your USDT balance increase!")

except Exception as e:
    print(f"\n❌ Error: {e}")
