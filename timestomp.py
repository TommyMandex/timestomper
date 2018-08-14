#!/usr/bin/python

from __future__ import print_function
import re
import csv
import sys
import logging
import os.path
from datetime import datetime

_version_ = '1.0'

import formats as fmts
log = logging.getLogger('timestomper')

class NoMatchError(Exception):
  pass
class MatchIndexError(Exception):
  pass
class ReplaceError(Exception):
  pass
class FormatError(Exception):
  pass
class MissingYear(Exception):
  pass


def loadf(inFile):

  if inFile == '-':
    line_no = 0
    for line in sys.stdin:
      line_no += 1
      yield line_no, line

  else:
    with open(inFile) as fp:
      for line_no, line in enumerate(fp):
        yield line_no, line


class writef(object):

  def __init__(self, outFile='-'):
    super(writef, self).__init__()

    self.outFile = outFile

    if outFile == '-':
      log.debug('Opening "stdout"')
      self.outFile = sys.stdout
    else:
      log.debug('Opening for write: "{}"'.format(self.outFile))
      self.outFile = open(outFile, mode='wb', buffering=1)

  def get_file_obj(self):
    return self

  def write(self, line):

    line_no, line = line

    log.debug('Writing line [{}] to "{}" | {}'.format(line_no, ('-' if type(self.outFile) == str else self.outFile.name), [line]))
    print(line, end='') if type(self.outFile) == str else self.outFile.write(line)


  def close(self):
    log.debug('Closing: "{}"'.format('-' if type(self.outFile) == str else self.outFile.name))


def time2re(fmt_string, regex=True):
  mappings = {
    'a': '(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)',
    'A': '(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)',
    'w': '[0-6]',
    'd': '[0-3][0-9]',
    '-d': '[0-9]{1,2}',
    'b': '(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
    'B': '(?:January|February|March|April|May|June|July|August|September|October|November|December)',
    'm': '(0[1-9]|1[012])',
    '-m': '[1-12]{1,2}',
    'y': '[0-9]{2}',    ## Modded
    'Y': '[0-9]{4}',    ## Modded
    'H': '[0-2][0-9]',
    '-H': '[0-9]{1,2}',
    'I': '[0-1][0-9]',
    '-I': '[0-9]{1,2}',
    'p': '[AP]M',
    'M': '[0-5][0-9]',   ## Modded
    '-M': '[0-59]{1,2}',  ## Modded
    'S': '[0-5][0-9]',
    '-S': '[0-9]{1,2}',
    'f': '[0-9]{6}',
    'z': '(?:\+|-){0,1}(?:[0-1][0-9][0-5][0-9]){0,1}',
    'Z': '[A-Z]{2,5}',
    'j': '[0-3][0-9]{2}',
    '-j': '[0-9]{1,3}',
    'U': '[0-5][0-9]',
    'W': '[0-5][0-9]',
    '%': '%',
  }

  regex_safe = ['{', '}', '[', ']', '(', ')', '+', '.', '?', '|', '$', '^', '\\']

  def enumerate_fmt_string(fmt_string):
    for i in fmt_string:
      yield i

  final_re = []
  chars = enumerate_fmt_string(fmt_string)
  for c in chars:
    s = ''
    if c == '%':
      s = next(chars)
      if s == '-':
        s += next(chars)
      final_re.append(mappings[s])
      continue
    final_re.append('\\' + c if c in regex_safe else c)

  return (''.join(final_re)) if regex else ''.join(final_re)

def parse_cut(cut):

  if '-' in cut:
      start, end = cut.split('-')

      start = int(start) if start is not '' else 0
      end = int(end) if end is not '' else None

  else:
      start = 0
      end = int(cut)

  return start, end


def match(line, searches, line_no=None, index=None, cut=False, ignore=False, include=True):

  if cut:
    start, end = cut
    end = len(line) if end is None else end
  else:
    start = 0
    end = len(line)

  # # For each of the search types get matches
  matches = []
  for s in searches:

    regex = re.compile(s['regex'])
    strptime = s['strptime']

    matches += list((strptime, match) for match in regex.finditer(line, start, end))


  # # Reorder the matches otherwise index is going to be wrong
  # # There is no guarantee that the order we found the matches in are in order
  order = []
  for m in matches:
    strptime, match = m

    order.append(match.start())

  matches = [x for _,x in sorted(zip(order, matches))]

  # # Only return the correct match if index is set
  if type(index) == int:
    try:
       return [matches[index]]
    except:
      if (ignore or include):
        return
      else:
        raise MatchIndexError('Index does not exist: [{}] "{}"'.format(line_no, [line]))

  # # No matches
  elif len(matches) == 0:
    if (ignore or include):
      return
    else:
      raise NoMatchError('No matches: [{}] "{}"'.format(line_no, [line]))

  # # Only one match - OK
  elif len(matches) == 1:
    return matches

  # # index not defined so return all
  else:
    return matches

def replace(line, strftime, strptime, matchobj, line_no=None, ignore=False, offset=False, year=False, highlight=False):

  # # If given an offset, it is presumed the start and end values will need adjusting
  start, end = matchobj.start(), matchobj.end()
  if offset:
    start += offset
    end += offset

  old_date = line[start:end]

  # # Try and parse the old date to datetime - if it fails make sure we have ignore
  try:
    new_date = datetime.strptime(old_date, strptime)
  except ValueError as e:
    if not ignore:
      raise FormatError(e)
    else:
      return

  # # Some timestamps dont include a year
  if new_date.year == 1900:
    if ignore and not year:
      new_date.year = datetime.now().year
    elif not year:
      raise MissingYear(('Year not found in date, define with --year, or --ignore: [{}] "{}"'.format(line_no, [line])))
    else:
      new_date = new_date.replace(year=year)

  # # Get the new timestamp as a string using args.replace value
  new_date_str = new_date.strftime(strftime)

  # # Construct new line, highlight selections if asked
  if highlight:
    new_line = '{}\033[1;41m{}\033[0m{}'.format(line[:start], new_date_str, line[end:])
  else:
    new_line = '{}{}{}'.format(line[:start], new_date_str, line[end:])

  return new_line



if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser()

  parser.add_argument('--formats', action='store_true', help='Print the preloaded search formats')

  parser.add_argument('-i', '--infile', type=str, default='-', nargs='+', metavar='file.txt', help='File to parse. - is stdin')
  parser.add_argument('-o', '--outfile', type=str, default='-', metavar='file.txt', help='Output changed lines to this file. Without or -, results are printed to stdout')

  parser.add_argument('-s', '--search', type=str, metavar='{} OR "%Y-%m-%d %H:%M"'.format(', '.join(fmts.searches.keys()[:3])), help='Type of date/time strftime format that will be found in the file - you can get a list of available searches using: {} --formats'.format(sys.argv[0]))
  parser.add_argument('-r', '--replace', type=str, default='default', metavar='"%Y-%m-%d %H:%M"', help='Translate the found date/time to this strptime format - you can get a list of available formats using: {} formats --search'.format(sys.argv[0]))
  parser.add_argument('-y', '--year', type=int, default=False, metavar='1997', help='Some dates dont contain the year. Set those dates with this flag')

  parser.add_argument('-c', '--cut', type=str, metavar='#-#', help='Start and end position in lines to look for timestamps - same as Linux cut syntax (10-15, -10, 10- etc.) cut operation is performed before index evaluation')
  parser.add_argument('--index', type=int, default=None, metavar='#', help='Preferred timestamp to convert should there be more than one match. If there is more than one match and index is not specified, all matches on a line are replaced')

  parser.add_argument('--include', action='store_true', help='Include non-matching lines with output - helps with free-form text files. If used with --ignore, --ignore is, ignored :)')
  parser.add_argument('--ignore', action='store_true', help='Ignore non-critical errors. If --include is not specified, lines which would normal generate an error are ommited from output')

  parser.add_argument('--highlight', action='store_true', help='Highlight the text being changed')
  parser.add_argument('-v', '--verbose', action='store_true', help='Print debug information to stderr')

  args = parser.parse_args()


  if args.verbose:
    logging.basicConfig(stream=sys.stderr, format='Verbose | %(levelname)s | %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(stream=sys.stderr, format='*** %(levelname)s | %(message)s', level=logging.CRITICAL)

  log = logging.getLogger('timestomper')

  # # Show the formats
  if args.formats:
    print('\nSearch formats:')

    for name, types in fmts.searches.items():
      print('{:>17}:'.format(name))

      for t in types:
        regex = t['regex']
        strptime = t['strptime']

        print('{0:>15}Regex: "{1}"\n{0:>15}strptime: "{2}"\n'.format(' ', regex, strptime))

    print('Output formats:')
    for k,v in fmts.out_strftime.items():
      print('{:>15}: "{}"'.format(k,v))


    print("""
Python's strftime directives:

Code    Meaning                                                             Example
%a      Weekday as locale's abbreviated name.                               Mon
%A      Weekday as locale's full name.                                      Monday
%w      Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.   1
%d      Day of the month as a zero-padded decimal number.                   30
%-d     Day of the month as a decimal number. (Platform specific)           30
%b      Month as locale's abbreviated name.                                 Sep
%B      Month as locale's full name.                                        September
%m      Month as a zero-padded decimal number.                              09
%-m     Month as a decimal number. (Platform specific)                      9
%y      Year without century as a zero-padded decimal number.               13
%Y      Year with century as a decimal number.                              2013
%H      Hour (24-hour clock) as a zero-padded decimal number.               07
%-H     Hour (24-hour clock) as a decimal number. (Platform specific)       7
%I      Hour (12-hour clock) as a zero-padded decimal number.               07
%-I     Hour (12-hour clock) as a decimal number. (Platform specific)       7
%p      Locale's equivalent of either AM or PM.                             AM
%M      Minute as a zero-padded decimal number.                             06
%-M     Minute as a decimal number. (Platform specific)                     6
%S      Second as a zero-padded decimal number.                             05
%-S     Second as a decimal number. (Platform specific)                     5
%f      Microsecond as a decimal number, zero-padded on the left.           000000
%z      UTC offset in the form +HHMM or -HHMM (empty string if the the 
        object is naive).
%Z      Time zone name (empty string if the object is naive).
%j      Day of the year as a zero-padded decimal number.                    273
%-j     Day of the year as a decimal number. (Platform specific)            273
%U      Week number of the year (Sunday as the first day of the week) as
        a zero padded decimal number. All days in a new year preceding the
        first Sunday are considered to be in week 0.                        39
%W      Week number of the year (Monday as the first day of the week) as
        a decimal number. All days in a new year preceding the first Monday
        are considered to be in week 0.                                     39
%c      Locale's appropriate date and time representation.                  Mon Sep 30 07:06:05 2013
%x      Locale's appropriate date representation.                           09/30/13
%X      Locale's appropriate time representation.                           07:06:05
%%      A literal '%' character.                                            %
    """)

    exit(0)

  else:

    if not args.search:
        print('\n*** Required:\t[-s cli-golive, osx-ls, us-slash-no_secs OR "%Y-%m-%d %H:%M"]\n')
        parser.print_help()
        exit(0)

    # # Check replace format
    if args.replace in fmts.out_strftime:
      args.replace = fmts.out_strftime[args.replace]
      log.debug('Output date format "{}"'.format(args.replace))
    else:
      log.debug('Custom output date format "{}"'.format(args.replace))

    # # Check cut is sensible - check if the starting cut is before end
    if args.cut:
      args.cut = (parse_cut(args.cut))

      if args.cut[0] < args.cut[1]:
        log.critical('Error with --cut - start greater than end: {} < {}'.format(args.cut[0], args.cut[1]))
        exit(1)

    # # Check the file is valid
    for file in args.infile:
      if not file == '-' and not os.path.isfile(file):
        log.critical('Exiting, cannot find file: {}'.format(file))
        exit(1)

    write_file = writef(args.outfile)
    write_file = write_file.get_file_obj()

    # # Check the searches
    if args.search in fmts.searches:
      searches = fmts.searches[args.search]
    else:
      searches = [{'regex': time2re(args.search), 'strptime': args.search}]

    log.debug('Using the following search(s): {}'.format(searches))

    # # Main loop
    for file in args.infile:
      for line_no, line in loadf(file):

        matches = match(line_no=line_no, line=line, searches=searches, index=args.index, cut=args.cut, ignore=args.ignore, include=args.include)

        if matches:

          # # We need to calcualte the offset if multiple matches need to be replaced
          # # The new time format is probably not the same length as the old one
          new_line = line
          new_line_len = prev_line_len = len(new_line)

          for m in matches:

            # # An offset is needed as we change the length of the line with each replace
            offset = abs(prev_line_len - new_line_len)
            if new_line_len < prev_line_len:
              offset = offset * -1

            strptime, matchobj = m

            new_line = replace(line_no=line_no, line=new_line, strftime=args.replace, strptime=strptime, matchobj=matchobj, ignore=args.ignore, offset=offset, year=args.year, highlight=args.highlight)
            new_line_len = len(new_line)

          if new_line:
            write_file.write((line_no, new_line))
          else:
            if args.highlight:
              raise ReplaceError(('Highlight failed: [{}] "{}"'.format(line_no, [line])))
            else:
              raise ReplaceError(('Replace failed: [{}] "{}"'.format(line_no, [line])))


        # # This line didn't match, but we were asked to include non-matching
        elif args.include:
          log.debug('No match, but --include used | {}'.format([line]))
          write_file.write((line_no, line))

        # # The line didn't match, and we don't care about them
        elif args.ignore:
          log.debug('No match and --ignore used | {}'.format([line]))

          continue

    write_file.close()
