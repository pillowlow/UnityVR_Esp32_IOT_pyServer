import asyncio
import websockets
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.FileHandler("server.log"), logging.StreamHandler()])

clients = set()

async def register(websocket):
    clients.add(websocket)
    logging.info(f"New client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            logging.info(f"Received message from {websocket.remote_address}: {message}")
            await notify_clients(message)
    except websockets.ConnectionClosed as e:
        logging.warning(f"Connection closed: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        clients.remove(websocket)
        logging.info(f"Client disconnected: {websocket.remote_address}")

async def notify_clients(message):
    if clients:  # asyncio.wait doesn't accept an empty list
        await asyncio.gather(*[client.send(message) for client in clients])

async def read_input():
    while True:
        user_input = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        user_input = user_input.strip()
        if user_input.lower() == "exit":
            logging.info("Shutting down server...")
            for client in clients:
                await client.close()
            break
        else:
            logging.info(f"Broadcasting message: {user_input}")
            await notify_clients(user_input)

async def main():
    logging.info("Server started, waiting for clients to connect...")
    server = await websockets.serve(register, "0.0.0.0", 8080)
    await asyncio.gather(server.wait_closed(), read_input())

if __name__ == "__main__":
    asyncio.run(main())
