"""Tests for the libfsapfs fsapfsinfo stat (-E or -F) output parser."""

import io
import unittest

from libfsapfs import fsapfsinfo

from tests import test_lib


class FsApfsInfoOutputParserTest(test_lib.BaseTestCase):
    """Tests for the libfsapfs fsapfsinfo stat output parser."""

    # pylint: disable=protected-access

    def test_parse_date_time(self):
        """Tests the _parse_date_time function."""
        parser = fsapfsinfo.FsApfsInfoOutputParser()

        self.assertIsNone(parser._parse_date_time("Not set (0)"))
        self.assertEqual(
            parser._parse_date_time("2026-08-04T11:09:25.297329545Z"),
            "2026-08-04T11:09:25.297329545Z",
        )
        self.assertEqual(
            parser._parse_date_time("2026-08-04T11:09:25Z"),
            "2026-08-04T11:09:25Z",
        )
        self.assertEqual(
            parser._parse_date_time("May 20, 2026 17:44:28 UTC"),
            "2026-05-20T17:44:28Z",
        )
        self.assertEqual(
            parser._parse_date_time("May 20, 2026 17:44:28.893595285 UTC"),
            "2026-05-20T17:44:28.893595285Z",
        )

        with self.assertRaises(RuntimeError):
            parser._parse_date_time("2026-99-04T11:09:25.297329545Z")

        with self.assertRaises(RuntimeError):
            parser._parse_date_time("bogus")

    def test_parse(self):
        """Tests the parse function with fsapfsinfo stat output."""
        test_file = self._get_test_file_path(
            ["macos-26.7.2", "fsapfsinfo.apfs.36.txt"]
        )
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = fsapfsinfo.FsApfsInfoOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-11-21T09:18:25.823233333Z",
            "change_time": "2026-11-21T09:18:25.831759666Z",
            "creation_time": "2026-11-21T09:18:25.823233333Z",
            "file_mode": 0o100644,
            "group_identifier": 99,
            "inode_number": 36,
            "metadata": {"version": "20261030"},
            "modification_time": "2026-11-21T09:18:25.823233333Z",
            "name": "xattr1",
            "number_of_links": 1,
            "size": 0,
            "user_identifier": 99,
        }
        self.assertEqual(result, expected_result)

    def test_parse_with_optional_attributes(self):
        """Tests the parse function with path, added time, device, and symlink."""
        output = (
            "fsapfsinfo 20261030\n"
            "\n"
            "File entry:\n"
            "\tPath\t\t\t: /forward:slash\n"
            "\tIdentifier\t\t: 30\n"
            "\tName\t\t\t: file_symboliclink2\n"
            "\tSize\t\t\t: 0\n"
            "\tCreation time\t\t: 2026-08-04T11:09:25.292907234Z\n"
            "\tModification time\t: 2026-08-04T11:09:25.292907234Z\n"
            "\tInode change time\t: 2026-08-04T11:09:25.292907234Z\n"
            "\tAccess time\t\t: Not set (0)\n"
            "\tAdded time\t\t: 2026-08-04T11:09:25.292907234Z\n"
            "\tNumber of links\t\t: 1\n"
            "\tOwner identifier\t: 99\n"
            "\tGroup identifier\t: 99\n"
            "\tFile mode\t\t: lrwxr-xr-x (0120755)\n"
            "\tDevice number\t\t: 24,57\n"
            "\tSymbolic link target\t: /Volumes/apfs_test/forward:slash\n"
            "\tExtended attributes:\n"
            "\t\tAttribute: 1\t: com.apple.fs.symlink\n"
        )
        file_object = io.StringIO(output)
        result = fsapfsinfo.FsApfsInfoOutputParser().parse(file_object)

        expected_result = {
            "access_time": None,
            "added_time": "2026-08-04T11:09:25.292907234Z",
            "change_time": "2026-08-04T11:09:25.292907234Z",
            "creation_time": "2026-08-04T11:09:25.292907234Z",
            "device_number": "24,57",
            "file_mode": 0o120755,
            "group_identifier": 99,
            "inode_number": 30,
            "metadata": {"version": "20261030"},
            "modification_time": "2026-08-04T11:09:25.292907234Z",
            "name": "file_symboliclink2",
            "number_of_links": 1,
            "path": "/forward:slash",
            "size": 0,
            "symbolic_link_target": "/Volumes/apfs_test/forward:slash",
            "user_identifier": 99,
        }
        self.assertEqual(result, expected_result)

    def test_parse_errors(self):
        """Tests the parse function with unsupported inputs."""
        parser = fsapfsinfo.FsApfsInfoOutputParser()

        with self.assertRaises(RuntimeError):
            parser.parse(io.StringIO(""))

        with self.assertRaises(RuntimeError):
            parser.parse(io.StringIO("bogus\n\nFile entry:\n"))

        with self.assertRaises(RuntimeError):
            parser.parse(io.StringIO("fsapfsinfo 20261030\n\nContainer information:\n"))

        with self.assertRaises(RuntimeError):
            parser.parse(
                io.StringIO("fsapfsinfo 20261030\n\nFile entry:\n\tUnknown\t: 1\n")
            )


if __name__ == "__main__":
    unittest.main()
