#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to export file content data using dfVFS and pyfsntfs."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import stat
import sys

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.resolver import resolver

import pyfsntfs


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Exports file content data from a NTFS file system within '
      'a storage media image.'))

  argument_parser.add_argument(
      '--offset', dest='offset', action='store', type=int, default=None,
      help='the NTFS volume offset, in bytes')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='SOURCE', default=None,
      help='the storage media image.')

  argument_parser.add_argument(
      'mft_entry', nargs='?', action='store', metavar='MFT_ENTRY', type=int,
      default=None, help='the MFT entry index to export.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not options.mft_entry:
    print('MFT entry value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  statinfo = os.stat(options.source)

  range_offset = options.offset
  range_size = statinfo.st_size - range_offset

  os_path_spec = factory.Factory.NewPathSpec(
      definitions.TYPE_INDICATOR_OS, location=options.source)
  data_range_path_spec = factory.Factory.NewPathSpec(
      definitions.TYPE_INDICATOR_DATA_RANGE, range_offset=range_offset,
      range_size=range_size, parent=os_path_spec)

  file_object = resolver.Resolver.OpenFileObject(data_range_path_spec)

  fsntfs_volume = pyfsntfs.volume()
  fsntfs_volume.open_file_object(file_object)

  fsntfs_file_entry = fsntfs_volume.get_file_entry(options.mft_entry)

  buffer_size = 16 * 1024 * 1024
  output_file = 'fsntfsexport-{0:d}.bin'.format(options.mft_entry)

  with open(output_file, 'wb') as output_file:
    data = fsntfs_file_entry.read(size=buffer_size)
    while data:
      output_file.write(data)
      data = fsntfs_file_entry.read(size=buffer_size)

  fsntfs_volume.close()
  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
