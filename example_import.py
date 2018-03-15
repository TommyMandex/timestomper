#!/usr/bin/python

# Main imports
from timestomp import loadf, writef, match, replace

# Required imports
import logging, sys

# Set logging verbosity - verbose messages are printed at debug level
logging.basicConfig(stream=sys.stderr, format='Verbose | %(levelname)s | %(message)s', level=logging.DEBUG)

# Print output to stdout. Change for filename to write to file
f = writef('-')

# loadf is an iterator for lines from file/stdin ('-')
# This maybe changed for any line input (as below)

# text = """
# 14/07/2009  01:14             9,728 winhlp32.exe
# 09/11/2015  16:41    <DIR>          winsxs
# 10/06/2009  20:52           316,640 WMSysPr9.prx
# 14/07/2009  01:39            10,240 write.exe
#               27 File(s)      5,344,622 bytes
#               54 Dir(s)  53,496,602,624 bytes free
# """.splitlines()
# lines = zip(range(0,len(text)), text)

# for line_no, line in lines:
for line_no, line in loadf('./examples/free-win7-dir-uk.txt'):

	# Returns a list of match objects given the regex and strptime
	searches = [ {
		'regex': '(\\d{2}\\/\\d{2}\\/\\d{4}\\s\\s\\d{2}\\:\\d{2})',
		'strptime': '%d/%m/%Y  %H:%M'
	}]
	matches = match(line, searches, line_no=line_no, index=None, cut=False, ignore=True, include=True)

	# For this example just take the first one
	if matches:
		strptime, m = matches[0]

		# Replace the matches given the strftime format
		strftime = '%s'
		line = replace(line_no=line_no, line=line, strftime=strftime, strptime=strptime, matchobj=m, ignore=True)

		# Reward!!
	print([line_no, line])


# Finally, close the output file
f.close()
