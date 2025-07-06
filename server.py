import asyncio
import websockets
import os
import http.server
import socketserver
import threading

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

# Responds to HTTP HEAD requests so Render thinks we're healthy
def run_http_health_check(port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

        def log_message(self, format, *args):  # Silence logging
            return

    # Use a different port for the health check
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Health check HTTP server on port {port}")
        httpd.serve_forever()

async def main():
    ws_port = int(os.environ.get("PORT", 8765))
    print(f"WebSocket server running on port {ws_port}...")

    # Start HTTP health check server on an unused port
    threading.Thread(target=run_http_health_check, args=(ws_port + 1,), daemon=True).start()

    async with websockets.serve(handler, "", ws_port):
        await asyncio.Future()

asyncio.run(main())
