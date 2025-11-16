import asyncio
import websockets
import json
import threading
from datetime import datetime


class LogWebSocketServer:
    def __init__(self, orderbook_instance):
        self.orderbook = orderbook_instance
        self.connected_clients = set()
        self.last_log_index = 0
        
    async def register_client(self, websocket):
        self.connected_clients.add(websocket)
        try:
            recent_logs = self.orderbook.logs[-50:] if len(self.orderbook.logs) > 50 else self.orderbook.logs
            for log in recent_logs:
                await websocket.send(json.dumps({
                    "type": "log",
                    "message": str(log),
                    "timestamp": datetime.now().isoformat()
                }))
        except websockets.exceptions.ConnectionClosed:
            pass

    async def unregister_client(self, websocket):
        self.connected_clients.discard(websocket)

    async def broadcast_log(self, log_message):
        if self.connected_clients:
            message = json.dumps({
                "type": "log", 
                "message": str(log_message),
                "timestamp": datetime.now().isoformat()
            })
            
            clients_copy = self.connected_clients.copy()
            
            for client in clients_copy:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    self.connected_clients.discard(client)

    async def broadcast_orderbook(self):
        if self.connected_clients:
            with self.orderbook.lock:
                bids = list(self.orderbook.bids)
                asks = list(self.orderbook.asks)
            
            message = json.dumps({
                "type": "orderbook",
                "data": {"bid": bids, "ask": asks},
                "timestamp": datetime.now().isoformat()
            })
            
            clients_copy = self.connected_clients.copy()
            
            for client in clients_copy:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    self.connected_clients.discard(client)

    async def handle_client(self, websocket):
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

    def start_monitoring_logs(self):
        async def monitor_logs():
            while True:
                try:
                    current_log_count = len(self.orderbook.logs)
                    if current_log_count > self.last_log_index:
                        new_logs = self.orderbook.logs[self.last_log_index:]
                        for log in new_logs:
                            await self.broadcast_log(log)
                        self.last_log_index = current_log_count
                    
                    await self.broadcast_orderbook()
                    
                    await asyncio.sleep(0.1)  # Check every 100ms
                except Exception as e:
                    print(f"Error in log monitoring: {e}")
                    await asyncio.sleep(1)
        
        asyncio.create_task(monitor_logs())

    def start_server(self, host="localhost", port=8765):
        async def run_server():
            print(f"WebSocket server starting on ws://{host}:{port}")
            
            self.start_monitoring_logs()
            
            async with websockets.serve(self.handle_client, host, port):
                await asyncio.Future()  # Run forever
        
        asyncio.run(run_server())