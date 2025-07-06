import asyncio
import websockets
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

async def main():
    print("Starting WebSocket server on port 10000...")
    async with websockets.serve(handler, "", 10000):
        await asyncio.Future()  # run forever

# --- HTTP server for Render ping checks ---
def run_http_server():
    PORT = 80
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving HTTP on port {PORT}")
        httpd.serve_forever()

# Start HTTP server in a background thread
threading.Thread(target=run_http_server, daemon=True).start()

# Start WebSocket server in main thread
asyncio.run(main())
