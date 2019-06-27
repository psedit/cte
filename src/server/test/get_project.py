import asyncio
import websockets
from api import fetch_files


async def get_files():
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        await fetch_files(sock)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(get_files())
