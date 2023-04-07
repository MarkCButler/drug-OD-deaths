"""Constants and functions used in managing labels displayed in different parts
of the app's interface.

The keys in the dictionaries below can be considered code that must be used
consistently in both the app's front end and back end.  These keys correspond to
data categories or filters used in the app, while the values determine what is
displayed in the UI and the HTML markup.

In order to facilitate consistent usage of these keys, several constants and
functions that involve hard-coded instances of the keys are defined here.

Values defined in the current module that are needed by front-end code
are delivered through a Jinja2 HTML template, which uses dictionary keys to
select the strings rendered in the template.

Some dictionaries defined here depend on the data model exposed by the database
module.  For instance, the keys used below in OD_TYPE_LABELS correspond to
values found in the column OD_type in the table of OD deaths.

There is also a dependency between the keys in some dictionaries defined here
and the module processed_data.  Requests by the front end for plot data include
parameter name-value pairs defined by constants in the current module.  The
back-end functions that process data to fulfill these requests need to
"understand" keys such as 'death_count', 'normalized_death_count', and
'percent_change' (see STATISTIC_LABELS below) in order to determine how data
should be processed.
"""
from collections import namedtuple

import pandas as pd

from .database import get_location_table

# Used in setting option tags in the HTML template.
SelectOption = namedtuple('SelectOption', ['value', 'name'])

################################################################################
# Categories of OD death
################################################################################
OD_TYPE_LABELS = {
    'all_drug_od': 'All drug-overdose deaths',
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
# The constant ORDERED_LOCATIONS is used within the functions get_locations and
# get_location_names.  We must interact with the database in order to define
# this global variable, and currently this is only supported within an app
# context.  So ORDERED_LOCATIONS is initially defined to be None, and it is
# defined on the fly when needed by an instance of the app.
ORDERED_LOCATIONS = None


def generate_ordered_locations():
    """Generate a table of ordered locations for which data is available.

    The table of locations exposed by the database module is first retrieved.
    Rows are first ordered alphabetically based on the full name of the location
    (which will appear in the UI), and then the row corresponding to the US is
    moved to the top of the table.
    """
    # Note that the function get_location_table used in the next line of code
    # returns a dataframe with 'Abbr' as the index.  This is convenient for all
    # functions that consume this dataframe (including the current function).
    # However, reset_index is used below to convert 'Abbr' into a column, in
    # order to simplify functions that consume the output of the current
    # function.
    data = get_location_table().sort_values(by='Name')
    reordered_index = data.index.drop('US').insert(0, 'US')
    return data.reindex(reordered_index).reset_index()


def _ensure_location_definitions():
    global ORDERED_LOCATIONS                  # pylint: disable=global-statement
    if ORDERED_LOCATIONS is None:
        ORDERED_LOCATIONS = generate_ordered_locations()


def get_locations():
    """Return a list of named tuples of the form (value, name) corresponding to
    locations for which data is available.

    The values are abbreviations used internally to identify locations, while
    the corresponding names are displayed in the UI.
    """
    _ensure_location_definitions()
    return [SelectOption(value=row.Abbr, name=row.Name)
            for row in ORDERED_LOCATIONS.itertuples(index=False)]


def get_location_names():
    """Return a list of full names of the locations for which data is
    available.
    """
    _ensure_location_definitions()
    return list(ORDERED_LOCATIONS.Name)


################################################################################
# Time periods that can be selected for plots.
################################################################################
TIME_PERIODS = ['September ' + str(year)
                for year in range(2015, 2020)]

# Used to convert time-period labels displayed in the UI into data that can be
# consumed by the back end.
TimePeriod = namedtuple('TimePeriod', ['month', 'year'])


def get_month_and_year(time_period):
    """Extract the month and year from a time period label used in the UI.

    The function returns a 2-element iterable Month, Year.
    """
    month, year = time_period.split()
    return TimePeriod(month=month, year=int(year))


################################################################################
# Parameter names used in front-end requests for plots
################################################################################
TIME_PLOT_PARAM_NAMES = {
    'location': 'time-plot-location',
    'statistic': 'time-plot-statistic',
    'od_type': 'time-plot-od-type'
}

MAP_PLOT_PARAM_NAMES = {
    'statistic': 'map-plot-statistic',
    'period': 'map-plot-period'
}


################################################################################
# Parameter name-value pairs for plots of the summary pane.
################################################################################
EPIDEMIC_PEAK_PARAMS = [
    {'name': TIME_PLOT_PARAM_NAMES['location'],
     'value': 'US'},
    {'name': TIME_PLOT_PARAM_NAMES['statistic'],
     'value': 'death_count'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'all_drug_od'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'prescription_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'synthetic_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'heroin'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'cocaine'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'other_stimulants'}
]

GROWTH_RATE_PARAMS = [
    {'name': TIME_PLOT_PARAM_NAMES['location'],
     'value': 'US'},
    {'name': TIME_PLOT_PARAM_NAMES['statistic'],
     'value': 'percent_change'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'all_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'prescription_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'synthetic_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'heroin'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'cocaine'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'other_stimulants'}
]

DISTRIBUTION_PARAMS = [
    {'name': MAP_PLOT_PARAM_NAMES['statistic'],
     'value': 'normalized_death_count'},
    {'name': MAP_PLOT_PARAM_NAMES['period'],
     'value': 'December 2017'}
]


def get_preset_plot_params():
    """Return a dictionary that can be used by the front end to generate preset
    query strings for certain plots.

    For plots linked to an HTML form, the parameters of the plot can be changed
    interactively by the user.  When the front end queries the back end for a
    plot linked to a form, parameters from the form are included in the query.

    For plots not linked to an HTML form, the front end uses the dataset object
    to retrieve the parameters that should be included in the query string.  The
    dictionary returned by the current function is used in the Jinja2 HTML
    template to populate the dataset objects with information about parameters.

    Each key in the dictionary corresponds to a plot.  Each value is a list of
    name-value pairs representing parameters to be used by the front end in
    querying the back end for the plot.
    """
    return {
        'epidemic_peak': EPIDEMIC_PEAK_PARAMS,
        'growth_rate': GROWTH_RATE_PARAMS,
        'distribution': DISTRIBUTION_PARAMS
    }
