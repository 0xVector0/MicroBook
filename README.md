# MicroBook

A simple orderbook implementation in Python. Built this to learn how trading systems work under the hood.

## How the Orderbook Engine Works

The engine maintains two sorted lists:
- Bids: Buy orders sorted by price (highest first)
- Asks: Sell orders sorted by price (lowest first)

When you place an order:
1. Limit orders get added to the appropriate list
2. Market orders immediately try to match against existing orders
3. The engine automatically matches compatible orders (when bid price >= ask price)

Example:
```
Current orderbook:
Bids: [(100, 50.0), (50, 49.5)]  # 100 shares at $50, 50 shares at $49.50
Asks: [(75, 51.0), (25, 52.0)]   # 75 shares at $51, 25 shares at $52

Market buy order for 75 shares:
- Takes the cheapest ask (75 @ $51)
- Order gets filled completely
- Orderbook now has no asks at $51
```

The matching engine runs in a separate thread and processes orders as they come in. Uses SortedList for fast insertions and lookups.
  
## Getting Started

Clone and run:
```bash
git clone https://github.com/0xVector0/MicroBook.git
cd MicroBook
pip install -r requirements.txt
python server.py
```

Server starts on `http://localhost:10000` with WebSocket on `ws://localhost:8765`

## Basic Usage

### Place Orders via HTTP
```python
import requests

# Buy limit order
requests.post('http://localhost:10000/limit-order', 
              json={'amount': 100, 'price': 50.0, 'type': 'bid'})

# Sell limit order  
requests.post('http://localhost:10000/limit-order',
              json={'amount': 50, 'price': 51.0, 'type': 'ask'})

# Market buy
requests.post('http://localhost:10000/order',
              json={'amount': 25, 'type': 'buy'})

# Check orderbook
response = requests.get('http://localhost:10000/orderbook')
print(response.json())
```

### Use the Python Client
```python
from orderbook.orderbook_client import orderbook_client

client = orderbook_client("localhost", 10000)

# Add orders
client.new_limit_order(100, 50.0, "bid")
client.new_limit_order(75, 52.0, "ask") 

# Execute trades
client.new_order(25, "buy")
client.new_order(30, "sell")

# View current state
print(client.get_order_book())
```

## Live Data Streaming

WebSocket endpoint streams real-time orderbook changes:

```python
import asyncio
import websockets
import json

async def monitor_orderbook():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            print(f"[{data['timestamp']}] {data['message']}")

asyncio.run(monitor_orderbook())
```

See `examples/` folder for visualization tools and more usage patterns.

## API Reference

HTTP Endpoints:
- `POST /limit-order` - Add limit order (amount, price, type: bid/ask)
- `POST /order` - Execute market order (amount, type: buy/sell)  
- `GET /orderbook` - Get current orderbook state
- `GET /logs` - Get trade history

WebSocket: 
- Real-time trade executions and orderbook updates

## Architecture

Simple three-component design:
- Core Engine: SortedList-based orderbook with O(log n) insertions
- HTTP Server: Flask API for order placement and queries
- WebSocket Server: Real-time streaming of trades and updates

## File Structure

```
MicroBook/
├── orderbook/              # Core package
├── examples/               # Usage examples
├── server.py               # Main entry point
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
