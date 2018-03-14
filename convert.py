#!/usr/bin/python

# Change to module/class?
# Example values in --help

from __future__ import print_function

import argparse, re, sys, logging
from datetime import datetime

import formats as fmts

class NoMatchError(Exception):
	pass
class MatchIndexError(Exception):
	pass
class ReplaceError(Exception):
	pass
class FormatError(Exception):
	pass


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', help='Print debug information to stderr')

subparsers = parser.add_subparsers(help='')

enquire_parser = subparsers.add_parser('enquire')
enquire_parser.add_argument('-s', '--search', action='store_true', required=True, help='Show available search and replace strings')

fileout_parser = subparsers.add_parser('fileout')
fileout_parser.add_argument('--infile', type=str, required=True, nargs='+', help='File to parse. - is stdin')
fileout_parser.add_argument('--outfile', type=str, required=False, default='-', help='Output changed lines to this file. If not included or -, results are printed to stdout')
fileout_parser.add_argument('-s', '--search', type=str, required=True, help='Type of date/time format that will be found in the file - you can get a list of available searches using: {} enquire --search'.format(sys.argv[0]))
fileout_parser.add_argument('-r', '--replace', type=str, default='default', help='Translate the found date/time to this format - you can get a list of available formats using: {} enquire --search'.format(sys.argv[0]))
fileout_parser.add_argument('-c', '--cut', type=int, required=False, nargs=2, help='Start and end position in lines to look for timestamps - cut operation is performed before index evaluation')
fileout_parser.add_argument('-i', '--index', type=int, default=None, help='Preferred timestamp to convert should there be more than one match. If there is more than one match and index is not specified, all matches on a line are replaced')
fileout_parser.add_argument('--include', action='store_true', required=False, help='Include non-matching lines with output - helps with free-form text files. If used with --ignore, --ignore is, ignored :)')
fileout_parser.add_argument('--ignore', action='store_true', required=False, help='Ignore non-critical errors. If --include is not specified, lines which would normal generate an error are ommited from output')

# timesketch_parser = subparsers.add_parser('timesketch')

args = parser.parse_args()



if args.verbose:
	method = sys.argv[2]
	logging.basicConfig(stream=sys.stderr, format='Verbose | %(levelname)s | %(message)s', level=logging.DEBUG)
else:
	method = sys.argv[1]
	logging.basicConfig(stream=sys.stderr, format='Verbose | %(levelname)s | %(message)s', level=logging.CRITICAL)

log = logging.getLogger('timestomper')


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

	def __init__(self, outFile):
		super(writef, self).__init__()
		self.outFile = outFile

		if outFile == '-':
			log.debug('Opening "stdout"')
		else:
			log.debug('Opening for write: "{}"'.format(self.outFile))
			self.outFile = open(outFile, mode='wb', buffering=1)


	def write(self, line):

		line_no, line = line

		log.debug('Writing line [{}] to "{}" | {}'.format(line_no, ('-' if type(self.outFile) == str else self.outFile.name), [line]))
		print(line, end='') if type(self.outFile) == str else self.outFile.write(line)	


	def close(self):
		log.debug('Closing: "{}"'.format('-' if type(self.outFile) == str else self.outFile.name))



def match(line_no, line, searches, index, cut, ignore, include):

	if cut:
		start, end = cut
	else:
		start = 0
		end = len(line)

	# For each of the search types get matches
	matches = []
	for s in searches:

		regex = re.compile(s['regex'])
		strftime = s['strftime']

		matches += list((strftime, match) for match in regex.finditer(line, start, end))


	# Reorder the matches otherwise index is wrong
	# There is no guarantee that the order we found the matches in are in order
	order = []
	for m in matches:
		strftime, match = m

		order.append(match.start())

	matches = [x for _,x in sorted(zip(order,matches))]

	# Only return the correct match if index is set
	if type(index) == int:
		try:
			 return [matches[index]]
		except:
			if (ignore or include):
				return
			else:
				raise MatchIndexError('Index does not exist: [{}] "{}"'.format(line_no, [line]))

	# No matches
	elif len(matches) == 0:
		if (ignore or include):
			return
		else:
			raise NoMatchError('No matches: [{}] "{}"'.format(line_no, [line]))

	# Only one match - OK
	elif len(matches) == 1:
		return matches

	# index not defined so return all
	else:
		return matches


def replace(line_no, line, replace, strftime, matchobj, ignore, offset=False):

	start, end = matchobj.start(), matchobj.end()

	if offset:
		start += offset
		end += offset

	old_date = line[start:end]

	# Try and parse the line
	try:
		new_date = datetime.strptime(old_date, strftime)
	except ValueError as e:
		if not ignore:
			raise FormatError(e)
		else:
			return

	# Some timestamps dont include a year, so add the current
	if new_date.year == 1900:
		new_date = new_date.replace(year=datetime.now().year)

	# Get the new timestamp as a string using args.replace 
	new_date_str = new_date.strftime(replace)

	# Construct new line
	new_line = line[:start] + new_date_str + line[end:]

	return new_line


if __name__ == '__main__':

	if method == 'enquire':
		if args.search:
			
			print('Search formats:')

			for name, types in fmts.searches.items():
				print('{:>17}:'.format(name))

				for t in types:
					regex = t['regex']
					strftime = t['strftime']

					print('{0:>15}Regex: "{1}"\n{0:>15}strftime: {2}\n'.format(' ', regex, strftime))

			print('Output formats:')
			for k,v in fmts.out_strftime.items():
				print('{:>15}: {}'.format(k,v))

			exit(0)

	elif method == 'fileout':

		# Check searches are valid and assign
		try:
			searches = fmts.searches[args.search]
			log.debug('Using \'{}\' search pattern'.format(args.search))
		except KeyError as e:
			log.critical('No such search. Use \'{} enquire --search\' to find valid searches: "{}"'.format(sys.argv[0], args.search))
			exit(1)

		# Check replace format
		if args.replace in fmts.out_strftime:
			args.replace = fmts.out_strftime[args.replace]
			log.debug('Output date format "{}"'.format(args.replace))
		else:
			log.debug('Custom output date format "{}"'.format(args.replace))

		# Check cut is sensible - check if the starting cut is before end
		if args.cut and (not args.cut[0] < args.cut[1]):
			log.critical('Error with --cut - start greater than end: {} < {}'.format(args.cut[0], args.cut[1]))
			exit(1)

		write_file = writef(args.outfile)

		for file in args.infile:
			for line_no, line in loadf(file):

				matches = match(line_no=line_no, line=line, searches=searches, index=args.index, cut=args.cut, ignore=args.ignore, include=args.include)

				# We really ought to sort the matches by start/end position and also sort them
				# This is so we can be safe going into the next section

				if matches:

					# We need to calcualte the offset if multiple matches need to be replaced
					# The new time format is probably not the same length as the old one
					new_line = line
					new_line_len = prev_line_len = len(new_line)

					for m in matches:

						# An offset is needed as we change the length of the line
						offset = abs(prev_line_len - new_line_len)
						if new_line_len < prev_line_len:
							offset = offset * -1

						strftime, matchobj = m

						new_line = replace(line_no=line_no, line=new_line, replace=args.replace, strftime=strftime, matchobj=matchobj, ignore=args.ignore, offset=offset)
						new_line_len = len(new_line)


					if new_line:
						write_file.write((line_no, new_line))
					else:
						raise ReplaceError(('Replace failed: [{}] "{}"'.format(line_no, [line])))


				# This line didn't match, but we were asked to include non-matching
				elif args.include:
					# log.debug('No match, but included | {}'.format([line]))
					write_file.write((line_no, line))

				# The line didn't match, and we don't care about them
				elif args.ignore:
					continue


		write_file.close()

