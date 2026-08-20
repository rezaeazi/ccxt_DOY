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
    
    print("\n--- 📜 Fetching Transaction History (Deposits & Withdrawals) ---")
    
    transactions = exchange.fetch_transactions(limit=10)
    
    if not transactions:
        print("❌ هیچ تراکنشی (واریز/برداشت) یافت نشد.")
    else:
        print(f"✅ {len(transactions)} تراکنش اخیر یافت شد:\n")
        for tx in transactions:
            tx_type = tx.get('type', 'N/A')
            amount = tx.get('amount', 0)
            currency = tx.get('currency', 'N/A')
            status = tx.get('status', 'N/A')
            timestamp = tx.get('timestamp')
            
            dt_str = 'N/A'
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                dt_str = dt.strftime('%Y-%m-%d %H:%M')
                
            type_fa = 'واریز' if tx_type == 'deposit' else ('برداشت' if tx_type == 'withdraw' else tx_type)
            
            print(f"  ⏱ زمان: {dt_str}")
            print(f"  🔄 نوع: {type_fa}")
            print(f"  💰 مبلغ: {amount} {currency}")
            print(f"  📊 وضعیت: {status}")
            print("-" * 50)

except Exception as e:
    print(f"\n❌ Error: {e}")
