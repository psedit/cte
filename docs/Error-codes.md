# Client
The client merely receives and reports any errors the server has sent.
Whenever the client itself detects an error, it may or may not be get caught and handled.
Currently, we assume this will never happen.

# Server
Whenever an error occurs, the server sends an error response to the client with type `error-response`.
Currently, only the filesystem service can detect and report errors to the client.

## Filesystem service

|name|code|description|
|-----|-----|-----|
|ERROR_WRONG_MESSAGE|1|Unexpected message type|
|ERROR_FILE_NOT_IN_RAM|2|Operation failed because the specified file has not been loaded from disk|
|ERROR_FILE_NOT_JOINED|3|Operation failed because the specified file has not been opened by this client|
|ERROR_FILE_NOT_PRESENT|4|The specified file does not exist|
|ERROR_FILE_ILLEGAL_BLOCK|5|Invalid range in specified piece identifier|
|ERROR_NOT_LOCKED|6|The specified piece is read-only because the associated lock is not owned by this client|
|ERROR_ILLEGAL_PIECE_ID|7|Invalid piece identifier|
|ERROR_FILE_NOT_SAVED|8|The file the client is trying to leave is not saved