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

    'uk': [
        {
            'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{1,2}\:\d{1,2}\:\d{1,2})',
            'strptime': '%d/%m/%Y %H:%M:%S'
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

    'cbrcli': [
        {
            'regex': r'(\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\.\d*)',
            'strptime': '%Y-%m-%d %H:%M:%S.%f'
        }
    ],

    'us-slash': [
        {
            'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{2}\:\d{2}\:\d{2})',
            'strptime': '%m/%d/%Y %H:%M:%S'
        }
    ],

    'us-slash-no_secs': [
        {
            'regex': r'(\d{2}\/\d{2}\/\d{4}\s\d{2}\:\d{2})',
            'strptime': '%m/%d/%Y %H:%M'
        }
    ],

}

out_strftime = {
    'epoch'     : '%s',
    'uk'        : '%d/%m/%y %H:%M:%S',
    'us'        : '%m/%d/%y %H:%M:%S',
    'year'      : '%y-%m-%d %H:%M:%S',
    'default'   : '%Y/%m/%d %H:%M:%S',
}
