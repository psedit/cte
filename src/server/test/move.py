import asyncio
import websockets
from api import file_move

async def move_file(old, new):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        await file_move(sock, old, new)


async def run_tests():
    await move_file('kaas_is_dood.txt', 'kaas_was_dood.txt')
    await move_file('kaas_was_dood.txt', 'kaas_is_dood.txt')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run_tests())
