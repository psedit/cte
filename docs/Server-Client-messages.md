The CTE server employs various macroservices for functions like file i/o, client management, etc. These services communicate by way of messages through the MessageBus service.

Most of these messages will be send from and to the connected clients, which will be expected to communicate via this system.

## Basic structure
Each message has the following basic structure:

```
{
    "type": <message type>,
    "uuid": <message uuid>,
    "response_uuid": <uuid of the message to which this message is a response>
    "sender": <sender service or sender (client address, username)>,
    "pref_dest": <preferred receiving service>,
    "content": <message payload>
}
```

Note that the `sender` field contains the necessary information for the server to give an appropriate response. It is a list which contains the client address (at index 0) and the username (at index 1). 

## Message list
The list below details the specific fields of the `content` field for each message type and a short description.

### General messages

#### `net-send`
Sends a message to all listed clients. All response and broadcast messages are send via this message type, which is why response messages do not contain an `address` field.
```
{
    "response_addrs": <address(es) to which response is sent>,
    "msg": <message to be sent to client>
}
```

#### `error-response`
A message send directly to the clients of which the server has encountered a error during processing their request message. The `message` field contains the full description, and error codes can be used whenever further action is required from the client.
```
{
    "message": <error-specific message>,
    "error_code": <int which signals the error type>
}
```

### Client stuff

#### `client-list-request`
```
{
    None
}
```

#### `client-list-request`
```
{
    "client_list": <list of connected client adresses>
}
```

#### `client-disconnect`
```
{
    "address": <address of disconnected client>
}
```

### File General

#### `file-join`
Tells the server that the specified client joins the file, after which it becomes eligible for `file-content-request` and `cursor-move` messages. Clients are expected to join multiple files, corresponding to which files are opened (in tabs for example) in their editor.
```
{
    "file_path": <file to join>
}
```

#### `file-leave`
Leaves the file, undoing the `file-join` message. Clients should always leave the file when closing the file/tab on the client side, such that unused files can be removed from server RAM. When the file is unsaved, and the client is the last one accessing the file, does not remove the client but instead sends an exception message warning the user (see below). Set `force_exit` to True/1 to leave anyway, losing all file modifications.
```
{
    "file_path": <file to leave>,
    "force_exit": <flag to allow losing unsaved changes>
}
```

#### `file-leave-broadcast`
```
{
    "file_path": <file which is left>,
    "username": <user which left>
}
```

#### `file-list-request`
Messages for requesting a list of the available files in the server (send by client) and the corresponding response (send by the server). 
```
{
    None
}
```

#### `file-list-response`
```
{
    "root_tree": <directory tree of the server files>
}
```

#### `file-list-broadcast`
Broadcast variant of the above messages. Used by the server when the file list is updated.
```
{
    "root_tree": <directory tree of the server files>
}
```

#### `file-content-request`
Requests the piece table of the specified file. Only send this message if the client has joined the file in question using the `file-join` message.
```
{
    "file_path": <requested file path>
}
```

#### `file-content-response`
Sends back the requested file data to the client. Send by the server only. It contains the complete piece table, as well as a list of blocks to which the piece table refers.
```
{
    "piece_table": [[uuid, block_id, start, length, username], ...]
    "block_list": [[block_id, is_locked (bool), [lijst van strings (regels)]], ...]
}
```

#### `file-change`
Add the file to the server, optionally filling its contents with `file_content` if non-empty.
```
{
    "old_path": <path of file, empty if file is new>,
    "new_path": <new path of file, empty if file is deleted>
    "file_content": <the content of the file as a string>
}
```

#### `file-change-broadcast`
Changes the name of a given file.
```
{
    "file_path": <path of file, empty if file is new>,
    "new_path": <new path of file, empty if file is deleted>
}
```


### File input

#### `file-delta` and `file-delta-broadcast`
```
{
    "file_path": <relative path of the file>
    "piece_uuid": <uuid of the piece in which content has changed>
    "content": <replacement data for selected row in specified piece>
}
```

#### `file-save`
Saves the modifications of the file on the server to disk. 
```
{
    "file_path": <relative path of the file>
}
```

#### `file-save-broadcast`
Tell clients whether a file is saved
```
{
    "file_path": <relative path of the file>,
    "username": <username of the client who saved the file>
}
```

#### `file-project-request`
Request the complete working directory currently present on the server.
```
{  
}
```

#### `file-project-response`
```
{
    "data": <base64 encoded string with binary data of project as tar file>
}
```

#### `file-folder-upload`
```
{
    "file_path": <path to which folder should be uploaded>
    "data": <base64 encoded string with binary data of project as tar file>
}
```

### Cursor movement

#### `cursor-move`
Moves the client's cursor to the specified location within the file.
```
{
    "file_path": <relative path of the file>,
    "piece_id": <id of the piece containing the cursor>,
    "offset": <cursor position offset in rows from the start of the containing piece>,
    "column": <cursor position column>
}
```

#### `cursor-move-broadcast`
Broadcast of the new cursor position of the specified client.
```
{
    "username": <username of moving client>,
    "file_path": <relative path of the file>,
    "piece_id": <id of the piece containing the cursor>,
    "offset": <cursor position offset in rows from the start of the containing piece>,
    "column": <cursor position column>
}
```

#### `cursor-list-request`
Request for the cursor list for the specified file and the corresponding response message. Also returns idle status along with the position.
```
{
    "file_path": <relative path of the file>
}

```
#### `cursor-list-response`
```
{
    "cursor_list": <list of cursors: [username, piece_id, offset, column]>
}
```

### File locks

#### `file-lock-request`
Request a lock starting in the specified piece with offset `offset` and with length `length`.
If successful, a table change broadcast message is send (see below).
```
{
    "file_path": <path of file in which the lock is requested>,
    "piece_uuid": <uuid of the piece in which to add the lock>
    "offset": <offset from piece start>
    "length": <length of the lock>
}
```

#### `file-lock-response`
```
{
    "file_path": <path of the file in which the lock is given>,
    "success": <boolean which signals whether the lock was accepted>
}
```

#### `file-unlock-request`
Request to unlock the specified lock.
```
{
    "file_path": <path of file in which the lock is requested>,
    "lock_id": <id string of the locked block which is to be unlocked>
}
```

#### `file-lock-insert-request`
Request a lock after the specified piece, in order to make it possible to insert new locks between existing locks, or at the start/end of the file. To specify the start of the file, make `piece_uuid` equal "".
```
{
    "file_path": <path of file in which the lock is requested>,
    "piece_uuid": <uuid of the piece in which to add the lock>
}
```

#### `file-piece-table-change-broadcast`
Forwards table changes, thus lock updates, to the clients. Resends the complete table. `changed_blocks` further describes the change within the table, where `is_removed` is False when the lock is added or not removed, and True when it is removed. When `is_locked` is False, you can ignore the `lines` field.
```
{
    "file_path": file_path,
    "piece_table": [[uuid, block_id, start, length, username], ...],
    "changed_blocks": [[block_id, is_removed (bool), [lines]], ... ]
}
```

#### `file-lock-list-request` 
```
{
    "file_path": <path of the file to request the lock list for>
}
```

#### `file-lock-list-response` 
```
{
    "file_path": <path of the file which contains the locks>
    "lock_list": <list of the locks in the file: [[username, lock_uuid], ...]>
}
```




### User management

#### `login-request`
Login to the server. This registers the client's username, but only if it is not already in use. The actual username `new_username` is returned in `login-response` and should always be used by the client in order for the server its messages.  
```
{
    "username": <client username>
}
```

#### `login-response`
```
{
    "succeed": <True/False>
    "new_username": <updated client username>
}
```