import sys
import os
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
python_dir = os.path.join(current_dir, 'python')
sys.path.insert(0, python_dir)

from ccxt import nobitex

def main():
    exchange = nobitex()
    print("Exchange Name:", exchange.name)
    
    try:
        ticker = exchange.fetch_ticker('BTC/IRT')
        print("BTC/IRT Last Price:", ticker['last'])
        print("\n✅ پروژه با موفقیت در پایتون اجرا شد و آماده تحویله!")
    except Exception as e:
        print("❌ Error Type:", type(e).__name__)
        print("❌ Error:", e)
        print("\n--- Traceback ---")
        traceback.print_exc()

if __name__ == '__main__':
    main()