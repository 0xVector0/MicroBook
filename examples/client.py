import sys
import os
# Add parent directory to path so we can import orderbook
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import random
import threading
from datetime import datetime
from orderbook.orderbook_client import orderbook_client

def main():
    """Basic client example showing orderbook usage."""
    print("🚀 MicroBook Client Example")
    print("=" * 40)
    
    # Create client connection
    client = orderbook_client("localhost", 10000)
    
    try:
        # Test connection
        print("\n📊 Current orderbook:")
        current_book = client.get_order_book()
        print(f"Bids: {len(current_book.get('bid', []))}")
        print(f"Asks: {len(current_book.get('ask', []))}")
        
        # Add some limit orders
        print("\n📝 Adding limit orders...")
        print("Adding bid (buy) order: 100 @ 50.0")
        result1 = client.new_limit_order(100, 50.0, "bid")
        print(f"Result: {result1}")
        
        print("Adding ask (sell) order: 75 @ 52.0")
        result2 = client.new_limit_order(75, 52.0, "ask")
        print(f"Result: {result2}")
        
        # Check orderbook
        print("\n📊 Updated orderbook:")
        updated_book = client.get_order_book()
        bids = updated_book.get('bid', [])
        asks = updated_book.get('ask', [])
        
        if bids:
            best_bid = max(bids, key=lambda x: x[1])
            print(f"Best bid: {best_bid[0]} @ {best_bid[1]}")
        
        if asks:
            best_ask = min(asks, key=lambda x: x[1])
            print(f"Best ask: {best_ask[0]} @ {best_ask[1]}")
        
        if bids and asks:
            spread = best_ask[1] - best_bid[1]
            print(f"Spread: {spread}")
        
        # Execute market orders
        print("\n💰 Executing market orders...")
        print("Market buy: 25 units")
        buy_result = client.new_order(25, "buy")
        print(f"Buy result: {buy_result}")
        
        print("Market sell: 30 units")
        sell_result = client.new_order(30, "sell")
        print(f"Sell result: {sell_result}")
        
        # Final orderbook state
        print("\n📊 Final orderbook:")
        final_book = client.get_order_book()
        print(f"Bids: {final_book.get('bid', [])}")
        print(f"Asks: {final_book.get('ask', [])}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure to run 'python server.py' first!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
