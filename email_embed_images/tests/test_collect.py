import os
from unittest import TestCase
from unittest.mock import patch

import requests_mock
from pyfakefs.fake_filesystem_unittest import TestCase as FakeFsTestCase

from email_embed_images.cache import TemporaryFolderCache
from email_embed_images.collect import CollectImages, ImageNotFound


class TestCollectImagesCacheAndLoadFile(FakeFsTestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_cache_set_no_backend(self):
        collector = CollectImages()
        collector.cache_set("foo", b"ok")
        cache = TemporaryFolderCache()
        filepath = os.path.join(cache.cache_path, "foo")
        self.assertFalse(os.path.isfile(filepath))

    def test_cache_set(self):
        collector = CollectImages(cache=TemporaryFolderCache())
        collector.cache_set("foo", b"ok")
        with open(os.path.join(collector.cache.cache_path, "foo")) as handle:
            value = handle.read()
        self.assertEqual(value, "ok")

    def test_cache_get_no_backend(self):
        collector = CollectImages()
        self.assertIsNone(collector.cache_get("foo"))

    def test_cache_get(self):
        collector = CollectImages(cache=TemporaryFolderCache())
        with open(os.path.join(collector.cache.cache_path, "foo"), "w") as handle:
            handle.write("ok")
        self.assertEqual(collector.cache_get("foo"), b"ok")

    def test_load_file_from_folders(self):
        with open("foo.txt", "w") as handle:
            handle.write("ok")
        collector = CollectImages()
        content = collector.load_file_from_folders("foo.txt")
        self.assertEqual(content, b"ok")

    def test_load_file_from_folders_not_found(self):
        collector = CollectImages()
        with self.assertRaises(ImageNotFound):
            collector.load_file_from_folders("foo.txt")

    def test_load_file_from_folders_get_replacement_file(self):
        class WithDefaultImage(CollectImages):
            def get_replacement_file(self, path):
                return b"ok" if path == "foo.txt" else None
        collector = WithDefaultImage()
        content = collector.load_file_from_folders("foo.txt")
        self.assertEqual(content, b"ok")

    @requests_mock.Mocker()
    def test_load_file_from_internet(self, mock_req):
        mock_req.get("https://example.com/path/file.png", text='PNG')
        collector = CollectImages()
        content = collector.load_file("https://example.com/path/file.png")
        self.assertEqual(content, b"PNG")

    def test_load_file_from_local_folder(self):
        with open("file.png", "w") as handle:
            handle.write("PNG")
        collector = CollectImages()
        content = collector.load_file("file.png")
        self.assertEqual(content, b"PNG")

    @requests_mock.Mocker()
    @patch("email_embed_images.collect.logging")
    def test_collect_images(self, mock_req, mock_logging):
        with open("img-1.png", "w") as handle:
            handle.write("PNG-1")
        mock_req.get("https://example.com/path/img-2.png", text='PNG-2')
        html = """
            <img src="img-1.png">
            <img src="not-found-1.jpg">
            <img src="https://example.com/path/img-2.png">
            <input type="image" src="https://example.com/path/img-2.png">
            <input type="image" src="img-1.png">
            <input type="image" src="not-found-2.jpg">
        """
        collector = CollectImages()
        body, images = collector.collect_images(html)
        self.assertEqual(body, """<html><body><img src="cid:img1"/>
            <img src="not-found-1.jpg"/>
            <img src="cid:img2"/>
            <input type="image" src="cid:img2"/>
            <input type="image" src="cid:img1"/>
            <input type="image" src="not-found-2.jpg"/>
        </body></html>""")
        self.assertEqual(images, [
            ('image', 'png', 'img1', b'PNG-1'),
            ('image', 'png', 'img2', b'PNG-2'),
        ])
        self.assertTrue(mock_logging.error.called)

    @requests_mock.Mocker()
    @patch("email_embed_images.collect.logging")
    def test_collect_attachments(self, mock_req, mock_logging):
        with open("picture.png", "w") as handle:
            handle.write("PNG")
        with open("duplicate.png", "w") as handle:
            handle.write("PNG")
        mock_req.get("https://example.com/path/picture.gif", text='GIF')
        attachments = (
            'picture.png',
            'not-found.jpg',
            'duplicate.png',
            'https://example.com/path/picture.gif',
        )
        collector = CollectImages()
        attachs = collector.collect_attachments(attachments)
        self.assertEqual(attachs, [
            ('image', 'png', 'picture.png', b'PNG'),
            ('image', 'gif', 'picture.gif', b'GIF'),
        ])
        self.assertTrue(mock_logging.error.called)

    def test_collect_attachments_unknown_mime_type(self):
        with open("unknown.foo", "w") as handle:
            handle.write("FOO")
        collector = CollectImages()
        attachs = collector.collect_attachments(('unknown.foo', ))
        self.assertEqual(attachs, [('', '', 'unknown.foo', b'FOO')])

    def test_load_file_from_url_from_cache(self):
        cache = TemporaryFolderCache()
        cache.set("https://example.com/path/picture.png", b'PNG')
        collector = CollectImages(cache=cache)
        content = collector.load_file_from_url("https://example.com/path/picture.png")
        self.assertEqual(content, b'PNG')


class TestCollectImages(TestCase):

    @patch("email_embed_images.collect.logging")
    def test_log_error(self, mock_logging):
        collector = CollectImages()
        collector.log_error(ImageNotFound())
        self.assertTrue(mock_logging.error.called)

    def test_conditionally_raise(self):
        class MyClass(CollectImages):
            def conditionally_raise(self, error):
                raise error

        collector = CollectImages()
        collector.conditionally_raise(ImageNotFound())

        collector = MyClass()
        with self.assertRaises(ImageNotFound):
            collector.conditionally_raise(ImageNotFound())

    def test_get_replacement_file(self):
        collector = CollectImages()
        self.assertIsNone(collector.get_replacement_file("path"))

    @requests_mock.Mocker()
    def test_load_file_from_url(self, mock_req):
        mock_req.get("https://example.com/path/file.png", text='PNG')
        collector = CollectImages()
        content = collector.load_file_from_url("https://example.com/path/file.png")
        self.assertEqual(content, b'PNG')

    @requests_mock.Mocker()
    @patch("email_embed_images.collect.logging")
    def test_load_file_from_url_not_found(self, mock_req, mock_logging):
        mock_req.get("https://foo.foo/none", text='Not Found', status_code=404)
        collector = CollectImages()
        with self.assertRaises(ImageNotFound):
            collector.load_file_from_url("https://foo.foo/none")
        self.assertTrue(mock_logging.error.called)

    @requests_mock.Mocker()
    @patch("email_embed_images.collect.logging")
    def test_load_file_from_url_not_found_use_replacemnt(self, mock_req, mock_logging):
        class WithDefaultImage(CollectImages):
            def get_replacement_file(self, path):
                return b"ok"
        mock_req.get("https://foo.foo/none", text='Not Found', status_code=404)
        collector = WithDefaultImage()
        content = collector.load_file_from_url("https://foo.foo/none")
        self.assertEqual(content, b'ok')
        self.assertTrue(mock_logging.error.called)

    def test_init_cid(self):
        collector = CollectImages()
        collector.init_cid()
        self.assertEqual(collector.position, 0)

    def test_get_next_cid(self):
        collector = CollectImages()
        collector.position = 0
        self.assertEqual(collector.get_next_cid(), "img1")
        self.assertEqual(collector.get_next_cid(), "img2")
        self.assertEqual(collector.get_next_cid(), "img3")
