# server.py
import asyncio
import websockets
import json

connected = set()

async def handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            # Broadcast received message to all other clients
            for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    finally:
        connected.remove(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
