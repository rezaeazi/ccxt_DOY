import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

# کلید والکس خود را دقیقاً بین کوتیشن‌ها قرار دهید
API_KEY = '20103|Am0Xf2b7IEBP1lsS6GOXRjWWVl0bKYoZSiZI3gMN'

# حذف فاصله‌های اضافی احتمالی
API_KEY = API_KEY.strip()

print(f"Using API Key: {API_KEY}")

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("\nConnecting to Wallex...")
    exchange.load_markets()
    
    print("--- Fetching Balance ---")
    balance = exchange.fetch_balance()
    
    # فقط موجودی‌های غیر صفر را نشان می‌دهیم
    non_zero = {k: v for k, v in balance.items() if k != 'info' and isinstance(v, dict) and v.get('total') not in [None, 0]}
    
    if not non_zero:
        print("❌ No balance found in your account!")
    else:
        print("✅ Your non-zero balances:")
        for cur, val in non_zero.items():
            print(f"  {cur}: Free: {val.get('free')} | Total: {val.get('total')}")

except Exception as e:
    print(f"\n❌ Error: {e}")
