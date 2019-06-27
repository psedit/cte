## Setup
In order to get started quickly, you need to follow these steps:
* Download the [source code](https://github.com/psedit/cte/archive/develop.zip)
* Setup client:
  * Install npm:
    * Using apt package manager: `sudo apt install npm`
    * Or directly from the [official website](https://nodejs.org/en/)
  * In `src/client`, run the instructions below.
  * The executable program can be found in  the `build` folder
* Setup server:
  * Install [Docker](https://docker.com)
  * Go to the `src/server` directory.
  * Build the Docker image using `docker build -t teamcode .`
      * (the image will probably be uploaded to docker repos at some point, but don't quote us on that)

## Building and running
### Client
```
cd src/client
npm install
npm run build
```
### Server
* Run the Docker image generated in the setup section using `docker run`
  * The server runs inside the container and listens on port 12345
  * To run the server interactively and map the container port to a host port, run `docker run -itp <host-port>:12345 teamcode`)