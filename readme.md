# Timestomper

This app converts timestamps in free text files, line-by-line. It was made to combat the non-standardised date/time fields tools output.

Give it an input file (\-\-infile) and the format type of dates and/or times in that file, then an output format (in the style of a python datetime.strftime - examples can be found in the strftime.md file).

If it is a **completely** freeform input file, every line may not have a date/time present. If these fields want to still be retained, use the \-\-ignore argument.

To save the output to a new file, use the \-\-outfile argument.

## \-\-help

    usage: convert.py load [-h] [-v] --infile INFILE -f FORMAT -o OUTFORMAT
                           [--outfile OUTFILE] [--ignore]
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Verbose - print lines being parsed
      --infile INFILE       File to parse
      -f FORMAT, --format FORMAT
                            Type of formatting that will be found in the file
      -o OUTFORMAT, --outformat OUTFORMAT
                            Translate the format to this date format - you can get
                            a list of available formats using --formats
      --outfile OUTFILE     Output to the changed lines to this file
      --ignore              Ignore no matches - can be used with free text files -
                            potentially dangerous

## formats .py
This file contains a list of common dates and times and their regex.

#### in_formats

If we consider the following entry:

    'free-win-dir-uk': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strftime': '%d/%m/%Y  %H:%M'
		}
	},

This entry allows us to dissect the Windows dir command output in UK formatted time. The regex field allows the script to recognise a date in the line, and the strftime parser is then run over that regex output to get a python datetime object.
If it is possible to have two types of date/time formats in a file then additional formats need to be used:

    'free-osx-ls': {
		0: {
			'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d\d\:\d\d)',
			'strftime': '%d %b %H:%M'
		},
		1: {
			'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
			'strftime': '%d %b %Y'
		}
	}
The output of OSX ls command likes to exclude the year data if that file/directory has been created in the present year. For that reason, two parsers need to be used.

In the case of a missing year, the year is set to the present.

#### out_formats

This section allows you to quickly provide a format as a string rather than a format string on the command line

Pull requests welcome to update the list of formats!

## Possible next steps:
- Integrate into a simple Django app for easier use