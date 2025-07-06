import asyncio
import websockets
import http.server
import socketserver
import threading
import os
import sys
import socket

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

# --- HTTP server for Render health check ---
def run_http_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

    try:
        with socketserver.TCPServer(("", 10000), Handler) as httpd:
            print("Health check server running on port 10000")
            httpd.serve_forever()
    except OSError as e:
        print(f"[HTTP] Port 10000 already in use: {e}", file=sys.stderr)

# Start HTTP server in background thread
threading.Thread(target=run_http_server, daemon=True).start()

# --- WebSocket Server ---
def find_available_port(start_port=8765, max_tries=50):
    for i in range(max_tries):
        port = start_port + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                s.close()
                return port
            except OSError:
                continue
    raise RuntimeError("No available port found")

async def main():
    # Use Render's PORT environment variable or find an available local one
    port = int(os.environ.get("PORT", 0)) or find_available_port()

    print(f"WebSocket server binding to port {port}...")
    async with websockets.serve(handler, "", port):
        print(f"✅ WebSocket server is running on port {port}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shut down.")
