"""Constants and functions used in setting/formatting labels displayed in
different parts of the app's UI.

Some labels and formatting are set by dictionaries that use a common set of
keys, defined below in the constant STATISTIC_LABELS.  These keys must be used
consistently in both the app's front and back end code.  In order to facilitate
this, all constants and functions that involve hard-coded copies of the keys are
defined in the current module.  The flask back end delivers some labels defined
here to the front-end javascript code through a Jinja2 template.
"""

# TODO:  Check whether this list is needed as a Python object.  Possibly just
#   define in a comment.
STATISTIC_LABELS = ['death_count', 'normalized_death_count', 'percent_change']

# Labels displayed when hovering over a map
MAP_HOVERTEMPLATES = {
    'death_count': '%{z:,d}<br>%{text}<extra></extra>',
    'normalized_death_count': '%{z:.1f}<br>%{text}<extra></extra>',
    'percent_change': '%{z:.2p}<br>%{text}<extra></extra>'
}
# Labels and formatting for the map colorbar
COLORBAR_TITLES = {
    'death_count': 'Number of deaths',
    'normalized_death_count': 'Deaths per<br>100,000 people',
    'percent_change': 'Percent change<br>in one year'
}
COLORBAR_TICKFORMATS = {
    'death_count': ',d',
    'normalized_death_count': '.0f',
    'percent_change': '.0%'
}

# List of full names of locations for which data is available.
ORDERED_LOCATIONS = [
    'United States', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
    'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii',
    'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
    'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
    'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
    'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]
