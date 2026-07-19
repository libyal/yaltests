"""Tests for the libfsfat fsfatinfo stat (-E or -F) output parser."""

import unittest

from libfsfat import fsfatinfo

from tests import test_lib


class FsFatInfoOutputParserTest(test_lib.BaseTestCase):
    """Tests for the libfsfat fsfatinfo stat output parser."""

    # pylint: disable=protected-access

    def test_parse(self):
        """Tests the parse function with fsfatinfo stat output."""
        test_file = self._get_test_file_path(
            ["mkfs.fat-4.2", "fsfatinfo.fat12.0x00006260.txt"],
        )
        self._skip_if_path_not_exists(test_file)

        with open(test_file, encoding="utf-8") as file_object:
            result = fsfatinfo.FsFatInfoOutputParser().parse(file_object)

        expected_result = {
            "access_time": "2026-08-19T00:00:00",
            "creation_time": "2026-08-19T04:49:36",
            "file_attribute_flags": 32,
            "identifier": 25184,
            "metadata": {"version": "20260717"},
            "modification_time": "2026-08-19T04:49:36",
            "name": "testfile1",
            "size": 8,
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
