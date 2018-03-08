#!/usr/bin/python

import argparse, re
from datetime import datetime

from formats import in_formats, out_formats

class MatchError(Exception):
	def __init__(self, message):
		self.message = message
class FormatError(Exception):
	def __init__(self, message):
		self.message = message


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='')

enquire_parser = subparsers.add_parser('enquire')
enquire_parser.add_argument('-f', '--formats', action='store_true', required=True, help='Show available formats')

load_parser = subparsers.add_parser('load')
load_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose - print lines being parsed')
load_parser.add_argument('--infile', type=str, required=True, help='File to parse')
load_parser.add_argument('-f', '--format', type=str, required=True, help='Type of formatting that will be found in the file')
load_parser.add_argument('-o', '--outformat', type=str, required=True, help='Translate the format to this date format - you can get a list of available formats using --formats')
load_parser.add_argument('--outfile', type=str, required=False, default=None, help='Output to the changed lines to this file')
load_parser.add_argument('--ignore', action='store_true', required=False, help='Ignore no matches - can be used with free text files - potentially dangerous')

args = parser.parse_args()


def loadf(inFile, inFmt, outFmt, outFile, verbose=False, ignore=False):

	try:
		parser = in_formats[inFmt]
	except KeyError as e:
		raise FormatError('No such formatter: {}'.format(inFmt))
	
	with open(inFile) as f:
		lines = f.readlines()

	if outFile:
		if verbose:
			print('Opening file: {}'.format(outFile))
		write_file = open(outFile, 'w')

	line_no = 1
	for line in lines:

		line = line.rstrip()

		matches = []
		for i, candidate in parser.items():
			regex = candidate['regex']
			strftime = candidate['strftime']

			match = re.findall(regex, line)

			if len(match) > 1:
				raise MatchError('Too many matches in line: {}'.format(line_no))
			elif len(match) == 1:
				matches.append({'ts':match[0], 'strftime':strftime})

		# Test to see if there are multiple matches
		if len(matches) > 1:
			raise MatchError('Multiple matches for line: {}'.format(line_no))
		elif len(matches) < 1:

			if not ignore:
				line_no += 1
				continue
			elif ignore:
				if verbose:
					print('{:>5}: [{}] {}'.format(line_no, 'ignore', line))
				if outFile:
					write_file.write(new_line+'\n')
				line_no += 1
				continue				

			raise MatchError('No matches for line: {}'.format(line_no))

		# Format the times
		match = matches[0]
		ts_old = match['ts']

		try:
			ts_new = datetime.strptime(ts_old, match['strftime'])
		except ValueError as e:
			raise FormatError(e)

		# Some timestamps dont have the year if it is the current, so set to current
		if ts_new.year == 1900:
			ts_new = ts_new.replace(year=datetime.now().year)

		if outFmt in out_formats:
			ts_new = ts_new.strftime(out_formats[outFmt])
		else:
			ts_new = ts_new.strftime(outFmt)

		# Now to replace the timestamp
		new_line = line.replace(ts_old, ts_new)

		if verbose:
			print('{:>5}: [{}] > [{}] {}'.format(line_no, ts_old, ts_new, new_line))

		if outFile:
			write_file.write(new_line+'\n')

		line_no += 1

	if outFile:
		if verbose:
			print('Closing file: {}'.format(outFile))
		write_file.close()


def suggest(line):
	pass

if __name__ == '__main__':


	try:
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
	except AttributeError as e:
		pass

	loadf(inFile=args.infile, inFmt=args.format, outFmt=args.outformat, outFile=args.outfile, verbose=args.verbose, ignore=args.ignore)
