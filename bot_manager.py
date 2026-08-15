import sys
import os
import time
from datetime import datetime
from collections import defaultdict

# Add the python directory path to find the nobitex file
current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex

class TradingBotManager:
    def __init__(self, api_key, secret=None):
        """Initialize connection to Nobitex exchange"""
        config = {'apiKey': api_key}
        if secret:
            config['secret'] = secret
            
        self.exchange = nobitex(config)
        try:
            self.exchange.load_markets()
            print("Connected to Nobitex and markets loaded successfully.")
        except Exception as e:
            print(f"Error connecting to Nobitex: {e}")
            
    def get_live_price(self, symbol):
        """Fetch the current live market price for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker.get('last')
            if price:
                print(f"Current Live Price for {symbol}: {price:,.2f}")
            return price
        except Exception as e:
            print(f"Error fetching live price: {e}")
            return None

    def place_order(self, symbol, side, amount, price, simulate=False):
        """Place a spot (Limit) order with live price verification"""
        print(f"\n[Placing Spot Order] {side.upper()} {amount} {symbol} @ {price}")
        
        # Fetch live price exactly at the moment of execution
        live_price = self.get_live_price(symbol)
        if live_price is not None:
            diff = price - live_price
            print(f"Your Limit Price ({price:,.2f}) is {diff:+,.2f} away from the current Live Price ({live_price:,.2f})")
        
        try:
            order = self.exchange.create_order(symbol, 'limit', side, amount, price)
            print(f"Order placed successfully. Order ID: {order.get('id')}")
            return order
        except Exception as e:
            # If the user wants to run a simulation test and the error is related to insufficient balance
            if simulate and "OverValueOrder" in str(e):
                print("Insufficient balance detected. Running in SIMULATION MODE...")
                market = self.exchange.market(symbol)
                # Create a fake order for testing
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
                
                # Save to the simulated orders list
                if not hasattr(self, 'sim_orders'):
                    self.sim_orders = []
                self.sim_orders.append(order)
                
                print(f"SIMULATED Order placed successfully. Order ID: {order.get('id')}")
                return order
            else:
                print(f"Error placing order: {e}")
                return None

    def get_open_orders(self, symbol=None):
        """2. Fetch list of open spot orders"""
        print("\n[Fetching Open Orders]")
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            
            # Add simulated orders to the list
            if hasattr(self, 'sim_orders') and self.sim_orders:
                orders.extend(self.sim_orders)
                
            print(f"Found {len(orders)} open orders.")
            for o in orders:
                print(f"  ID: {o['id']} | {o['symbol']} | Side: {o['side']} | Amount: {o['amount']} | Price: {o['price']}")
            return orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return []

    def cancel_order(self, order_id, symbol=None):
        """3. Cancel a specific open order"""
        print(f"\n[Cancelling Order ID: {order_id}]")
        try:
            res = self.exchange.cancel_order(order_id, symbol)
            print("Order cancelled successfully.")
            return res
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return None

    def cancel_all_open_orders(self, symbol=None):
        """4. Close (cancel) all user's open orders"""
        print("\n[Cancelling All Open Orders]")
        try:
            # First, fetch the list of open orders
            open_orders = self.exchange.fetch_open_orders(symbol)
            
            if not open_orders:
                print("No open orders to cancel.")
                return True
                
            print(f"Found {len(open_orders)} open orders. Cancelling them one by one...")
            cancelled_count = 0
            
            for order in open_orders:
                order_id = order['id']
                order_symbol = order['symbol']
                try:
                    self.exchange.cancel_order(order_id, order_symbol)
                    print(f"  Cancelled Order ID: {order_id} ({order_symbol})")
                    cancelled_count += 1
                except Exception as e_inner:
                    print(f"  Failed to cancel Order ID {order_id}: {e_inner}")
                    
            print(f"Successfully cancelled {cancelled_count} out of {len(open_orders)} orders.")
            return True
        except Exception as e:
            print(f"Error cancelling all open orders: {e}")
            return False

    def get_trade_history(self, symbol=None, limit=50):
        """5. Fetch executed spot trade history"""
        print("\n[Fetching Trade History]")
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            print(f"Found {len(trades)} executed trades.")
            return trades
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []

    def calculate_pnl(self, trades):
        """6. Calculate Profit and Loss (daily, monthly, yearly)"""
        print("\n[Calculating Profit and Loss (PnL)]")
        
        if not trades:
            print("No trades to calculate.")
            return None

        # Using nested dictionaries to group by currency (USDT/RLS) and date
        pnl_data = {
            'daily': defaultdict(lambda: defaultdict(float)),
            'monthly': defaultdict(lambda: defaultdict(float)),
            'yearly': defaultdict(lambda: defaultdict(float)),
            'total': defaultdict(float)
        }
        
        for trade in trades:
            cost = trade.get('cost')  # Total trade value (price * amount)
            side = trade.get('side')  # buy or sell
            timestamp = trade.get('timestamp')
            market = trade.get('symbol', '')
            
            # Extract quote currency (e.g., USDT or RLS from BTC/USDT)
            quote_currency = market.split('/')[-1] if '/' in market else 'UNKNOWN'
            
            if cost is None or side is None or timestamp is None:
                continue
                
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(timestamp / 1000.0)
            
            # Calculate cash flow (sell = money in, buy = money out)
            trade_value = float(cost) if side == 'sell' else -float(cost)
            
            # Categories
            day_key = dt.strftime('%Y-%m-%d')
            month_key = dt.strftime('%Y-%m')
            year_key = dt.strftime('%Y')
            
            pnl_data['daily'][day_key][quote_currency] += trade_value
            pnl_data['monthly'][month_key][quote_currency] += trade_value
            pnl_data['yearly'][year_key][quote_currency] += trade_value
            pnl_data['total'][quote_currency] += trade_value

        # Print clean and readable output
        print("\n" + "="*40)
        print("📊 Total Overall PnL (Cash Flow)")
        for currency, val in pnl_data['total'].items():
            print(f"  {currency}: {val:,.2f}")
            
        print("\n--- 📅 Daily PnL ---")
        for day, currencies in pnl_data['daily'].items():
            curr_str = " | ".join([f"{c}: {v:,.2f}" for c, v in currencies.items()])
            print(f"  {day}: {curr_str}")
            
        print("\n--- 🗓 Monthly PnL ---")
        for month, currencies in pnl_data['monthly'].items():
            curr_str = " | ".join([f"{c}: {v:,.2f}" for c, v in currencies.items()])
            print(f"  {month}: {curr_str}")
            
        print("\n--- 📆 Yearly PnL ---")
        for year, currencies in pnl_data['yearly'].items():
            curr_str = " | ".join([f"{c}: {v:,.2f}" for c, v in currencies.items()])
            print(f"  {year}: {curr_str}")
            
        return pnl_data