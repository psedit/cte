import asyncio
import websockets
from api import open_file_data


async def dump_content(path):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        content = await open_file_data(sock, path)
        print(content['block_list'])

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(
        dump_content('kaas_is_dood.txt'))
