These pages are intended to provide support for users of the collaborative editor. If more information is necessary, please contact one of the project administrators.
 
The application consists of two parts, the _editor component_ which all users will run on their own computer, and the _server component_, which one user will run on their computer or dedicated server. Clients must connect to the address of the server to be able to edit the files, which will be present on the computer running the server component, together.

The pages in this subsection will provide information of both components of the application, as well as describe how to install, start and use them. At the moment, you need to download the source and compile the project yourself. See these instructions below for more details.

## The Editor client

The editor, which we refer to as 'the client', is build in Javascript with [Electron](https://electronjs.org/). This means most major platforms are supported. 

Currently, you need to build the client yourself, which can be done easily using [npm](https://www.npmjs.com/). See [[here|Installation Guide]] for more information.

## The Server

The server is build in python 3.7 and runs with [docker](https://www.docker.com/), which should run on most platforms, although only Linux is actively tested. Once again, see [[here|Installation Guide]] for more information.