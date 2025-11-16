import threading
from orderbook.orderbook_server import orderbook_server
from orderbook.flask_server import flask_server
from orderbook.websocket_server import LogWebSocketServer

microbook = orderbook_server()

engine_thread = threading.Thread(target=microbook.orderbook_engine_run, daemon=True)
engine_thread.start()

flask_app = flask_server(microbook)
server_thread = threading.Thread(
    target=lambda: flask_app.run("localhost", 10000, debug=False, use_reloader=False),
    daemon=True
)
server_thread.start()

websocket_server = LogWebSocketServer(microbook)
websocket_thread = threading.Thread(
    target=lambda: websocket_server.start_server("localhost", 8765),
    daemon=True
)
websocket_thread.start()

print("MicroBook server started on localhost:10000")
print("WebSocket live logs available on ws://localhost:8765")
print("Press Ctrl+C to stop the server")

try:
    while True:
        if not engine_thread.is_alive():
            print("WARNING: Order engine thread has stopped!")
        if not server_thread.is_alive():
            print("WARNING: Flask server thread has stopped!")
        if not websocket_thread.is_alive():
            print("WARNING: WebSocket server thread has stopped!")
            
        import time
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nShutting down server...")

        

        
