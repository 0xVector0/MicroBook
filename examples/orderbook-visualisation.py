import sys
import os
# Add parent directory to path so we can import orderbook
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time
import random
from datetime import datetime
from orderbook.orderbook_client import orderbook_client

def random_order_generator(microbook, stop_event):
    """Thread function to continuously add random orders"""
    while not stop_event.is_set():
        try:
            order_type = random.choice(["bid", "ask"])
            amount = random.randint(1, 10)
            
            if order_type == "bid":
                price = random.randint(1, 12)
            else:
                price = random.randint(8, 20)
            
            microbook.new_limit_order(amount, price, order_type)
            
            time.sleep(random.uniform(0.01, 0.1))
            
        except Exception as e:
            print(f"Error adding random order: {e}")
            time.sleep(1)

def aggregate_orders_by_price(orders):
    """Aggregate orders by price level, summing amounts for same prices"""
    if not orders:
        return []
    
    price_levels = {}
    for order in orders:
        amount, price, order_id = order
        if price in price_levels:
            price_levels[price] += amount
        else:
            price_levels[price] = amount
    
    # Return as list of (amount, price) tuples, sorted by price
    return [(amount, price) for price, amount in sorted(price_levels.items())]

def update_plot(frame, ax, microbook):
    ax.clear()
    
    current_book = microbook.get_order_book()
    
    asks = current_book["ask"]
    bids = current_book["bid"]
    
    # Aggregate orders by price level
    if asks:
        aggregated_asks = aggregate_orders_by_price(asks)
        ask_prices = [a[1] for a in aggregated_asks]  # price
        ask_amounts = [a[0] for a in aggregated_asks]  # amount
        ax.barh(ask_prices, ask_amounts, color='red', alpha=0.7, label='Asks')
    
    if bids:
        aggregated_bids = aggregate_orders_by_price(bids)
        bid_prices = [b[1] for b in aggregated_bids]  # price
        bid_amounts = [-b[0] for b in aggregated_bids]  # negative amount for left side
        ax.barh(bid_prices, bid_amounts, color='green', alpha=0.7, label='Bids')
    
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.set_xlabel("Amount (Bids ← | → Asks)")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Show order counts (individual orders, not aggregated levels)
    num_bids = len(bids) if bids else 0
    num_asks = len(asks) if asks else 0
    
    # Show aggregated levels count
    num_bid_levels = len(aggregated_bids) if bids else 0
    num_ask_levels = len(aggregated_asks) if asks else 0
    
    ax.set_title(f"Live Orderbook - {datetime.now().strftime('%H:%M:%S')} | "
                f"Bid Orders: {num_bids} ({num_bid_levels} levels) | "
                f"Ask Orders: {num_asks} ({num_ask_levels} levels)")

def start_live_orderbook():
    microbook = orderbook_client("localhost", 10000)

    stop_event = threading.Event()
    
    order_thread = threading.Thread(target=random_order_generator, 
                                   args=(microbook, stop_event), 
                                   daemon=True)
    order_thread.start()
    
    for _ in range(3):
        microbook.new_limit_order(random.randint(1, 5), random.randint(5, 10), "bid")
        microbook.new_limit_order(random.randint(1, 5), random.randint(11, 15), "ask")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax, microbook), 
                                interval=10, repeat=True, cache_frame_data=False)
    
    plt.tight_layout()
    
    def on_close(event):
        stop_event.set()
        print("Stopping order generation...")
    
    fig.canvas.mpl_connect('close_event', on_close)
    
    plt.show()
    stop_event.set()
    
    return ani
        
if __name__ == "__main__":
    try:
        ani = start_live_orderbook()
    except KeyboardInterrupt:
        print("\nStopping live orderbook...")
    except Exception as e:
        print(f"Error: {e}")