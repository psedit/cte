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

async def get_file_data(sock, path):
    data = {"type": "file-content-request", "content": {"file_path": path}}
    msg = json.dumps(data)
    await sock.send(msg)

    msg = await sock.recv()
    data = json.loads(msg)
    return data['content']

async def open_file(sock, path):
    data = {"type": "file-list-request", "content": ""}
    msg = json.dumps(data)
    await sock.send(msg)

    msg = await sock.recv()
    data = json.loads(msg)
    file_tree = data['content']['root_tree']

    if not has_file(file_tree, path):
        raise RuntimeError('file not found')

    data = {"type": "file-join", "content": {"file_path": path}}
    msg = json.dumps(data)
    await sock.send(msg)

async def open_file_data(sock, path):
    await open_file(sock, path)
    return await get_file_data(sock, path)

async def close_file(sock, path, exit=True):
    data = {
        "type": "file-leave",
        "content": {"file_path": path, "force_exit": str(exit)}
    }
    msg = json.dumps(data)
    await sock.send(msg)

async def edit_file(sock, path, uuid, content):
    payload = {
        "file_path": path,
        "piece_uuid": uuid,
        "content": content
    }
    data = {"type": "file-delta", "content": payload}
    msg = json.dumps(data)
    await sock.send(msg)
