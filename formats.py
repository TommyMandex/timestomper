in_formats = {

	'free-osx-ls': {
		0: {
			'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d\d\:\d\d)',
			'strftime': '%d %b %H:%M'
		},
		1: {
			'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
			'strftime': '%d %b %Y'
		}
	},

	'free-win-dir-uk': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strftime': '%d/%m/%Y  %H:%M'
		}
	},

	'free-win-dir-us': {
		0: {
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strftime': '%m/%d/%Y  %H:%M'
		}
	},

}

out_formats = {
	'epoch'	: '%s',
	'uk'	: '%d/%m/%y %H:%M',
	'us'	: '%m/%d/%y %H:%M',
}

