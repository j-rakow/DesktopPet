import asyncio
import websockets
import http.server
import socketserver
import threading
import os

connected = set()

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

# This HTTP server handles Render's pings (HEAD/GET requests)
def run_http_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

    with socketserver.TCPServer(("", 10000), Handler) as httpd:
        print("Health check server running on port 10000")
        httpd.serve_forever()

# Start HTTP in background thread
threading.Thread(target=run_http_server, daemon=True).start()

# Start WebSocket
async def main():
    port = int(os.environ.get("PORT", 8765))
    print(f"WebSocket server on port {port}")
    async with websockets.serve(handler, "", port):
        await asyncio.Future()

asyncio.run(main())
