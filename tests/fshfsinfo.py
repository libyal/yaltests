"""Tests for the libfshfs fshfsinfo stat (-E or -F) output parser."""

import unittest

from libfshfs import fshfsinfo

from tests import test_lib


class FsHfsInfoOutputParserTest(test_lib.BaseTestCase):
    """Tests for the libfshfs fshfsinfo stat output parser."""

    # pylint: disable=protected-access

    def test_parse(self):
        """Tests the parse function with fshfsinfo stat output."""
        test_file = self._get_test_file_path(
            ["macos-15.7.4", "fshfsinfo.hfsplus.35.txt"]
        )
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = fshfsinfo.FsHfsInfoOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-05-21T01:51:16Z",
            "added_time": "2026-05-21T01:51:16Z",
            "change_time": "2026-05-21T01:51:16Z",
            "creation_time": "2026-05-21T01:51:16Z",
            "backup_time": None,
            "file_mode": 0o100644,
            "group_identifier": 20,
            "inode_number": 35,
            "metadata": {"version": "20260626"},
            "modification_time": "2026-05-21T01:51:16Z",
            "name": "xattr1",
            "number_of_links": 1,
            "parent_identifier": 21,
            "size": 0,
            "user_identifier": 501,
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
