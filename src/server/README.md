# Collaborative Text Editor - Server

## Build Setup
Ensure that you have python 3.7 or better installed. Some linux distributions have python 3.6.8 or older installed.
In that case, you can use these [ubuntu instructions](https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/).

The [following modules](https://github.com/psedit/cte/blob/develop/src/server/requirements.txt) are needed for the server:
```
Pyro4
sh
coloredlogs
websockets
pytest
path.py
coverage
```

If your python3 is already up-to-date, install each package using: `pip3 install _pkg_name_`
If you had to install python3.7, then use: `python3.7 -m pip install _pkg_nam

## Starting the server
```bash
cd cte/src/server/services
./start_base.sh
```

The server will create files in `cte/src/server/services/file_root`
