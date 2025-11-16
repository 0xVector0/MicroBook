import asyncio
import websockets
import json

async def test_websocket_logs():
    """Test client for WebSocket live logs"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")
            print("Listening for live logs and orderbook updates...")
            print("-" * 50)
            
            await websocket.send(json.dumps({"type": "subscribe", "subscribe_to": "all"}))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data["type"] == "log":
                        print(f"LOG: {data['message']}")
                    elif data["type"] == "orderbook":
                        orderbook = data["data"]
                        bid_count = len(orderbook["bid"])
                        ask_count = len(orderbook["ask"])
                        
                        best_bid = orderbook["bid"][0] if orderbook["bid"] else None
                        best_ask = orderbook["ask"][0] if orderbook["ask"] else None
                        
                        print(f"ORDERBOOK: {bid_count} bids, {ask_count} asks")
                        if best_bid and best_ask:
                            print(f"   Best Bid: {best_bid[0]} @ {best_bid[1]}")
                            print(f"   Best Ask: {best_ask[0]} @ {best_ask[1]}")
                            print(f"   Spread: {best_ask[1] - best_bid[1]:.2f}")
                        
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")
                    
    except websockets.exceptions.ConnectionRefused:
        print("Could not connect to WebSocket server. Is the server running?")
    except KeyboardInterrupt:
        print("\nDisconnected from WebSocket server")

if __name__ == "__main__":
    asyncio.run(test_websocket_logs())