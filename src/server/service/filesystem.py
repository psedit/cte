from fileio import ServerFile
from typing import Dict, List
import sys
import os
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class FileSystem:
    # Files sorted by path relative to root dir
    file_dict: Dict[str,ServerFile] = {}
    root_dir: str
    msg_pass = None

    def __init__(self, msg_pass):
        self.msg_pass = msg_pass

        # Check server config for root directory
        # TODO: retrieve from server
        self.root_dir = os.getcwd().replace('service','') + "test/"

    def handle_msg(self, msg):
        pass

    def add_file(self, path: str) -> None:
        """Add the file to the FileSystem. Path file is relative to root
        directory.
        """

        self.file_dict[path] = ServerFile(self.root_dir, path)

    def get_block(self, path: str, start: int = 0, end: int = -1) -> List[str]:
        """Returns all line between (and including) a start and end line, split
        up per line, of the specified file within the file system.

        Keyword arguments:
        path -- Path to the file relative to the root directory.
        start -- Line number indicating start position
        end -- Line number indicating end position, -1 indicates the last line.
        """

        if path in self.file_dict.keys():
            return self.file_dict[path].retrieve_block(start, end)
        else:
            print("Error: File is not present in the file system.")
            return None



def main():
    # Connect to message handler
    try:
        msg_pass = Pyro4.Proxy("service.message_passer")
    except Exception as e:
        msg_pass = None
        print("Message passer service not reachable")

    # Register Pyro4 daemon
    filesystem = FileSystem(msg_pass)
    filesystem_d = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    filesystem_uri = filesystem_d.register(filesystem)
    ns.register("service.filesystem", filesystem_uri)

    # Start request loop
    print("FileSystem service running")
    filesystem_d.requestLoop()

    daemon = Pyro4.Daemon()                # make a Pyro daemon
    ns = Pyro4.locateNS()                  # find the name server
    uri = daemon.register(FileSystem)   # register the greeting maker as a Pyro object
    ns.register("service.filesystem", uri)   # register the object with a name in the name server

if __name__ == "__main__":
    main()
