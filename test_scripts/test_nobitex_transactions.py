import sys
from datetime import datetime, timezone
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.nobitex import nobitex

API_KEY = 'YOUR_NOBITEX_TOKEN'

exchange = nobitex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Nobitex...")
    exchange.load_markets()

    print("\n--- Fetching Transaction History (Deposits & Withdrawals) ---")

    transactions = exchange.fetch_transactions(limit=10)

    if not transactions:
        print("No transactions found.")
    else:
        print(f"Found {len(transactions)} recent transactions:\n")
        for tx in transactions:
            tx_type = tx.get('type', 'N/A')
            amount = tx.get('amount', 0)
            currency = tx.get('currency', 'N/A')
            status = tx.get('status', 'N/A')
            timestamp = tx.get('timestamp')

            type_map = {
                'معامله': 'Trade', 'واریز': 'Deposit', 'برداشت': 'Withdrawal',
                'deposit': 'Deposit', 'withdraw': 'Withdrawal', 'trade': 'Trade'
            }
            type_en = type_map.get(tx_type, tx_type)

            dt_str = 'N/A'
            if timestamp:
                # استفاده از استاندارد جدید پایتون برای رفع ارور DeprecationWarning
                dt = datetime.fromtimestamp(timestamp / 1000.0, tz=timezone.utc)
                dt_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

            print(f"  Time: {dt_str}")
            print(f"  Type: {type_en}")
            print(f"  Amount: {amount} {currency.upper()}")
            print(f"  Status: {status}")
            print("-" * 50)

except Exception as e:
    print(f"\nError: {e}")
