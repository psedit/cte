import json
import asyncio
import websockets
from api import get_file_data, open_file_data, edit_file, close_file

async def add_line(path, line):
    async with websockets.connect('ws://127.0.0.1:12345') as sock:
        content = await open_file_data(sock, path)
        # {'piece_table': [['587d41b3-a136-4f15-b372-e28f1300244a', 0, 0, 1]], 'block_list': [[0, False, ['rip']]]}
        pt, bl = content['piece_table'], content['block_list']
        print('edit file:', content)

        if len(pt) != 1 or len(bl) != 1:
            raise RuntimeError("file state inconsistent")

        await edit_file(sock, path, pt[0][0], line)
        print('wait for new data')
        new_content = await get_file_data(sock, path)
        await close_file(sock, path)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(add_line('kaas_is_dood.txt', 'dit had je toch kunnen bedenken'))
