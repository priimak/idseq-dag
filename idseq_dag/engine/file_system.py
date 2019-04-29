import os
from urllib.parse import urlparse

from idseq_dag.util.s3 import check_s3_presence_for_file_list

# Collection of classes and utility functions to work with files and directories including those that are found
# in S3 and possibly other key-value stores.

class Path():
    """
    Abstract path formed from url provided to the constructor. Unlike generic url we check that only specific schema
    are allowed. Currently we allow only s3:// and file://
    """
    def __init__(self, url_str):
        self.url =  urlparse(url_str)
        if self.url.scheme == '':
            raise ValueError("Missing scheme")
        elif self.url.scheme != 's3' and self.url.scheme != 'file':
            raise ValueError("Unrecognized scheme")
        self.path = os.path.join(self.url.netloc, self.url.path)

class File(Path):
    """
    Object that represents file.
    """
    def __init__(self, url_str):
        super(File, self).__init__(url_str)
        # We verify that object referred by url_string does not exist or is not a file only in case were scheme
        # is file:// i.e it refers to object in the actual filesystem. Later we can add support for s3:// or
        # any there key-value store that we will choose to support later.
        if self.url.scheme == 'file' and os.path.exists(self.path) \
                and not os.path.isfile(self.path):
            raise RuntimeError("Local " + self.path + " is a directory while expected to be file or non-existent.")

    def withNewPath(self, newPath):
        """
        Create new instance of File object with new path replacing old one.
        """
        File(self.url.scheme + ':' + newPath)

class Dir(Path):
    """
    Object that represents directory.
    """
    def __init__(self, url_str):
        super(Dir, self).__init__(url_str)
        if self.url.scheme == 'file' and os.path.exists(self.path) and not os.path.isdir(self.path):
            raise RuntimeError("Local " + self.path + " is not a directory while expected to be dir or non-existent.")

    def withNewPath(self, newPath):
        """
        Create new instance of Dir object with new path replacing old one.
        """
        Dir(self.url.scheme + ':' + newPath)

    def check_files_exist(self, file_list):
        """
        Verify that files provided in the file_list are present under this directory returning True if all exist
        and False otherwise.
        """
        if self.url.scheme == "s3":
            check_s3_presence_for_file_list(self.url.geturl(), file_list)
        else:
            for file_name in file_list:
                full_file_name = os.path.join(self.path, file_name)
                if not os.path.exists(full_file_name) or not os.path.isfile(full_file_name):
                    return False
            return True
