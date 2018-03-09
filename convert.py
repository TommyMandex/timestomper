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
load_parser.add_argument('--infile', type=str, required=True, nargs='+', help='File to parse')
load_parser.add_argument('-f', '--format', type=str, required=True, nargs='+', help='Type of formatting that will be found in the file')
load_parser.add_argument('-o', '--outformat', type=str, required=True, nargs='+', help='Translate the format to this date format - you can get a list of available formats using --formats')
load_parser.add_argument('--outfile', type=str, required=False, default=None, help='Output to the changed lines to this file')
load_parser.add_argument('--ignore', action='store_true', required=False, help='Ignore no matches - can be used with free text files - potentially dangerous')

load_parser = subparsers.add_parser('timesketch')

args = parser.parse_args()
method = sys.argv[1]


def load(inFile):

	if inFile != '-':

		with open(inFile) as fp:
			for line_no, line in enumerate(fp):
				yield (line_no, line)
	else:
		line_no = 0
		for line in sys.stdin:
			yield (line_no, line)
			line_no += 1



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

		if not len(args.format) == len(args.outformat):
			print('No same amount of input and output formats')


		for file in args.infile:
			for line in load(file):
				







	elif method == 'timesketch':
		print('Doing timesketch: Not yet implemented!')

	else:
		print('Unknown method: {}'.format(method))
