#!/usr/bin/python

import argparse, re, sys, logging
from datetime import datetime

import formats as fmts

class MatchError(Exception):
	def __init__(self, message):
		self.message = message
		log.critical(message)

class FormatError(Exception):
	def __init__(self, message):
		self.message = message
		log.critical(message)


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose - print debug information')

subparsers = parser.add_subparsers(help='')

enquire_parser = subparsers.add_parser('enquire')
enquire_parser.add_argument('-s', '--search', action='store_true', required=True, help='Show available search types')

load_parser = subparsers.add_parser('load')
load_parser.add_argument('--infile', type=str, required=True, nargs='+', help='File to parse. "-" is stdin (without ")')
load_parser.add_argument('--outfile', type=str, required=False, default='-', help='Output to the changed lines to this file. Without, results are printed to stdout')
load_parser.add_argument('-s', '--search', type=str, required=True, help='Type of formatting that will be found in the file')
load_parser.add_argument('-r', '--replace', type=str, required=True, help='Translate the format to this date format - you can get a list of available formats using: enquire --search')

load_parser.add_argument('-c', '--cut', type=int, required=False, nargs=2, help='Start and end position to look for timestamps - cut operation is performed before index evaluation')
load_parser.add_argument('-i', '--index', type=int, default=None, help='Preferred timestamp to convert should there be more than one match. If there is more than one match and index is not specified, all matches on a line replaced')

# Mutually exclusive
load_parser.add_argument('--include', action='store_true', required=False, help='Include non-matching lines with output - helps with free-form text files')
load_parser.add_argument('--ignore', action='store_true', required=False, help='Ignore non-critical errors')

load_parser = subparsers.add_parser('timesketch')

args = parser.parse_args()

if args.verbose:
	method = sys.argv[2]
	logging.basicConfig(stream=sys.stderr, format='Verbose | %(message)s', level=logging.DEBUG)
else:
	method = sys.argv[1]
	logging.basicConfig(stream=sys.stderr, format='*** ERROR | %(message)s', level=logging.CRITICAL)
log = logging.getLogger('timestomper')


def loadf(inFile):

	if inFile == '-':
		line_no = 0
		for line in sys.stdin:
			line_no += 1
			yield line_no, line.rstrip()

	else:
		with open(inFile) as fp:
			for line_no, line in enumerate(fp):
				yield line_no, line.rstrip()

class writef(object):
	"""docstring for writef"""
	def __init__(self, outFile):
		super(writef, self).__init__()
		self.outFile = outFile

		if outFile == '-':
			self.outFile = 'stdout'
		else:
			pass
		log.debug('Opening for write: "{}"'.format(self.outFile))


	def write(self, line):
		log.debug('Writing to: "{}": {}'.format(self.outFile, line))

	def close(self):
		log.debug('Closing: "{}"'.format(self.outFile))


# If there are no matches, return nothing
# If there is more hat one match, return the match with index, else, nothing
# If there is only one match, that's good :)
def match(line, line_no, regex, index, cut, ignore, include):

	if cut:
		start, end = cut
	else:
		start = 0
		end = len(line)

	# matches = list(regex.finditer(line, start, end))
	matches = list(regex.finditer(line, start, end))

	# See if we can use index value
	if type(index) == int:
		try:
			return [matches[index]]
		except:
			if not ignore and not include:
				raise MatchError('Index does not exist: {} "{}"'.format(line_no, line))
			else:
				return

	# No matches
	elif len(matches) == 0:
		return
	# Only one match - OK
	elif len(matches) == 1:
		return matches
	else:
		return matches


def replace(line, line_no, matches, strftimes):
	pass


if __name__ == '__main__':

	if method == 'enquire':
		if args.search:
			
			print('Search formats:')

			for name, types in fmts.searches.items():
				print('{:>17}:'.format(name))

				regex = fmts.searches[name]['regex']
				strftime = fmts.searches[name]['strftime']

				print('{0:>15}Regex: "{1}"\n{0:>15}strftime: {2}\n'.format(' ', regex, strftime))

			print('Output formats:')
			for k,v in fmts.out_strftime.items():
				print('{:>15}: {}'.format(k,v))

			exit(0)

	elif method == 'load':

		# Check searches are valid and assign
		try:
			searches = fmts.searches[args.search]
		except KeyError as e:
			log.critical('No such search: "{}" - use enquire --search to find valid searches'.format(args.search))
			exit(1)

		regex = re.compile(searches['regex'])
		strftimes = searches['strftime']

		write_file = writef(args.outfile)

		for file in args.infile:
			for line_no, line in loadf(file):

				print('*'*10)

				matches = match(line=line, line_no=line_no, regex=regex, index=args.index, cut=args.cut, ignore=args.ignore, include=args.include)

				if matches:

					# Now replace!!
					# replace(line_no, line, matches, strftimes)

					for m in matches:
						print(m.start(), m.end(), m.groups(), line)

				elif args.include:
					print(line)

				elif args.ignore:
					continue

				continue





		write_file.close()






