"""Simple cache."""
import os
import re
import tempfile
from typing import Optional


class TemporaryFolderCache:
    """Simple cache stores values into temporary folder."""

    def __init__(self):
        tempdir = tempfile.gettempdir()
        self.cache_path = os.path.join(tempdir, "email-embed-images")
        if not os.path.isdir(self.cache_path):
            os.mkdir(self.cache_path)

    def slugify(self, value):
        """Slugify value."""
        value = re.sub('/', '_', value)
        value = re.sub(r'\.', '_', value)
        value = re.sub(r'[^\w\s-]', '', value)
        return re.sub(r'[-\s]+', '-', value)

    def set(self, key: str, value: bytes) -> None:
        """Set value to the cache."""
        fullpath = os.path.join(self.cache_path, self.slugify(key))
        with open(fullpath, "wb") as handle:
            handle.write(value)

    def get(self, key: str) -> Optional[bytes]:
        """Get value from the cache."""
        fullpath = os.path.join(self.cache_path, self.slugify(key))
        if os.path.isfile(fullpath):
            with open(fullpath, "rb") as handle:
                return handle.read()
        return None
