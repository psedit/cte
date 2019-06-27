## Pyro
The server makes use of service architecture build upon Pyro4. For more information, see [Pyro4's website](https://pythonhosted.org/Pyro4/).

## The Service class
_todo_

Currently, the services are:
* [[Websocket|The Websocket Service]] - This services is the connection of the server with the clients. It forwards messages from both directions to the corresponding receivers. 
* [[Filesystem|The Filesystem Service]] - Contains all file-based logic, and therefore most interactions of the client with the server are computed in here.