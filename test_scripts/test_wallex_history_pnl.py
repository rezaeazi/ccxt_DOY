import sys
from datetime import datetime
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

    print("\n--- Fetching Order History ---")
    # گرفتن تاریخچه سفارشات از والکس
    response = exchange.request('v1/account/orders', 'private', 'GET', {})
    result = response.get('result', {})
    
    # والکس ممکن است سفارشات را در لیست 'orders' یا مستقیما بریزد
    orders = []
    if isinstance(result, list):
        orders = result
    elif isinstance(result, dict):
        orders = result.get('orders', result.get('data', []))

    if not orders:
        print("No order history found.")
    else:
        print(f"Found {len(orders)} total orders. Filtering filled orders...\n")
        
        total_pnl = 0.0
        filled_count = 0

        for order in orders:
            # فقط سفارشات پر شده (Filled) را در نظر می‌گیریم
            status = order.get('status', '').upper()
            if 'FILL' not in status:
                continue
                
            filled_count += 1

            # استخراج اطلاعات
            timestamp = order.get('transactTime') or order.get('timestamp')
            # برخی زمان‌ها میلی‌ثانیه و برخی ثانیه هستند
            if timestamp and timestamp > 1e12:
                dt = datetime.fromtimestamp(timestamp / 1000.0)
            elif timestamp:
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = None
                
            dt_str = dt.strftime('%Y-%m-%d %H:%M') if dt else 'N/A'

            symbol = order.get('symbol', 'N/A')
            side = order.get('side', 'N/A').lower()
            price = float(order.get('price', 0) or 0)
            qty = float(order.get('origQty', order.get('quantity', 0)) or 0)
            
            # اگر قیمت یا حجم صفر بود، از فیلدهای اجرا شده استفاده کن
            if price == 0:
                price = float(order.get('executedPrice', 0) or 0)
            if qty == 0:
                qty = float(order.get('executedQty', 0) or 0)
                
            trade_value = price * qty

            print(f"[{dt_str}] {side.upper()} {qty} {symbol} @ {price} USDT (Value: {trade_value:.4f} USDT)")

            # محاسبه جریان نقدی (فروش = پول وارد شده، خرید = پول خارج شده)
            if side == 'sell':
                total_pnl += trade_value
            elif side == 'buy':
                total_pnl -= trade_value

        if filled_count == 0:
            print("❌ No filled orders found to calculate PnL.")
        else:
            print("\n" + "="*40)
            print(f"📊 Total Realized Cash Flow (USDT): {total_pnl:.4f} USDT")
            print("="*40)
            
            if total_pnl > 0:
                print("✅ You have a net positive cash flow (You sold more than you bought in USDT).")
            elif total_pnl < 0:
                print("⚠️ You have a net negative cash flow (You bought more than you sold in USDT), meaning you currently hold assets.")
            else:
                print("Neutral cash flow.")

except Exception as e:
    print(f"\n❌ Error: {e}")
