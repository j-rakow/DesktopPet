import asyncio
import websockets
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

async def main():
    port = int(os.environ.get("PORT", 10000))  # use Render's assigned port
    print(f"WebSocket server running on port {port}...")
    async with websockets.serve(handler, "", port):
        await asyncio.Future()

asyncio.run(main())
