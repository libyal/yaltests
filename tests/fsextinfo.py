"""Tests for the libfsext fsextinfo stat (-E or -F) output parser."""

import unittest

from libfsext import fsextinfo

from tests import test_lib


class FsExtInfoOutputParserTest(test_lib.BaseTestCase):
    """Tests for the libfsext fsextinfo stat output parser."""

    # pylint: disable=protected-access

    def test_parse_with_ext2(self):
        """Tests the parse function with ext2 fsextinfo stat output."""
        test_file = self._get_test_file_path(["mke2fs-1.47.0", "fsextinfo.ext2.22.txt"])
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = fsextinfo.FsExtInfoOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-05-20T17:44:28.893595285Z",
            "change_time": "2026-05-20T17:44:28.894595276Z",
            "creation_time": "2026-05-20T17:44:28.893595285Z",
            "deletion_time": None,
            "file_mode": 0o100644,
            "group_identifier": 0,
            "inode_number": 22,
            "metadata": {"version": "20260626"},
            "modification_time": "2026-05-20T17:44:28.893595285Z",
            "number_of_links": 1,
            "size": 0,
            "user_identifier": 0,
        }
        self.assertEqual(result, expected_result)

    def test_parse_with_ext4(self):
        """Tests the parse function with ext4 fsextinfo stat output."""
        test_file = self._get_test_file_path(["mke2fs-1.47.0", "fsextinfo.ext4.22.txt"])
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = fsextinfo.FsExtInfoOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-05-20T17:44:31.251573649Z",
            "change_time": "2026-05-20T17:44:31.252573640Z",
            "creation_time": "2026-05-20T17:44:31.251573649Z",
            "deletion_time": None,
            "file_mode": 0o100644,
            "group_identifier": 0,
            "inode_number": 22,
            "metadata": {"version": "20260626"},
            "modification_time": "2026-05-20T17:44:31.251573649Z",
            "number_of_links": 1,
            "size": 0,
            "user_identifier": 0,
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
