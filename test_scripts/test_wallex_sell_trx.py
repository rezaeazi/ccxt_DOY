import sys
import math
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
    
    symbol = 'TRX/USDT'
    market = exchange.market(symbol)
    wallex_symbol = market['id']
    
    print("\n--- Fetching TRX Balance ---")
    balance = exchange.fetch_balance()
    trx_free = float(balance.get('TRX', {}).get('free', 0))
    print(f"Available TRX Balance: {trx_free}")
    
    if trx_free < 1:
        print("❌ Not enough TRX balance to sell.")
        sys.exit()
        
    # ۱. قیمت دقیق درخواستی شما
    limit_price = "0.334"
    
    # ۲. محاسبه مقدار فروش با 1 رقم اعشار (طبق قوانین والکس)
    # استفاده از math.floor برای جلوگیری از ارور کسر موجودی
    truncated_amount = math.floor(trx_free * 10) / 10.0
    sell_amount_str = f"{truncated_amount:.1f}"
    
    print(f"\nPlacing REAL SELL order: {sell_amount_str} TRX @ {limit_price} USDT")
    
    # ۳. ارسال مستقیم درخواست به API والکس
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
    print("Check your Wallex account to see your USDT balance!")

except Exception as e:
    print(f"\n❌ Error: {e}")
