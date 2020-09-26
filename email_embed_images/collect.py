"""Image collector module."""
import hashlib
import logging
import mimetypes
import os
import re
from typing import Dict, Iterable, List, Optional, Tuple, Union

import requests
from lxml import etree


class ImageNotFound(Exception):
    """Image not found."""


class CollectImages:
    """Find links to images in HTML code and create a list of contents."""

    def __init__(self, cache=None, folders_root: List[str] = None,
                 requests_timeout: Union[int, Tuple[int, int]] = None) -> None:
        self.pretty_print = False
        # https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
        self.requests_timeout = requests_timeout
        self.cache = cache
        self.folders_root = ["."] if folders_root is None else folders_root

    def log_error(self, error: Exception) -> None:
        """Log error, then raise if is is set."""
        logging.error(error)

    def conditionally_raise(self, error: ImageNotFound) -> None:
        """Raise if it is needed."""

    def get_replacement_file(self, path) -> Optional[bytes]:
        """Get replacement file when original missing."""
        return None

    def cache_set(self, key: str, value: bytes) -> None:
        """Set value to the cache."""
        if self.cache is not None:
            self.cache.set(key, value)

    def cache_get(self, key: str) -> Optional[bytes]:
        """Get value from the cache."""
        if self.cache is not None:
            return self.cache.get(key)
        return None

    def load_file_from_url(self, url: str) -> bytes:
        """Load file from url."""
        cached_content = self.cache_get(url)
        if cached_content is not None:
            return cached_content
        try:
            req = requests.get(url, timeout=self.requests_timeout)
            req.raise_for_status()
            content = req.content
            self.cache_set(url, content)
        except requests.RequestException as err:
            self.log_error(err)
            repl_content = self.get_replacement_file(url)
            if repl_content is None:
                raise ImageNotFound(err)
            content = repl_content
        return content

    def load_file_from_folders(self, path: str) -> bytes:
        """Load file from file."""
        for root in self.folders_root:
            fullpath = os.path.join(root, path)
            if os.path.isfile(fullpath):
                with open(fullpath, "rb") as handle:
                    return handle.read()
        content = self.get_replacement_file(path)
        if content is not None:
            return content
        raise ImageNotFound()

    def load_file(self, src: str) -> bytes:
        """Load image from source."""
        if re.match("https?://", src):
            content = self.load_file_from_url(src)
        else:
            content = self.load_file_from_folders(src)
        return content

    def init_cid(self) -> None:
        """Initialize counter of images."""
        self.position = 0

    def get_next_cid(self) -> str:
        """Get next CID for related content."""
        self.position += 1
        return "img{}".format(self.position)

    def _get_mime_type(self, path: str) -> List[str]:
        ctype = mimetypes.guess_type(path)[0]
        if ctype is None or "/" not in ctype:
            return ["", ""]
        return ctype.split('/', 1)

    def collect_images(self, html_body: str, encoding: str = "UTF-8") -> Tuple[str, List[Tuple[str, str, str, bytes]]]:
        """Collect images from html code.

        Return html with iamge src=cid and list of tuple with (maintype, subtype, cid, imagebytes).
        """
        images = []
        reader = etree.HTMLParser(recover=True, encoding=encoding)
        root = etree.fromstring(html_body, reader)
        self.init_cid()
        same_content = {}  # type: Dict[bytes, str]
        # Search elements <img src="..."> and <input type="image" src="...">
        for image in root.xpath("//img | //input[@type='image']"):
            image_src = image.attrib["src"]
            try:
                image_content = self.load_file(image_src)
            except ImageNotFound as err:
                self.log_error(err)
                self.conditionally_raise(err)
                continue
            content_hash = hashlib.md5(image_content).digest()
            if content_hash in same_content:
                cid = same_content[content_hash]
            else:
                cid = self.get_next_cid()
                same_content[content_hash] = cid
                maintype, subtype = self._get_mime_type(image_src)
                images.append((maintype, subtype, cid, image_content))
            image.attrib["src"] = "cid:{}".format(cid)
        html_content = etree.tostring(root, encoding=encoding, pretty_print=self.pretty_print)
        return html_content.decode(encoding), images

    def collect_attachments(self, paths_or_urls: Iterable[str]) -> List[Tuple[str, str, str, bytes]]:
        """Collect attachment contents from paths or urls."""
        attachments = []
        same_content = []  # type: List[bytes]
        for src in paths_or_urls:
            try:
                content = self.load_file(src)
            except ImageNotFound as err:
                self.log_error(err)
                self.conditionally_raise(err)
                continue
            content_hash = hashlib.md5(content).digest()
            if content_hash in same_content:
                continue
            same_content.append(content_hash)
            maintype, subtype = self._get_mime_type(src)
            filename = os.path.basename(src)
            attachments.append((maintype, subtype, filename, content))
        return attachments
