#!/usr/bin/env python3
"""Parses debugfs stat output.

To create debugfs stat output:
    TZ=UTC debugfs -R "stat <22>" ext2.raw
"""

import json
import sys

from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import IO


class DebugfsStatOutputParser:
    """Parses debugfs stat output."""

    SECTION_HEADERS = {
        "BLOCKS:": "blocks",
        "EXTENTS:": "extents",
        "Extended attributes:": "extended_attributes",
    }

    DEFAULT_ATTRIBUTE_NAMES = {
        "atime": "access_time",
        "blockcount": "number_of_blocks",
        "crtime": "creation_time",
        "ctime": "change_time",
        "file acl": "file_acl",
        "flags": "flags",
        "generation": "nfs_generation_number",
        "group": "group_identifier",
        "inode": "inode_number",
        "links": "number_of_links",
        "mtime": "modification_time",
        "project": "project_identifier",
        "size": "size",
        "user": "user_identifier",
        "version": "version",
    }

    DECIMAL_ATTRIBUTES = frozenset(
        [
            "file_acl",
            "group_identifier",
            "inode_number",
            "nfs_generation_number",
            "number_of_blocks",
            "number_of_links",
            "project_identifier",
            "size",
            "user_identifier",
        ]
    )

    HEXADECIMAL_ATTRIBUTES = frozenset(["checksum", "flags"])

    # TODO: determine how debugfs represents a socket.
    FILE_TYPES = {
        "block": 0x6000,
        "character": 0x2000,
        "directory": 0x4000,
        "FIFO": 0x1000,
        "regular": 0x8000,
        "symlink": 0xA000,
    }

    def _parse_date_time(self, value: str) -> str:
        """Converts a debugfs date and time value to ISO 8601.

        Args:
          value (str): date and time value such as 'Wed Aug 19 18:48:01 2020'

        Returns:
          str: ISO 8601 formatted date and time value.

        Raises:
          RuntimeError: if the date and time value is not supported.
        """
        if " -- " not in value:
            raise RuntimeError(f"Unsupported date and time: {line:s}")

        values = value.strip().split(" -- ")

        timestamp_string = values[0].strip()
        date_time_string = values[1].strip()

        # TODO: check weekday date_time_string[0:3]
        try:
            date_time = datetime.strptime(date_time_string[4:], "%b %d %H:%M:%S %Y")
        except ValueError as exception:
            raise RuntimeError(
                f"Unable to parse date and time: {date_time_string:s}"
            ) from exception

        nanoseconds = None
        if ":" in timestamp_string:
            _, _, extra_precision = timestamp_string.rpartition(":")
            try:
                extra_precision = int(extra_precision, 16)
            except ValueError as exception:
                raise RuntimeError(
                    f"Unable to parse extra precision: {extra_precision:s}"
                ) from exception

            nanoseconds = (0x100000000 * (extra_precision & 0x3)) + (
                extra_precision >> 2
            )
            seconds, nanoseconds = divmod(nanoseconds, 1000000000)
            date_time += timedelta(seconds=seconds)

        iso8610_string = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        if nanoseconds is not None:
            iso8610_string = f"{iso8610_string:s}.{nanoseconds:09d}"

        return f"{iso8610_string:s}Z"

    def _parse_decimal(self, value: str) -> str:
        """Converts a string of a decimal value into an integer.

        Args:
          value (str): decimal value such as '1000'

        Returns:
          int: integer value.

        Raises:
          RuntimeError: if the decimal value is not supported.
        """
        try:
            integer = int(value, 10)
        except ValueError as exception:
            raise RuntimeError("Unable to parse decimal: {value:s}") from exception

        return integer

    def _parse_file_mode(self, file_type: str, permissions: str) -> int:
        """Converts a file mode string to a numeric representation.

        Args:
          file_type (str): file type, such as 'directory'.
          permissions (str): octal representation of permissions, such as '0644'.

        Returns:
          int: numeric representation of the file mode.
        """
        try:
            integer = int(permissions, 8)
        except ValueError as exception:
            raise RuntimeError(
                "Unable to parse permissions: {permissions:s}"
            ) from exception

        try:
            integer += self.FILE_TYPES.get(file_type)
        except TypeError as exception:
            raise RuntimeError("Unsupported file type: {file_type:s}") from exception

        return integer

    def _parse_hexadecimal(self, value: str) -> str:
        """Converts a string of a hexadecimal value into an integer.

        Args:
          value (str): hexadecimal value such as '0xeadbb557'

        Returns:
          int: integer value.

        Raises:
          RuntimeError: if the hexadecimal value is not supported.
        """
        try:
            integer = int(value, 16)
        except ValueError as exception:
            raise RuntimeError("Unable to parse hexadecimal: {value:s}") from exception

        return integer

    def _parse_section_default(self, line: str, result: Dict[str, str]):
        """Parses a line of the default section.

        Args:
          line (str): line in the section.
          result (dict): resulting attributes.

        Raises:
          RuntimeError: if the line is not supported.
        """
        file_type = "regular"

        if (
            line.startswith("atime:")
            or line.startswith("crtime:")
            or line.startswith("ctime:")
            or line.startswith("mtime:")
        ):
            key, _, value = line.partition(":")
            key = key.lower()

            attribute_name = self.DEFAULT_ATTRIBUTE_NAMES.get(key)
            result[attribute_name] = self._parse_date_time(value)

        elif line.startswith("Device major/minor number:"):
            # TODO: extract device major/minor number
            pass

        elif line.startswith("Fragment:"):
            if line != "Fragment:  Address: 0    Number: 0    Size: 0":
                raise RuntimeError(f"Unsupported fragment: {line:s}")

        elif line.startswith("Size of extra inode fields:"):
            pass

        else:
            while line:
                key, _, line = line.strip().partition(":")
                key = key.lower()

                value, _, line = line.strip().partition(" ")

                if key == "mode":
                    result["file_mode"] = self._parse_file_mode(
                        file_type, value.strip()
                    )
                elif key == "type":
                    file_type = value.strip()

                    if line.startswith("special"):
                        line = line[7:]

                else:
                    attribute_name = self.DEFAULT_ATTRIBUTE_NAMES.get(key)
                    if not attribute_name:
                        raise RuntimeError(f"Unsupported key: {key:s}")

                    attribute_value = value.strip()
                    if attribute_name in self.DECIMAL_ATTRIBUTES:
                        attribute_value = self._parse_decimal(attribute_value)
                    elif attribute_name in self.HEXADECIMAL_ATTRIBUTES:
                        attribute_value = self._parse_hexadecimal(attribute_value)

                    result[attribute_name] = attribute_value

    def parse(self, file_object: IO):
        """Parses debugfs stat output.

        Args:
          file_object (file): file-like object containing the debugfs stat output.

        Returns:
          dict[str, object]: values parsed from the debugfs stat output.

        Raises:
          RuntimeError: if the debugfs stat output is not supported.
        """
        lines = file_object.readlines()
        if not lines:
            raise RuntimeError("Missing debugfs stat output")

        result = {}
        section = "default"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line in self.SECTION_HEADERS:
                section = self.SECTION_HEADERS.get(line)

            elif line.startswith("Inode checksum:"):
                result["checksum"] = line[15:].strip()

            elif section == "blocks":
                # TODO: convert block numbers into ranges
                pass

            elif section == "default":
                if line.startswith("debugfs "):
                    # TODO: parser header
                    pass
                else:
                    self._parse_section_default(line, result)

            elif section == "extended_attributes":
                # TODO: parse extended attributes.
                pass

            elif section == "extents":
                # TODO: convert extents into ranges
                pass

        return result


if __name__ == "__main__":
    parser = DebugfsStatOutputParser()
    result_dict = parser.parse(sys.stdin)
    json_string = json.dumps(result_dict, indent=2)
    print(json_string)
