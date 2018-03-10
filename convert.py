#!/usr/bin/python

import argparse, re, sys, logging
from datetime import datetime

import formats as fmts


class MatchError(Exception):
	def __init__(self, message):
		self.message = message
		print(message)

class FormatError(Exception):
	def __init__(self, message):
		self.message = message
		print(message)


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose - print debug information')

subparsers = parser.add_subparsers(help='')

enquire_parser = subparsers.add_parser('enquire')
enquire_parser.add_argument('-s', '--search', action='store_true', required=True, help='Show available search types')

load_parser = subparsers.add_parser('load')
load_parser.add_argument('--infile', type=str, required=True, nargs='+', help='File to parse')
load_parser.add_argument('-s', '--search', type=str, required=True, help='Type of formatting that will be found in the file')
load_parser.add_argument('-i', '--index', type=int, default=0, help='Preferred timestamp to convert should there be more than one match')
load_parser.add_argument('-o', '--strftime', type=str, required=True, help='Translate the format to this date format - you can get a list of available formats using: enquire --search')
load_parser.add_argument('--outfile', type=str, required=False, default=None, help='Output to the changed lines to this file')
load_parser.add_argument('--printall', action='store_true', required=False, help='Keep lines with no matches (printall) - can be used with free text files - potentially dangerous')
load_parser.add_argument('--ignore', action='store_true', required=False, help='Ignore errors and continue parsing - only output matching lines')

load_parser = subparsers.add_parser('timesketch')

args = parser.parse_args()


if args.verbose:
	method = sys.argv[2]
	logging.basicConfig(stream=sys.stderr, format='%(message)s', level=logging.DEBUG)
else:
	method = sys.argv[1]
	logging.basicConfig(stream=sys.stderr, format='%(message)s', level=logging.CRITICAL)
log = logging.getLogger('timestomper')


def load(inFile):

	if inFile != '-':

		with open(inFile) as fp:
			for line_no, line in enumerate(fp):
				yield (line_no, line.rstrip())
	else:
		line_no = 0
		for line in sys.stdin:
			yield (line_no, line.rstrip())
			line_no += 1


def mod_ts(line, inFmt, outFmt, printall, ignore, index):

	line_no, line = line

	matches = []

	# Check informat are valid and assign
	try:
		fmt = fmts.searches[inFmt]
	except KeyError as e:
		raise FormatError('No such formatter: {}'.format(args.search))

	# Loop over the format types' candidates
	for i, candidate in fmt.items():

		regex = candidate['regex']
		strftime = candidate['strftime']

		match = re.findall(regex, line)

		# No matches
		if len(match) == 0:
			continue # We may get a match with another candidate

		# More than one match
		if len(match) > 1:
			matches.append({'ts':match[index], 'strftime':strftime})

		# Only one match - OK
		if len(match) == 1:
			matches.append({'ts':match[0], 'strftime':strftime})


	# No matches at all, for line
	if len(matches) < 1:

		if printall:
			return line
		elif ignore:
			return False
		else:
			raise MatchError('No matches for line: {}'.format(line_no))

	# If we have more than one match
	if len(matches) > 1:

		if not ignore:
			raise MatchError('Multiple matches for line: {}'.format(line_no))

	# If we have more than one match for the entire line, we use the first one
	if len(matches) == 1:

		# Format the times
		match = matches[0]
		ts_old = match['ts']

		try:
			ts_new = datetime.strptime(ts_old, match['strftime'])
		except ValueError as e:
			if printall:
				return line
			elif not ignore:
				raise FormatError(e)

		# Some timestamps dont have the year if it is the current, so set to current
		if ts_new.year == 1900:
			ts_new = ts_new.replace(year=datetime.now().year)

		if outFmt in fmts.out_strftime:
			ts_new = ts_new.strftime(fmts.out_strftime[outFmt])
		else:
			ts_new = ts_new.strftime(outFmt)

		# Now to replace the timestamp
		new_line = line.replace(ts_old, ts_new)

		log.debug('{:5}: [{}] > [{}] {}'.format(line_no, ts_old, ts_new, new_line))

		return new_line

def print_searches():

	print('Search formats:')
	for name, types in fmts.searches.items():
		print('{:>17}:'.format(name))

		for k,v in types.items():
			print('{0:>15}Regex: {1}\n{0:>15}strftime: {2}\n'.format(' ',v['regex'], v['strftime']))

	print('Output formats:')
	for k,v in fmts.out_strftime.items():
		print('{:>15}: {}'.format(k,v))


if __name__ == '__main__':

	if method == 'enquire':
		if args.formats:
			print_searches()
			exit(0)

	elif method == 'load':

		if args.outfile:
			log.debug('Opening file: {}'.format(args.outfile))
			write_file = open(args.outfile, 'w+')


		for file in args.infile:
			for line in load(file):

				new_line = mod_ts(line=line, inFmt=args.search, outFmt=args.strftime, printall=args.printall, ignore=args.ignore, index=args.index)

				if new_line:

					if args.outfile:
						write_file.write('{}\n'.format(new_line))
					if not args.outfile and not args.verbose:
						print(new_line)

				else:
					if args.verbose:
						line_no, line = line
						log.debug('{:5}: [ignore] {}'.format(line_no, line))



		if args.outfile:
			log.debug('Closing file: {}'.format(args.outfile))
			write_file.close()




	elif method == 'timesketch':
		print('Doing timesketch: Not yet implemented!')

	else:
		print('Unknown method: {}'.format(method))
