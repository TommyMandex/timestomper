#!/usr/bin/python

import argparse, re, sys
from datetime import datetime

from formats import in_formats, out_formats

class MatchError(Exception):
	def __init__(self, message):
		self.message = message
class FormatError(Exception):
	def __init__(self, message):
		self.message = message


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose - print lines being parsed')

subparsers = parser.add_subparsers(help='')

enquire_parser = subparsers.add_parser('enquire')
enquire_parser.add_argument('-f', '--formats', action='store_true', required=True, help='Show available formats')

load_parser = subparsers.add_parser('load')
load_parser.add_argument('--infile', type=str, required=True, help='File to parse')
load_parser.add_argument('-f', '--informat', type=str, required=True, nargs='+', help='Type of formatting that will be found in the file')
load_parser.add_argument('-o', '--outformat', type=str, required=True, help='Translate the format to this date format - you can get a list of available formats using --formats')
load_parser.add_argument('--outfile', type=str, required=False, default=None, help='Output to the changed lines to this file')
load_parser.add_argument('--printall', action='store_true', required=False, help='Ignore lines with no matches (printall) - can be used with free text files - potentially dangerous')
load_parser.add_argument('--ignore', action='store_true', required=False, help='Ignore errors and continue parsing - only output matching lines')

load_parser = subparsers.add_parser('timesketch')

args = parser.parse_args()
method = sys.argv[1]


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

def mod_ts(line, inFmt, outFmt, printall, ignore):

	line_no, line = line

	matches = []

	for i, candidate in inFmt.items():

		regex = candidate['regex']
		strftime = candidate['strftime']

		match = re.findall(regex, line)

		if len(match) > 1:
			if not ignore:
				raise MatchError('Too many matches in line: {}'.format(line_no))
			else:
				return False
		elif len(match) == 1:
			matches.append({'ts':match[0], 'strftime':strftime})

		# Test to see if there are multiple matches
		if len(matches) > 1:
			if not ignore:
				raise MatchError('Multiple matches for line: {}'.format(line_no))
			else:
				return False
		elif len(matches) < 1:

			if printall:
				return line
			else:
				if not ignore:
					raise MatchError('No matches for line: {}'.format(line_no))
				else:
					return False

		# Format the times
		match = matches[0]
		ts_old = match['ts']

		try:
			ts_new = datetime.strptime(ts_old, match['strftime'])
		except ValueError as e:
			if not ignore:
				raise FormatError(e)
			else:
				return False

		# Some timestamps dont have the year if it is the current, so set to current
		if ts_new.year == 1900:
			ts_new = ts_new.replace(year=datetime.now().year)

		if outFmt in out_formats:
			ts_new = ts_new.strftime(out_formats[outFmt])
		else:
			ts_new = ts_new.strftime(outFmt)

		# Now to replace the timestamp
		new_line = line.replace(ts_old, ts_new)

		return new_line


if __name__ == '__main__':

	if method == 'enquire':
		if args.formats:
			print('Search formats:')
			for name, types in in_formats.items():
				print('{:>15}'.format(name))

				for k,v in types.items():
					print('{0}Regex: {1}\n{0}strftime: {2}'.format(' '*10,v['regex'], v['strftime']))

			print('\nOutput formats:')
			for k,v in out_formats.items():
				print('{:>15}: {}'.format(k,v))

			exit(0)

	elif method == 'load':


		# Check informat are valid and assign
		try:
			args.informat = in_formats[args.informat]
		except KeyError as e:
			raise FormatError('No such formatter: {}'.format(args.informat))
			exit(0)

		if args.outfile:
			print('Opening file: {}'.format(args.outfile))
			write_file = open(args.outfile, 'w')


		for file in args.infile:
			for line in load(file):

				new_line = mod_ts(line, args.informat, args.outformat, printall=args.printall, ignore=args.ignore)
				if new_line:
					print(new_line)

		if args.outfile:
			print('Closing file: {}'.format(args.outfile))
			write_file.close()




	elif method == 'timesketch':
		print('Doing timesketch: Not yet implemented!')

	else:
		print('Unknown method: {}'.format(method))
