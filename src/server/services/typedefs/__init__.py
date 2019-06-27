from typing import Tuple


# Type definition for client address
Address = Tuple[str, int]

UUID = str

ServiceAddress = str


class LockError(Exception):
    """
    Error to indicate the lock creation has failed.
    """
    pass
