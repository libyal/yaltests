"""Tests for the Mac OS stat output parser."""

import unittest

# Note stat we cannot use stat given Python already has a module named stat
from macos import macos_stat

from tests import test_lib


class StatOutputParserTest(test_lib.BaseTestCase):
    """Tests for the Mac OS stat output parser."""

    # TODO: add tests for _parse_date_time
    # TODO: add tests for _parse_hexadecimal

    def test_parse(self):
        """Tests the parse function with HFS+ Mac OS stat output."""
        test_file = self._get_test_file_path(["macos-15.7.4", "stat.hfsplus.35.txt"])
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = macos_stat.StatOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-05-21T01:51:16.000000000Z",
            "change_time": "2026-05-21T01:51:16.000000000Z",
            "creation_time": "2026-05-21T01:51:16.000000000Z",
            "file_mode": 0o100755,
            "group_identifier": 20,
            "inode_number": 35,
            "modification_time": "2026-05-21T01:51:16.000000000Z",
            "number_of_blocks": 0,
            "number_of_links": 1,
            "path": "/tmp/clitooltester/TestVolume/testdir1/xattr1",
            "size": 0,
            "user_identifier": 501,
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
