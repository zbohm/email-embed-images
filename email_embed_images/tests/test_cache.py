import os

from pyfakefs.fake_filesystem_unittest import TestCase

from email_embed_images.cache import TemporaryFolderCache


class TestCache(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_slugify(self):
        cache = TemporaryFolderCache()
        slug = cache.slugify("https://example.com/path/File name.png")
        self.assertEqual(slug, "https__example_com_path_File-name_png")

    def test_get(self):
        cache = TemporaryFolderCache()
        self.assertIsNone(cache.get("foo"))
        with open(os.path.join(cache.cache_path, "foo"), "w") as handle:
            handle.write("ok")
        self.assertEqual(cache.get("foo"), b"ok")

    def test_set(self):
        cache = TemporaryFolderCache()
        cache.set("foo", b"value")
        with open(os.path.join(cache.cache_path, "foo")) as handle:
            value = handle.read()
        self.assertEqual(value, "value")
