import asyncio
import websockets
from api import open_file, save_file


async def write_content(path):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        await open_file(sock, path)
        print(await save_file(sock, path))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(
        write_content('kaas_is_dood.txt'))
