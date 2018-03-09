in_formats = {

	'osx-ls': {
		0: {
			'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d\d\:\d\d)',
			'strftime': '%d %b %H:%M'
		},
		1: {
			'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
			'strftime': '%d %b %Y'
		}
	},

	'win-dir-uk': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strftime': '%d/%m/%Y  %H:%M'
		}
	},

	'win-dir-us': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strftime': '%m/%d/%Y  %H:%M'
		}
	},

	'web-golive': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{2}\:\d{2}\s[AP]M\s\w+)',
			'strftime': '%m/%d/%Y  %H:%M %p %Z'
		}
	},

	'cli-golive': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{2}\:\d{2}:\d{2}\s[AP]M)',
			'strftime': '%m/%d/%Y  %H:%M:%S %p'
		}
	},
}

out_formats = {
	'epoch'	: '%s',
	'uk'	: '%d/%m/%y %H:%M',
	'us'	: '%m/%d/%y %H:%M',
	'year'	: '%y-%m-%d %H_%M',
}

