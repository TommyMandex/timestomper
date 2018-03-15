searches = {
 
	'osx-ls': [
		{
				'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d\d\:\d\d)',
				'strptime': '%d %b %H:%M'
		},
		{
				'regex': r'(\d\d?\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
				'strptime': '%d %b %Y'
		}
	],

	'win-dir-uk': [
		{
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strptime': '%d/%m/%Y  %H:%M'
		}
	],

	'win-dir-us': [
		{
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\s\d{2}\:\d{2})',
			'strptime': '%m/%d/%Y  %H:%M'
		}
	],

	'web-golive': [
		{
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{2}\:\d{2}\s[AP]M\s\w+)',
			'strptime': '%m/%d/%Y  %H:%M %p %Z'
		}
	],

	'cli-golive': [
		{
			'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{2}\:\d{2}:\d{2}\s[AP]M)',
			'strptime': '%m/%d/%Y  %H:%M:%S %p'
		}
	],

}

out_strftime = {
	'epoch'		: '%s',
	'uk'		: '%d/%m/%y %H:%M',
	'us'		: '%m/%d/%y %H:%M',
	'year'		: '%y-%m-%d %H:%M',
	'default'	: '%Y%m%d_%H%M',
}