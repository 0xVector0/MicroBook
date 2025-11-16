from datetime import datetime
from sortedcontainers import SortedList
import threading
import time
import traceback

class orderbook_server:
    def __init__(self):
        # Bids sorted by price descending (highest price first)
        self.bids = SortedList(key=lambda x: -x[1])
        # Asks sorted by price ascending (lowest price first)  
        self.asks = SortedList(key=lambda x: x[1])
        
        self.logs = []
        self.id = 0
        self.lock = threading.Lock()

    def connection_handler(self, websocket):
        for messages in websocket:
            print(messages)

    def orderbook_engine_run(self):
        while True:
            try:
                with self.lock:
                    if not self.bids or not self.asks:
                        pass 
                    else:
                        best_bid = self.bids[0]  # Highest price bid
                        best_ask = self.asks[0]  # Lowest price ask
                        
                        if best_bid[1] >= best_ask[1]:
                            bid_amount, bid_price, bid_id = best_bid
                            ask_amount, ask_price, ask_id = best_ask
                            
                            if bid_amount > ask_amount:
                                remaining_bid = (bid_amount - ask_amount, bid_price, bid_id)
                                
                                self.asks.pop(0)
                                self.bids.pop(0)
                                self.bids.add(remaining_bid)
                                
                                self.logs.append(f"{datetime.now()} order {best_ask} got filled.")
                                
                            elif ask_amount > bid_amount:
                                remaining_ask = (ask_amount - bid_amount, ask_price, ask_id)
                                self.bids.pop(0)
                                self.asks.pop(0)
                                self.asks.add(remaining_ask)
                                
                                self.logs.append(f"{datetime.now()} order {best_bid} got filled.")
                                
                            else:
                                self.bids.pop(0)
                                self.asks.pop(0)
                                
                                self.logs.append(f"{datetime.now()} order {best_bid} got filled.")
                                self.logs.append(f"{datetime.now()} order {best_ask} got filled.")
                        
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)  # 1ms delay
                
            except Exception as e:
                print(f"Error in orderbook engine: {e}")
                traceback.print_exc()
                time.sleep(0.1)

    def new_limit_order(self, amount: float, price: float, type: str):
        try:
            if amount is None or price is None or type is None:
                return "Missing required parameters: amount, price, type"
                
            if amount <= 0:
                return "Amount must be positive."
            
            if price <= 0:
                return "Price must be positive."
            
            with self.lock:
                self.id += 1
                order = (amount, price, self.id)
                
                if type == "bid":
                    self.bids.add(order)
                    self.logs.append(f"{datetime.now()} bid added for {amount} token at {price} price ")
                    return "Order added."
                elif type == "ask":
                    self.asks.add(order)
                    self.logs.append(f"{datetime.now()} ask added for {amount} token at {price} price ")
                    return "Order added."
                else:
                    return "Type must be either 'bid' or 'ask'"
        except Exception as e:
            print(f"Error in new_limit_order: {e}")
            return f"Error processing order: {str(e)}"

    def new_order(self, amount: float, type: str):
        if amount < 0:
            return "Amount must be positive."
        
        with self.lock:
            if type == "buy":
                remaining_amount = amount
                executed_trades = []
                
                while remaining_amount > 0 and self.asks:
                    best_ask = self.asks[0]
                    ask_amount, ask_price, ask_id = best_ask
                    
                    if remaining_amount >= ask_amount:
                        executed_trades.append((ask_amount, ask_price))
                        remaining_amount -= ask_amount
                        self.asks.pop(0)
                        self.logs.append(f"{datetime.now()} Market buy executed: {ask_amount} @ {ask_price}")
                    else:
                        executed_trades.append((remaining_amount, ask_price))
                        updated_ask = (ask_amount - remaining_amount, ask_price, ask_id)
                        self.asks.pop(0)
                        self.asks.add(updated_ask)
                        self.logs.append(f"{datetime.now()} Market buy executed: {remaining_amount} @ {ask_price}")
                        remaining_amount = 0
                
                if remaining_amount > 0:
                    return f"Partially filled. {amount - remaining_amount} executed, {remaining_amount} remaining (no more asks available)"
                else:
                    return f"Market buy order fully executed. Trades: {executed_trades}"
                    
            elif type == "sell":
                remaining_amount = amount
                executed_trades = []
                
                while remaining_amount > 0 and self.bids:
                    best_bid = self.bids[0]
                    bid_amount, bid_price, bid_id = best_bid
                    
                    if remaining_amount >= bid_amount:
                        executed_trades.append((bid_amount, bid_price))
                        remaining_amount -= bid_amount
                        self.bids.pop(0)
                        self.logs.append(f"{datetime.now()} Market sell executed: {bid_amount} @ {bid_price}")
                    else:
                        executed_trades.append((remaining_amount, bid_price))
                        updated_bid = (bid_amount - remaining_amount, bid_price, bid_id)
                        self.bids.pop(0)
                        self.bids.add(updated_bid)
                        self.logs.append(f"{datetime.now()} Market sell executed: {remaining_amount} @ {bid_price}")
                        remaining_amount = 0
                
                if remaining_amount > 0:
                    return f"Partially filled. {amount - remaining_amount} executed, {remaining_amount} remaining (no more bids available)"
                else:
                    return f"Market sell order fully executed. Trades: {executed_trades}"
            else:
                return "Type must be either 'buy' or 'sell'"