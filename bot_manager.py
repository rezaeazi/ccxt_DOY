import sys
import os
import time
from datetime import datetime
from collections import defaultdict

# اضافه کردن مسیر پوشه پایتون
current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

# ایمپورت کردن هر دو صرافی
from ccxt.nobitex import nobitex
from ccxt.wallex import wallex

class TradingBotManager:
    def __init__(self, exchange_id='nobitex', api_key=None, secret=None):
        """راه‌اندازی اتصال به صرافی (نوبیتکس یا والکس)"""
        config = {}
        if api_key:
            config['apiKey'] = api_key
        if secret:
            config['secret'] = secret
            
        if exchange_id == 'nobitex':
            self.exchange = nobitex(config)
        elif exchange_id == 'wallex':
            self.exchange = wallex(config)
        else:
            raise ValueError(f"Exchange {exchange_id} is not supported.")
            
        try:
            self.exchange.load_markets()
            print(f"✅ Connected to {self.exchange.name} and markets loaded successfully.")
        except Exception as e:
            print(f"❌ Error connecting to exchange: {e}")

    def get_live_price(self, symbol):
        """گرفتن قیمت لحظه ای"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker.get('last')
            if price:
                print(f"📈 Current Live Price for {symbol}: {price:,.2f}")
            return price
        except Exception as e:
            print(f"❌ Error fetching live price: {e}")
            return None

    def place_order(self, symbol, side, amount, price, simulate=False):
        """ثبت سفارش اسپات"""
        print(f"\n[Placing Spot Order] {side.upper()} {amount} {symbol} @ {price}")
        
        try:
            order = self.exchange.create_order(symbol, 'limit', side, amount, price)
            print(f"✅ Order placed successfully. Order ID: {order.get('id')}")
            return order
        except Exception as e:
            if simulate and ("OverValueOrder" in str(e) or "InsufficientBalance" in str(e)):
                print("⚠️ Insufficient balance detected. Running in SIMULATION MODE...")
                market = self.exchange.market(symbol)
                fake_id = f"SIM-{int(time.time())}"
                fake_order_data = {
                    'id': fake_id,
                    'type': side,
                    'side': side,
                    'srcCurrency': market['baseId'],
                    'dstCurrency': market['quoteId'],
                    'amount': str(amount),
                    'price': str(price),
                    'status': 'Active',
                    'createdAt': int(time.time() * 1000)
                }
                order = self.exchange.parse_order(fake_order_data, market)
                
                if not hasattr(self, 'sim_orders'):
                    self.sim_orders = []
                self.sim_orders.append(order)
                
                print(f"✅ SIMULATED Order placed successfully. Order ID: {order.get('id')}")
                return order
            else:
                print(f"❌ Error placing order: {e}")
                return None

    def get_open_orders(self, symbol=None):
        """گرفتن لیست سفارشات باز"""
        print("\n[Fetching Open Orders]")
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            if hasattr(self, 'sim_orders') and self.sim_orders:
                orders.extend(self.sim_orders)
            print(f"Found {len(orders)} open orders.")
            for o in orders:
                print(f"  ID: {o['id']} | {o['symbol']} | Side: {o['side']} | Amount: {o['amount']} | Price: {o['price']}")
            return orders
        except Exception as e:
            print(f"❌ Error fetching open orders: {e}")
            return []

    def cancel_all_open_orders(self, symbol=None):
        """بستن تمامی سفارشات باز"""
        print("\n[Cancelling All Open Orders]")
        try:
            open_orders = self.exchange.fetch_open_orders(symbol)
            if not open_orders:
                print("✅ No open orders to cancel.")
                return True
            print(f"Found {len(open_orders)} open orders. Cancelling them one by one...")
            cancelled_count = 0
            for order in open_orders:
                order_id = order['id']
                order_symbol = order['symbol']
                try:
                    self.exchange.cancel_order(order_id, order_symbol)
                    print(f"  ❌ Cancelled Order ID: {order_id} ({order_symbol})")
                    cancelled_count += 1
                except Exception as e_inner:
                    print(f"  ⚠️ Failed to cancel Order ID {order_id}: {e_inner}")
            print(f"✅ Successfully cancelled {cancelled_count} out of {len(open_orders)} orders.")
            return True
        except Exception as e:
            print(f"❌ Error cancelling all open orders: {e}")
            return False

    def get_trade_history(self, symbol=None, limit=50):
        """گرفتن تاریخچه معاملات"""
        print("\n[Fetching Trade History]")
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            print(f"✅ Found {len(trades)} executed trades.")
            return trades
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
            return []

    def calculate_pnl(self, trades):
        """محاسبه سود و زیان"""
        print("\n[Calculating Profit and Loss (PnL)]")
        if not trades:
            print("No trades to calculate.")
            return None
        pnl_data = {
            'daily': defaultdict(lambda: defaultdict(float)),
            'monthly': defaultdict(lambda: defaultdict(float)),
            'yearly': defaultdict(lambda: defaultdict(float)),
            'total': defaultdict(float)
        }
        for trade in trades:
            cost = trade.get('cost')
            side = trade.get('side')
            timestamp = trade.get('timestamp')
            market = trade.get('symbol', '')
            quote_currency = market.split('/')[-1] if '/' in market else 'UNKNOWN'
            if cost is None or side is None or timestamp is None:
                continue
            dt = datetime.fromtimestamp(timestamp / 1000.0)
            trade_value = float(cost) if side == 'sell' else -float(cost)
            day_key = dt.strftime('%Y-%m-%d')
            month_key = dt.strftime('%Y-%m')
            year_key = dt.strftime('%Y')
            pnl_data['daily'][day_key][quote_currency] += trade_value
            pnl_data['monthly'][month_key][quote_currency] += trade_value
            pnl_data['yearly'][year_key][quote_currency] += trade_value
            pnl_data['total'][quote_currency] += trade_value
        print("\n" + "="*40)
        print("📊 Total Overall PnL (Cash Flow)")
        for currency, val in pnl_data['total'].items():
            print(f"  {currency}: {val:,.2f}")
        return pnl_data