import hashlib


class FileHash:
    FILE_CHUNK_SIZE = 4096
    """
    Utility methods for hashing files, verifying hashes, etc.
    The main purpose for this is to ensure multiple files aren't uploaded by the end user.
    """
    @staticmethod
    def hash_file(file_path: str) -> str:
        with open(file_path, "rb") as fh:
            hl = hashlib.md5()
            chunk = fh.read(FileHash.FILE_CHUNK_SIZE)
            while chunk:
                hl.update(chunk)
                chunk = fh.read(4096)
            return 'md5: {0}'.format(hl.hexdigest())

