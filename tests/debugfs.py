"""Tests for the debugfs stat output parser."""

import unittest

from e2fsprogs import debugfs

from tests import test_lib


class DebugfsStatOutputParserTest(test_lib.BaseTestCase):
    """Tests for the debugfs stat output parser."""

    # TODO: add tests for _parse_date_time
    # TODO: add tests for _parse_decimal
    # TODO: add tests for _parse_file_mode
    # TODO: add tests for _parse_hexadecimal
    # TODO: add tests for _parse_section_default

    def test_parse_with_ext2(self):
        """Tests the parse function with ext2 debugfs stat output."""
        test_file = self._get_test_file_path(["mke2fs-1.47.0", "debugfs.ext2.22.txt"])
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = debugfs.DebugfsStatOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-05-20T17:44:28.893595285Z",
            "change_time": "2026-05-20T17:44:28.894595276Z",
            "creation_time": "2026-05-20T17:44:28.893595285Z",
            "file_mode": 0o100644,
            "file_acl": 0,
            "flags": 0x0,
            "group_identifier": 0,
            "inode_number": 22,
            "modification_time": "2026-05-20T17:44:28.893595285Z",
            "nfs_generation_number": 1803167177,
            "number_of_blocks": 0,
            "number_of_links": 1,
            "project_identifier": 0,
            "size": 0,
            "user_identifier": 0,
            "version": "0x00000000:00000002",
        }
        self.assertEqual(result, expected_result)

    def test_parse_with_ext4(self):
        """Tests the parse function with ext4 debugfs stat output."""
        test_file = self._get_test_file_path(["mke2fs-1.47.0", "debugfs.ext4.22.txt"])
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = debugfs.DebugfsStatOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-05-20T17:44:31.251573649Z",
            "change_time": "2026-05-20T17:44:31.252573640Z",
            "checksum": "0xeadbb557",
            "creation_time": "2026-05-20T17:44:31.251573649Z",
            "file_acl": 0,
            "file_mode": 0o100644,
            "flags": 0x80000,
            "group_identifier": 0,
            "inode_number": 22,
            "modification_time": "2026-05-20T17:44:31.251573649Z",
            "nfs_generation_number": 612045194,
            "number_of_blocks": 0,
            "number_of_links": 1,
            "project_identifier": 0,
            "size": 0,
            "user_identifier": 0,
            "version": "0x00000000:00000002",
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
