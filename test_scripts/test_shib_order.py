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
    
    # ۱. گرفتن موجودی ریالی
    print("\n--- Fetching RLS Balance ---")
    balance = exchange.fetch_balance()
    rls_free = balance.get('RLS', {}).get('free', 0)
    print(f"Available RLS Balance: {rls_free:,.2f}")
    
    if rls_free < 100000:
        print("❌ Not enough RLS balance to buy SHIB.")
        sys.exit()
        
    # ۲. گرفتن قیمت لحظه‌ای 1K_SHIB
    # در نوبیتکس شیبا با نام 1K_SHIB معامله میشود
    symbol = '1K_SHIB/RLS'
    print(f"\n--- Fetching {symbol} Price ---")
    ticker = exchange.fetch_ticker(symbol)
    live_price = ticker['last']
    print(f"Live price for {symbol}: {live_price:,.2f}")
    
    # ۳. محاسبه مقدار خرید (استفاده از 90% موجودی برای احتیاط در کارمزد)
    spend_rls = rls_free * 0.90
    # چون 1K_SHIB ارز cheap است، حجم باید عدد صحیح (Integer) باشد
    buy_amount = int(spend_rls / live_price)
    
    # قیمت لیمیت را 1% بالاتر از بازار می‌گذاریم تا سفارش فورا پر شود (Market Order تقریبی)
    limit_price = int(live_price * 1.01)
    
    print(f"\nCalculated Buy Amount: {buy_amount} of 1K_SHIB")
    print(f"Placing REAL BUY order: {buy_amount} {symbol} @ {limit_price:,.2f} RLS")
    
    # ۴. ثبت سفارش واقعی
    order = exchange.create_order(symbol, 'limit', 'buy', buy_amount, limit_price)
    print("\n✅ Order Success! Order ID:", order.get('id'))
    print("Check your Nobitex account to see the SHIB balance!")

except Exception as e:
    print(f"\n❌ Error: {e}")
