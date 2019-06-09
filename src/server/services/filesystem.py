from server_file import ServerFile
from typing import Dict, List
from service import Service, message_type
import os
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Filesystem(Service):
    """

    """
    def __init__(self, msg_bus) -> None:
        super().__init__(msg_bus)

        # Files sorted by path relative to root dir
        self.file_dict: Dict[str, ServerFile] = {}

        # Check server config for root directory
        # TODO: retrieve from server
        self.root_dir: str = os.path.realpath('../test/')

    @message_type("file-add")
    def add_file(self, msg) -> None:
        """
        Add the file to the Filesystem. Path file is relative to root
        directory.
        """
        path = msg['content']['file_path']
        self.file_dict[path] = ServerFile(self.root_dir, path)

    def list_files(self) -> List[str]:
        """
        Lists all files currently within the file system, relative to
        the root directory.
        """
        return list(self.file_dict.keys())

    def list_files_available(self) -> List[str]:
        """
        Lists all files currently available, but not necessarily added,
        to the file system, relative to the root directory.
        """
        root_dir = self.root_dir()[:-1]
        file_list = []

        for root, dirs, files in os.walk(root_dir):
            for f in files:
                file_list.append(os.path.join(root, f).replace(root_dir, ""))
            for d in dirs:
                file_list.append(os.path.join(root, d).replace(root_dir, ""))

        return file_list

    @message_type("file-content-request")
    def _process_file_content_request(self, msg) -> None:
        """
        Take the file content request message and construct the appropriate response,
        sending the block via a new 'file-content-response' message.
        """
        content = msg["content"]

        end = content["end"]
        start = content["start"]
        file_path = content["file"]
        address = content["request_address"]

        block = self.get_block(file_path, start, end)

        response_content = {"file_content": block}
        self._send_message_client(
            "file-content-response", response_content, address)

    def get_block(self, path: str, start: int = 0, end: int = -1) -> List[str]:
        """
        Returns all line between (and including) a start and end line, split
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

    @message_type("cursor-move")
    def _move_cursor(self, msg) -> None:
        pass
        # response_content = {

        #     }

        # self._send_message_client("cursor-move-broadcast", response_content)


if __name__ == "__main__":
    Filesystem.start()
