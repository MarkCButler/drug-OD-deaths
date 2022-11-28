"""Constants and functions used in setting/formatting labels displayed in
different parts of the app's UI.

In cases where the labels/formatting are specified below by a dictionary, the
dictionary keys correspond to data categories used in the app's UI.  These keys
must be used consistently in both the app's front and back-end code.  In order
to facilitate consistent usage of these keys, all constants and functions that
involve hard-coded copies of the keys are defined in the current module.  Labels
defined here that are needed by front-end javascript code are delivered by the
back end through a Jinja2 template.
"""
import pandas as pd

################################################################################
# Categories of OD death
################################################################################
ORDERED_OD_TYPE_KEYS = [
    'all_drug_OD',
    'all_opioids',
    'prescription_opioids',
    'synthetic_opioids',
    'heroin',
    'cocaine',
    'other_stimulants'
]

OD_TYPE_LABELS = {
    'all_drug_OD': 'All drug-overdose deaths',
    'all_opioids': 'All opioids',
    'prescription_opioids': 'Prescription opioid pain relievers',
    'synthetic_opioids': 'Fentanyl and other synthetic opioids',
    'heroin': 'Heroin',
    'cocaine': 'Cocaine',
    'other_stimulants': 'Methamphetamine and other stimulants'
}


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
# TODO:  Check whether this list is needed as a Python object.  Possibly just
#   define in a comment.
ORDERED_STATISTIC_KEYS = [
    'death_count',
    'normalized_death_count',
    'percent_change'
]

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

################################################################################
# Misc labels
################################################################################
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
