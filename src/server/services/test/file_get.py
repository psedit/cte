import json
import asyncio
import websockets

def has_file(tree, path):
    """
    Ensure the path is valid in the specified tree
    """
    try:
        l = path.split('/')
        index = 0
        for f in l:
            for t in tree:
                if isinstance(t, list) and t[0] == l[index]:
                    tree = t[1]
                    index += 1
                    break

        if index == len(l) - 1:
            for t in tree:
                if t == f:
                    return True
        return False
    except IndexError:
        return False

async def get_file(path):
    async with websockets.connect('ws://127.0.0.1:12345') as websocket:
        data = {"type": "file-list-request", "content": ""}
        msg = json.dumps(data)
        await websocket.send(msg)

        msg = await websocket.recv()
        data = json.loads(msg)
        file_tree = data['content']['root_tree']

        if not has_file(file_tree, path):
            raise RuntimeError('file not found')

        data = {"type": "file-join", "content": {"file_path": path}}
        msg = json.dumps(data)
        await websocket.send(msg)

        data = {"type": "file-content-request", "content": {"file_path": path}}
        msg = json.dumps(data)
        await websocket.send(msg)

        msg = await websocket.recv()
        data = json.loads(msg)
        return data['content']

async def dump_content(path):
    content = await get_file(path)
    print(content['block_list'])

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(dump_content('code/service.py'))
