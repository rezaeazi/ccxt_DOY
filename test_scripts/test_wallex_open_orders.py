import sys
from datetime import datetime
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
    
    print("\n--- 📋 Fetching Open Orders (سفارشات باز) ---")
    
    # گرفتن لیست سفارشات باز با استفاده از متد استاندارد CCXT
    open_orders = exchange.fetch_open_orders()
    
    if not open_orders:
        print("❌ شما هیچ سفارش بازی ندارید.")
    else:
        print(f"✅ شما {len(open_orders)} سفارش باز دارید:\n")
        
        for order in open_orders:
            # استخراج اطلاعات هر سفارش
            order_id = order.get('id', 'N/A')
            symbol = order.get('symbol', 'N/A')
            side = order.get('side', 'N/A')
            price = order.get('price', 0)
            amount = order.get('amount', 0)
            timestamp = order.get('timestamp')
            
            # تبدیل زمان (والکس زمان را به ثانیه می‌فرستد، پس در 1000 ضرب نمی‌کنیم)
            dt_str = 'N/A'
            if timestamp:
                # اگر زمان میلی‌ثانیه باشد
                if timestamp > 1000000000000:
                    ts = timestamp / 1000
                else:
                    ts = timestamp
                dt = datetime.fromtimestamp(ts)
                dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            print(f"  🆔 شناسه سفارش: {order_id}")
            print(f"  ⏱ زمان ثبت: {dt_str}")
            print(f"  🔄 نوع سفارش: {side.upper()}")
            print(f"  💰 نماد: {symbol}")
            print(f"  📦 حجم درخواستی: {amount}")
            print(f"  💵 قیمت لیمیت: {price}")
            print("-" * 50)

except Exception as e:
    print(f"\n❌ Error: {e}")
