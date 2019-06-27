import json


def has_file(tree, path):
    """
    Ensure the path is valid in the specified tree
    """
    try:
        lst = path.split('/')
        index = 0
        for f in lst:
            for t in tree:
                if isinstance(t, list) and t[0] == lst[index]:
                    tree = t[1]
                    index += 1
                    break

        if index == len(lst) - 1:
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


async def join_file(sock, path):
    data = {"type": "file-join", "content": {"file_path": path}}
    msg = json.dumps(data)
    await sock.send(msg)


async def file_open(sock, path, exists=True):
    data = {"type": "file-list-request", "content": ""}
    msg = json.dumps(data)
    await sock.send(msg)

    msg = await sock.recv()
    data = json.loads(msg)
    file_tree = data['content']['root_tree']

    if has_file(file_tree, path) != exists:
        raise RuntimeError('file not found')

    await join_file(sock, path)


async def file_open_data(sock, path):
    await file_open(sock, path)
    return await get_file_data(sock, path)


async def close_file(sock, path, exit=True):
    data = {
        "type": "file-leave",
        "content": {"file_path": path, "force_exit": str(exit)}
    }
    msg = json.dumps(data)
    await sock.send(msg)


async def fetch_files(sock):
    data = {"type": "file-project-request", "content": ""}
    msg = json.dumps(data)
    await sock.send(msg)

    msg = await sock.recv()
    print('msg:', msg)
    #if msg['type'] != "file-project-response":
        #raise ValueError("invalid type:", msg['type'])

    return json.loads(msg)

async def edit_file(sock, path, uuid, content):
    payload = {
        "file_path": path,
        "piece_uuid": uuid,
        "content": content
    }
    data = {"type": "file-delta", "content": payload}
    msg = json.dumps(data)
    await sock.send(msg)


async def file_lock(sock, path, uuid, offset, length):
    content = {"file_path": path, "piece_uuid": uuid, "offset": offset, "length": length}
    data = {"type": "file-lock-request", "content": content}
    msg = json.dumps(data)
    await sock.send(msg)

    msg = await sock.recv()
    data = json.loads(msg)
    return data['content']


async def save_file(sock, path):
    data = {"type": "file-save", "content": {"file_path": path}}
    msg = json.dumps(data)
    await sock.send(msg)

    print('wait for response')

    msg = await sock.recv()
    return json.loads(msg)
