import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.nobitex import nobitex
from datetime import datetime

API_KEY = '040dff9101b461a49cb50db31bf582875466f9f4'

exchange = nobitex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Nobitex...")
    exchange.load_markets()

    print("\n--- Fetching Trade History ---")
    trades = exchange.fetch_my_trades(limit=10)

    if not trades:
        print("No executed trades found.")
    else:
        print(f"Found {len(trades)} recent executed trades:\n")
        
        total_pnl = 0.0

        for trade in trades:
            timestamp = trade.get('timestamp')
            dt = datetime.fromtimestamp(timestamp / 1000.0) if timestamp else None
            dt_str = dt.strftime('%Y-%m-%d %H:%M') if dt else 'N/A'

            symbol = trade.get('symbol') or 'N/A'
            
            # نوبیتکس ممکن است خرید/فروش را در فیلد type یا side بفرستد
            side = trade.get('side') or trade.get('type') or 'unknown'
            
            price = float(trade.get('price') or 0)
            amount = float(trade.get('amount') or 0)
            
            trade_value = price * amount

            print(f"[{dt_str}] {side.upper()} {amount} {symbol} @ {price:,.2f} RLS (Value: {trade_value:,.2f} RLS)")

            if side == 'sell':
                total_pnl += trade_value
            elif side == 'buy':
                total_pnl -= trade_value

        print("\n" + "="*40)
        print(f"📊 Total Realized Cash Flow (RLS): {total_pnl:,.2f} RLS")
        print("="*40)
        
        if total_pnl > 0:
            print("✅ You have a net positive cash flow (You sold more than you bought in RLS).")
        elif total_pnl < 0:
            print("⚠️ You have a net negative cash flow (You bought more than you sold in RLS), meaning you currently hold assets.")
        else:
            print("Neutral cash flow.")

except Exception as e:
    print(f"\n❌ Error: {e}")
