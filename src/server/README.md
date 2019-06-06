# CTE Database
## Requirements
This project requires Docker 1.13.1 or newer, and docker-compose 1.10.0 or
newer for hosting the database.

### Linux
You can install Docker and docker-compose using your password manager, e.g.
`sudo apt install docker.io docker-compose`.

Note that you will need root rights for everything Docker. It is
[not recommended][docker-attack-surface] to add yourself to the `docker` group.

### macOS
On macOS, it's easiest to install Docker using Homebrew Cask:
`brew cask install docker`. This will also install docker-compose.


### Windows
You can get Docker for Windows from the [Docker store][docker-windows]

## Configuration
Currently, you only need to choose a password for the database by creating a
`.env` file with the following contents:

```sh
DATABASE_PASSWORD=...
```

Just make up a strong, random password here.

### Changing Password
You can change it by opening a mysql shell with

```sh
docker-compose run database mysql cte -u cte -p
```

Then, enter the *old* password and execute the following command:

```sql
ALTER USER cte IDENTIFIED BY 'new_random_password';
```

Close the shell with `\q` and edit `.env` to the new password.

## Running
Open a terminal in the server folder, run `docker-compose up -d`, the database should now be available through adminer at `localhost:8080`


[docker-install]: https://docs.docker.com/install/
[docker-compose-install]: https://docs.docker.com/compose/install/
[docker-windows]: https://store.docker.com/editions/community/docker-ce-desktop-windows
[docker-attack-surface]: https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface
