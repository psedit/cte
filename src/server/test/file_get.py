import asyncio
import websockets
from api import file_open_data


async def dump_content(path):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        content = await file_open_data(sock, path)
        print(content['block_list'])


async def bogus_open(path):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        await file_open(sock, path, False)


async def run_tests():
    await dump_content('kaas_is_dood.txt')
    await bogus_open('txt.bogus.txt')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run_tests())
