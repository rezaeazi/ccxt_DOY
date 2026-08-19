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
    
    print("Attempting to place a REAL order...")
    order = exchange.create_order('BTC/USDT', 'limit', 'buy', 0.001, 60000)
    print("✅ Order Success! Order ID:", order.get('id'))
    
except Exception as e:
    print("❌ Error:", e)
