import sys
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
    
    print("\n--- 🚀 Initiating Transfer (Withdraw) ---")
    
    # Transfer settings
    currency = 'TRX'  # The currency you want to transfer
    amount = 1.0      # The amount to transfer (e.g., 1 TRX)
    
    # Destination wallet address (Put your friend's wallet address here)
    destination_address = '20106|x6HsW4YHBmQAF7IWSyYJJqIKMbCaY8fcDnRtmuS5'
    
    # Transfer network (e.g., TRX for Tron, TRC20 for Tether)
    network = 'TRX'
    
    print(f"Transferring {amount} {currency} to {destination_address} via {network} network...")
    
    # Execute the withdrawal/transfer request
    # In the CCXT system, the 'withdraw' method is used to send funds out of the account
    response = exchange.withdraw(currency, amount, destination_address, None, {'network': network})
    
    print("\n✅ Transfer Request Sent Successfully!")
    print("Transfer ID:", response.get('id', 'N/A'))
    print("Status:", response.get('status', 'N/A'))
    print("\n💡 Note: The transfer might take a few minutes to reflect on the blockchain/receiver account.")

except Exception as e:
    print(f"\n❌ Error: {e}")
