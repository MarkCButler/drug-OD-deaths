"""Constants and functions used in setting/formatting labels displayed in
different parts of the app's UI.

In cases where the labels/formatting are specified below by a dictionary, the
dictionary keys correspond to data categories used in the app's UI.  These keys
must be used consistently in both the app's front and back-end code.  In order
to facilitate consistent usage of these keys, all constants and functions that
involve hard-coded copies of the keys are defined in the current module.  Labels
defined here that are needed by front-end code are delivered by the back end
through a Jinja2 HTML template or are returned in response to AJAX-style calls.
"""
from collections import namedtuple

import pandas as pd

# Used in setting option tags in the HTML template.
SelectOption = namedtuple('SelectOption', ['value', 'name'])

################################################################################
# Categories of OD death
################################################################################
OD_TYPE_LABELS = {
    'all_drug_OD': 'All drug-overdose deaths',
    'all_opioids': 'All opioids',
    'prescription_opioids': 'Prescription opioid pain relievers',
    'synthetic_opioids': 'Fentanyl and other synthetic opioids',
    'heroin': 'Heroin',
    'cocaine': 'Cocaine',
    'other_stimulants': 'Methamphetamine and other stimulants'
}


def get_od_types():
    """Return a list of named tuples of the form (value, name) representing the
    different categories of OD deaths.

    The values are used internally to identify different categories of OD
    deaths, while the corresponding names are displayed in the UI.
    """
    named_tuples = map(SelectOption._make, OD_TYPE_LABELS.items())
    return list(named_tuples)


def get_od_code_table():
    """Return a table showing the correspondence between the following:
    1. Labels used in the app's UI to indicate the type of overdose
    2. Cause-of-death codes from ICD–10, the Tenth Revision of the International
    Statistical Classification of Diseases and Related Health Problems
    """
    data = [
        ('all_opioids', 'T40.0-T40.4, T40.6'),
        ('heroin', 'T40.1'),
        ('prescription_opioids', 'T40.2'),
        ('synthetic_opioids', 'T40.3, T40.4'),
        ('cocaine', 'T40.5'),
        ('other_stimulants', '43.6')
    ]
    code_table = pd.DataFrame(data, columns=['Label', 'Code'])
    code_table.Label = code_table.Label.replace(OD_TYPE_LABELS)
    return code_table


################################################################################
# Statistics used to describe OD deaths
################################################################################
STATISTIC_LABELS = {
    'death_count': 'Number of deaths',
    'normalized_death_count': 'Deaths per 100,000 people',
    'percent_change': 'Percent change in one year'
}

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


def get_statistic_types():
    """Return a list of named tuples of the form (value, name) representing the
    different statistics used to describe the OD deaths.

    The values are used internally to identify different statistics, while the
    corresponding names are displayed in the UI.
    """
    named_tuples = map(SelectOption._make, STATISTIC_LABELS.items())
    return list(named_tuples)


################################################################################
# Locations for which data is available.
################################################################################
ORDERED_LOCATIONS = {
    'US': 'United States',
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}


def get_locations():
    """Return a list of named tuples of the form (value, name) corresponding to
    locations for which data is available.

    The values are abbreviations used internally to identify locations, while
    the corresponding names are displayed in the UI.
    """
    named_tuples = map(SelectOption._make, ORDERED_LOCATIONS.items())
    return list(named_tuples)


def get_location_names():
    """Return a list of full names of the locations for which data is
    available.
    """
    return list(ORDERED_LOCATIONS.values())


def get_location_abbr():
    """Return a list of abbreviations of the locations for which data is
    available.
    """
    return list(ORDERED_LOCATIONS.keys())
