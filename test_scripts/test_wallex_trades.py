import sys
from datetime import datetime, timezone
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
    
    print("\n--- Fetching Executed Trades History ---")
    print("ℹ️ Note: Wallex API does not support deposit/withdrawal history. Showing executed trades only.")
    
    response = exchange.request('v1/account/orders', 'private', 'GET', {})
    result = response.get('result', {})
    all_orders = result.get('orders', [])
    
    executed_trades = []
    for o in all_orders:
        status = o.get('status', '').upper()
        if 'FILL' in status or 'DONE' in status or 'CLOSED' in status:
            executed_trades.append(o)
            
    if not executed_trades:
        print("\n❌ No executed trades found. (Open orders are ignored)")
    else:
        print(f"\n✅ Found {len(executed_trades)} executed trades:\n")
        for t in executed_trades:
            symbol = t.get('symbol', 'N/A')
            side = t.get('side', 'N/A').upper() 
            price = float(t.get('price', 0) or 0)
            qty = float(t.get('origQty', 0) or 0)
            
            # والکس زمان را به صورت عدد (Timestamp) می‌فرستد
            ts = t.get('transactTime') or t.get('time') or t.get('timestamp')
            dt_str = 'N/A'
            if ts:
                try:
                    # اگر میلی‌ثانیه باشد
                    if int(ts) > 1000000000000:
                        dt = datetime.fromtimestamp(int(ts)/1000.0, tz=timezone.utc)
                    else:
                        # اگر ثانیه باشد
                        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
                    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                except:
                    dt_str = str(ts)
                
            print(f"  Time: {dt_str}")
            print(f"  Type: {side}")
            print(f"  Symbol: {symbol}")
            print(f"  Price: {price}")
            print(f"  Quantity: {qty}")
            print(f"  Status: {t.get('status', 'N/A')}")
            print("-" * 50)

except Exception as e:
    print(f"\nError: {e}")
