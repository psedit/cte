import asyncio
import websockets
from api import file_open_data, file_lock, file_lock_insert


async def bogus_lock(path, what, exists=True):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        if not exists:
            await file_open(sock, path, exists)
            return
        content = await file_open_data(sock, path)
        pt, bl = content['piece_table'], content['block_list']
        print('edit file:', content)

        if len(pt) < 1 or len(bl) < 1:
            raise RuntimeError("file state inconsistent")

        length = 0
        uuid = pt[0][0]
        if what is None:
            pass
        elif what == 'length':
            length = -1
        elif what == 'id':
            uuid = 'the pope uses dope'
        await file_lock(sock, path, uuid, 0, length)


async def insert_lock(path):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        content = await file_open_data(sock, path)
        pt, bl = content['piece_table'], content['block_list']
        print('edit file:', content)

        if len(pt) < 1 or len(bl) < 1:
            raise RuntimeError("file state inconsistent")

        length = 1
        uuid = pt[0][0]
        await file_lock_insert(sock, path, uuid, 0, length)


async def run_tests():
    await insert_lock('kaas_is_dood.txt')
    await bogus_lock('kaas_is_dood.txt', 'id')
    await bogus_lock('txt.kaas_was_dood.txt', None, False)
    await bogus_lock('kaas_is_dood.txt', 'length')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run_tests())
