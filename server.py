import asyncio
import websockets
import http.server
import socketserver
import threading
import os

connected = set()

# WebSocket handler
async def handler(websocket):
    print("Client connected")
    connected.add(websocket)
    try:
        async for message in websocket:
            for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected.remove(websocket)

# HTTP handler for HEAD/GET (Render pings)
def run_http_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()
        def log_message(self, format, *args):
            return  # Silence logs

    with socketserver.TCPServer(("", 10000), Handler) as httpd:
        print("Health check HTTP server running on port 10000")
        httpd.serve_forever()

# Start HTTP server in background thread
threading.Thread(target=run_http_server, daemon=True).start()

# Start WebSocket server
async def main():
    port = int(os.environ.get("PORT", 8765))  # For Render, PORT is env var
    print(f"WebSocket server running on port {port}")
    async with websockets.serve(handler, "", port):
        await asyncio.Future()

asyncio.run(main())
