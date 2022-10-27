"""Constants and functions used in setting/formatting labels displayed in
different parts of the app's UI.

Labels and formatting are set by dictionaries that use the same set of keys,
defined below in the constant STATISTIC_LABELS.  These keys must be used
consistently in both the app's front and back end code.  In order to facilitate
this, all constants and functions that involve hard-coded copies of the keys are
defined in the current module.  The flask back end delivers some labels defined
here to the front-end javascript code through a Jinja2 template.
"""

# Labels used within the app code as keys for different statistics
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
