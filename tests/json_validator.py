"""Tests for the JSON normalized CLI tool output validator."""

import json
import io
import unittest

from scripts import json_validator

from tests import test_lib


class CliToolOutputJsonValidatorTest(test_lib.BaseTestCase):
    """Tests for the JSON normalized CLI tool output validator."""

    def test_compare_date_time_value(self):
        """Tests the _compare_date_time_value function."""
        rules = []
        validator = json_validator.CliToolOutputJsonValidator(rules)

        result = validator._compare_date_time_value("2026-05-20", "2026-05-20")
        self.assertEqual(result, {})

        result = validator._compare_date_time_value("2026-05-99", "2026-05-20")
        expected_result = {
            "issue": "unable to parse reference value",
            "output_value": "2026-05-20",
            "reference_value": "2026-05-99",
        }
        self.assertEqual(result, expected_result)

        result = validator._compare_date_time_value(
            "2026-05-20T99:44:28.893595285Z", "2026-05-20T17:44:28.893595285Z"
        )
        expected_result = {
            "issue": "unable to parse reference value",
            "output_value": "2026-05-20T17:44:28.893595285Z",
            "reference_value": "2026-05-20T99:44:28.893595285Z",
        }
        self.assertEqual(result, expected_result)

        result = validator._compare_date_time_value("2026-05-20", "2026-05-99")
        expected_result = {
            "issue": "unable to parse output value",
            "output_value": "2026-05-99",
            "reference_value": "2026-05-20",
        }
        self.assertEqual(result, expected_result)

        result = validator._compare_date_time_value(
            "2026-05-20T17:44:28.893595285Z", "2026-05-20T99:44:28.893595285Z"
        )
        expected_result = {
            "issue": "unable to parse output value",
            "output_value": "2026-05-20T99:44:28.893595285Z",
            "reference_value": "2026-05-20T17:44:28.893595285Z",
        }
        self.assertEqual(result, expected_result)

        result = validator._compare_date_time_value(
            "2026-05-20T17:44:28.893595285Z", "2026-05-21T17:44:28.893595285Z"
        )
        expected_result = {
            "issue": "value mismatch",
            "output_value": "2026-05-21T17:44:28.893595285Z",
            "reference_value": "2026-05-20T17:44:28.893595285Z",
        }
        self.assertEqual(result, expected_result)

        result = validator._compare_date_time_value(
            "2026-05-20T17:44:28.893595285Z", "2026-05-20T17:44:28Z"
        )
        expected_result = {
            "issue": "value granularity mismatch",
            "output_value": "2026-05-20T17:44:28Z",
            "reference_value": "2026-05-20T17:44:28.893595285Z",
        }
        self.assertEqual(result, expected_result)

    def test_convert_date_time_value(self):
        """Tests the _convert_date_time_value function."""
        rules = []
        validator = json_validator.CliToolOutputJsonValidator(rules)

        result = validator._convert_date_time_value(
            "2026-05-20T99:44:28.893595285", "seconds"
        )
        self.assertEqual(result, "2026-05-20T99:44:28")

        with self.assertRaises(RuntimeError):
            validator._convert_date_time_value(
                "2026-05-20T99:44:28.893595285Z", "bogus"
            )

    def test_is_date_time_value(self):
        """Tests the _is_date_time_value function."""
        rules = []
        validator = json_validator.CliToolOutputJsonValidator(rules)

        result = validator._is_date_time_value("2026-05-20")
        self.assertTrue(result)

        result = validator._is_date_time_value("2026-05-20T17:44:28Z")
        self.assertTrue(result)

        result = validator._is_date_time_value("2026-05-20T17:44:28.893595285Z")
        self.assertTrue(result)

        result = validator._is_date_time_value(20260520)
        self.assertFalse(result)

        result = validator._is_date_time_value("2026-05-20T17:44:28")
        self.assertFalse(result)

        result = validator._is_date_time_value("2026-05-20 17:44:28")
        self.assertFalse(result)

    def test_validate(self):
        """Tests the validate function."""
        test_file = self._get_test_file_path(
            ["mke2fs-1.47.0", "reference_ext2.23.json"]
        )
        self._skip_if_path_not_exists(test_file)

        rules = []
        validator = json_validator.CliToolOutputJsonValidator(rules)

        normalized_output = {
            "access_time": "2026-07-18T16:46:27.824277590Z",
            "change_time": "2026-07-18T16:46:27.825277596Z",
            "creation_time": "2026-07-18T16:46:27.824277590Z",
            "file_mode": 16877,
            "group_identifier": 0,
            "inode_number": 23,
            "modification_time": "2026-07-18T16:46:27.824277590Z",
            "number_of_links": 2,
            "size": 0,
            "user_identifier": 0,
        }
        file_object = io.BytesIO(json.dumps(normalized_output).encode("utf-8"))

        with open(test_file, encoding="utf-8") as reference_file_object:
            result = validator.validate(reference_file_object, file_object)

        expected_result = {
            "additional_attributes": [],
            "missing_attributes": [],
            "value_mismatches": {
                "size": {
                    "issue": "value mismatch",
                    "output_value": 0,
                    "reference_value": 4096,
                },
            },
        }
        self.assertEqual(result, expected_result)

        rules = [
            json_validator.ValidationRule.from_dict(
                {
                    "attributes": ["size"],
                    "condition": "file_mode & 0x4000 != 0",
                    "expected_value": 0,
                }
            )
        ]
        validator = json_validator.CliToolOutputJsonValidator(rules)

        file_object = io.BytesIO(json.dumps(normalized_output).encode("utf-8"))

        with open(test_file, encoding="utf-8") as reference_file_object:
            result = validator.validate(reference_file_object, file_object)

        expected_result = {
            "additional_attributes": [],
            "missing_attributes": [],
            "value_mismatches": {},
        }
        self.assertEqual(result, expected_result)

        test_file = self._get_test_file_path(
            ["mke2fs-1.47.0", "reference_ext2.22.json"]
        )
        self._skip_if_path_not_exists(test_file)

        rules = []
        validator = json_validator.CliToolOutputJsonValidator(rules)

        normalized_output = {
            "inode_number": 22,
            "allocated": True,
            "group": 0,
            "nfs_generation_number": 1803167177,
            "user_identifier": 0,
            "group_identifier": 0,
            "file_mode": 33188,
            "size": 0,
            "number_of_links": 1,
            "access_time": "2026-05-20T17:44:28Z",
            "modification_time": "2026-05-20T17:44:28Z",
            "change_time": "2026-05-20T17:44:28Z",
        }
        file_object = io.BytesIO(json.dumps(normalized_output).encode("utf-8"))

        with open(test_file, encoding="utf-8") as reference_file_object:
            result = validator.validate(reference_file_object, file_object)

        expected_result = {
            "additional_attributes": ["allocated", "group", "nfs_generation_number"],
            "missing_attributes": ["creation_time"],
            "value_mismatches": {
                "access_time": {
                    "issue": "value granularity mismatch",
                    "output_value": "2026-05-20T17:44:28Z",
                    "reference_value": "2026-05-20T17:44:28.893595285Z",
                },
                "change_time": {
                    "issue": "value granularity mismatch",
                    "output_value": "2026-05-20T17:44:28Z",
                    "reference_value": "2026-05-20T17:44:28.894595276Z",
                },
                "modification_time": {
                    "issue": "value granularity " "mismatch",
                    "output_value": "2026-05-20T17:44:28Z",
                    "reference_value": "2026-05-20T17:44:28.893595285Z",
                },
            },
        }
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
