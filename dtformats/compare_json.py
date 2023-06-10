#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to compare Apple Unified Logging json files."""

import argparse
import difflib
import heapq
import json
import sys


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Compares Apple Unified Logging json files.'))

  argument_parser.add_argument(
      'first', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the first json file.')

  argument_parser.add_argument(
      'second', nargs='?', action='store', metavar='PATH',
      default=None, help='path of the second json file.')

  options = argument_parser.parse_args()

  if not options.first:
    print('First file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not options.second:
    print('Second file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  first_heap = []
  with open(options.first, encoding='utf8') as file_object:
    for log_entry in json.load(file_object):
      timestamp = log_entry.get('timestamp', None) or ''
      heapq.heappush(first_heap, (timestamp, json.dumps(log_entry)))

  try:
    _, first_log_entry = heapq.heappop(first_heap)
  except IndexError:
    first_log_entry = None

  first_sorted = []

  while first_log_entry:
    first_sorted.append(first_log_entry)

    try:
      _, first_log_entry = heapq.heappop(first_heap)
    except IndexError:
      first_log_entry = None

  del first_heap

  second_heap = []
  with open(options.second, encoding='utf8') as file_object:
    for log_entry in json.load(file_object):
      timestamp = log_entry.get('timestamp', None) or ''
      heapq.heappush(second_heap, (timestamp, json.dumps(log_entry)))

  try:
    _, second_log_entry = heapq.heappop(second_heap)
  except IndexError:
    second_log_entry = None

  second_sorted = []

  while second_log_entry:
    second_sorted.append(second_log_entry)

    try:
      _, second_log_entry = heapq.heappop(second_heap)
    except IndexError:
      second_log_entry = None

  del second_heap

  color_green = '\x1b[0;32m'
  color_red = '\x1b[0;31m'
  color_end = '\x1b[0m'

  matcher = difflib.SequenceMatcher(None, first_sorted, second_sorted)
  for (opcode, first_start, first_end, second_start,
       second_end) in matcher.get_opcodes():
    first_lines = first_sorted[first_start:first_end]
    second_lines = second_sorted[second_start:second_end]

    if opcode == 'insert':
      for line in second_lines:
        print(f'{color_green:s}+ {line:s}{color_end:s}')

    elif opcode == 'delete':
      for line in first_lines:
        print(f'{color_red:s}- {line:s}{color_end:s}')

    elif opcode == 'replace':
      for index in range(len(first_lines)):
        first_line = first_lines[index]
        second_line = second_lines[index]

        first_output = []
        second_output = []

        line_matcher = difflib.SequenceMatcher(
            None, first_line, second_line, autojunk=False)
        for line_opcode, a0, a1, b0, b1 in line_matcher.get_opcodes():
          if line_opcode == 'equal':
            text = first_line[a0:a1]
            first_output.append(text)
            second_output.append(text)

          elif opcode == 'insert':
            text = second_line[b0:b1]
            second_output.append(f'{color_green:s}{text:s}{color_end:s}')

          elif opcode == 'delete':
            text = first_line[a0:a1]
            first_output.append(f'{color_red:s}{text:s}{color_end:s}')

          elif opcode == 'replace':
            text = second_line[b0:b1]
            second_output.append(f'{color_green:s}{text:s}{color_end:s}')
            text = first_line[a0:a1]
            first_output.append(f'{color_red:s}{text:s}{color_end:s}')

        first_output = ''.join(first_output)
        second_output = ''.join(second_output)

        print(f'+ {second_output:s}')
        print(f'- {first_output:s}')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
