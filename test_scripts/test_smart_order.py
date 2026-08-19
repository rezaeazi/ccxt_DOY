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
    
    # ۱. بررسی موجودی واقعی
    print("\n--- Fetching Balance ---")
    balance = exchange.fetch_balance()
    non_zero = {k: v for k, v in balance.items() if k != 'info' and isinstance(v, dict) and v.get('total') not in [None, 0]}
    
    if not non_zero:
        print("❌ No balance found in your account!")
    else:
        print("✅ Your non-zero balances:")
        for cur, val in non_zero.items():
            print(f"  {cur}: Free: {val.get('free')} | Total: {val.get('total')}")
            
    # ۲. ثبت سفارش با ریال (RLS)
    print("\n--- Attempting to place a SMART order on BTC/RLS ---")
    # گرفتن قیمت لحظهای بازار
    ticker = exchange.fetch_ticker('BTC/RLS')
    live_price = ticker['last']
    
    if not live_price:
        print("❌ Could not fetch live price for BTC/RLS")
    else:
        print(f"Live price for BTC/RLS: {live_price:,.2f}")
        
        # محاسبه قیمت لیمیت (1% پایین‌تر از بازار تا خرید کنیم ولی فورا پر نشود)
        limit_price = live_price * 0.99
        amount = 0.001  # حجم خرید
        
        print(f"Placing BUY order: {amount} BTC @ {limit_price:,.2f} RLS")
        
        order = exchange.create_order('BTC/RLS', 'limit', 'buy', amount, limit_price)
        print("✅ Order Success! Order ID:", order.get('id'))

except Exception as e:
    print(f"\n❌ Error: {e}")
