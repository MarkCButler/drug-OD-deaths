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
select the strings rendered in the template, or in response to HTTP requests
made by the front end.

Some dictionaries defined here depend on the data model exposed by the
database_queries module.  For instance, the keys used below in OD_TYPE_LABELS
correspond to values found in the column OD_type in the table of OD deaths.

There is also a dependency between the keys in some dictionaries defined here
and the processing module in the current package.  Requests by the front end for
plot data include query parameters defined by constants in the current module.
The back-end functions that process data to fulfill these requests need to
"understand" keys such as 'death_count', 'normalized_death_count', and
'percent_change' (see STATISTIC_LABELS below) in order to determine how data
should be processed.
"""
from collections import namedtuple

import pandas as pd

from .database_queries import (
    DATASET_START_YEAR, DATASET_END_YEAR, execute_initialization_query,
    get_od_types_for_location, get_location_table
)

# Used in setting option tags in the HTML template.
SelectOption = namedtuple('SelectOption', ['value', 'text'])


def initialize_ui_labels(app):
    """Initialize constants in the current module whose definition requires a
    database query.

    Note that this function should be executed during app initialization, but
    only after the pool of database connections has been initialized by means of
    the function initialize_connection_pool in database_connection.py.
    """
    global ORDERED_LOCATIONS                  # pylint: disable=global-statement
    if ORDERED_LOCATIONS is None:
        ORDERED_LOCATIONS = generate_ordered_locations(app)


def generate_ordered_locations(app):
    """Generate a table of ordered locations for which data is available.

    The module-level constant ORDERED_LOCATIONS is initialized to be a dataframe
    with the following index and column:
      - index (named 'Abbr') giving the abbreviation used for each location
      - column 'Name' giving the full name of each location

    The table of locations exposed by the database_queries module is first
    retrieved. Rows are then ordered alphabetically based on the full name of
    the location (which will appear in the UI), and the row corresponding to the
    US is moved to the top of the table.
    """
    data = (
        execute_initialization_query(app, get_location_table)
        .sort_values(by='Name')
    )
    reordered_index = data.index.drop('US').insert(0, 'US')
    return data.reindex(reordered_index)


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
    """Return a list of named tuples of the form (value, text) representing the
    different categories of OD deaths.

    The values are used internally to identify different categories of OD
    deaths, while the corresponding text is displayed in the UI.
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
# The unit used to normalize death count
################################################################################
UNIT_POPULATION = 1e5
UNIT_POPULATION_LABEL = format(int(UNIT_POPULATION), ',')


################################################################################
# Labels / formatting that depend on the statistic used to characterize
# OD deaths
################################################################################
STATISTIC_LABELS = {
    'death_count': 'Number of deaths',
    'normalized_death_count': f'Deaths per {UNIT_POPULATION_LABEL} people',
    'percent_change': 'Percent change in one year'
}

# Labels displayed when hovering over a map
MAP_HOVERTEMPLATES = {
    'death_count': '%{z:,d}<br>%{text}<extra></extra>',
    'normalized_death_count': '%{z:.1f}<br>%{text}<extra></extra>',
    'percent_change': '%{z:.2p}<br>%{text}<extra></extra>'
}

# Labels, formatting, and range for the map colorbar
COLORBAR_TITLES = {
    'death_count': 'Number of deaths',
    'normalized_death_count': f'Deaths per<br>{UNIT_POPULATION_LABEL} people',
    'percent_change': 'Percent change<br>in one year'
}
COLORBAR_TICKFORMATS = {
    'death_count': ',d',
    'normalized_death_count': '.0f',
    'percent_change': '.0%'
}
# For each statistic, the colorbar range is set to the max and min values of
# that statistic for the dataset.  The colorbar range remains fixed regardless
# of which period is selected for the map plot.
# TODO:  Add SQL query to obtain these ranges during app initialization.
COLORBAR_RANGES = {
    'death_count': (55, 5959),
    'normalized_death_count': (5.9, 55.4),
    'percent_change': (-.333, .573)
}

MAP_PLOT_HEADINGS = {
    'death_count': 'Number of drug-overdose deaths',
    'normalized_death_count': ('Number of drug-overdose deaths '
                               f'per {UNIT_POPULATION_LABEL} people'),
    'percent_change': 'Percent change in drug-overdose deaths'
}


TIME_PLOT_HEADINGS = {
    'death_count': 'Number of deaths, preceding 12-month period',
    'normalized_death_count': (f'Number of deaths per {UNIT_POPULATION_LABEL} '
                               'people, preceding 12-month period'),
    'percent_change': ('Percent change in drug-overdose deaths, '
                       'preceding 12-month period')
}


def get_statistic_types():
    """Return a list of named tuples of the form (value, text) representing the
    different statistics used to describe the OD deaths.

    The values are used internally to identify different statistics, while the
    corresponding text is displayed in the UI.
    """
    named_tuples = map(SelectOption._make, STATISTIC_LABELS.items())
    return list(named_tuples)


################################################################################
# Locations for which data is available.
################################################################################
# The constant ORDERED_LOCATIONS is used within the functions get_locations and
# get_location_names.  We must interact with the database in order to define
# this constant, and the app only supports doing this within an application
# context.  So ORDERED_LOCATIONS is defined below to be None, and it is
# re-defined during app initialization by the function
# generate_ordered_locations.
ORDERED_LOCATIONS = None


def get_locations():
    """Return a list of named tuples of the form (value, text) corresponding to
    locations for which data is available.

    The values are abbreviations used internally to identify locations, while
    the corresponding text is displayed in the UI.
    """
    return [SelectOption(value=row.Index, text=row.Name)
            for row in ORDERED_LOCATIONS.itertuples()]


def get_location_names():
    """Return a list of full names of the locations for which data is
    available.
    """
    return list(ORDERED_LOCATIONS['Name'])


################################################################################
# Time periods that can be selected for plots.
################################################################################
# Example key-value pair in the TIME_PERIODS dictionary:
#
# 'september_2018': 'September 2018'
#
# The key 'september_2018' corresponds to the 12-month period ending September
# 2018.
TIME_PERIODS = {
    ('september_' + str(year)): ('September ' + str(year))
    for year in range(DATASET_START_YEAR, DATASET_END_YEAR + 1)
}

FIRST_TIME_PERIOD = 'september_' + str(DATASET_START_YEAR)

# Used to convert time periods sent as query parameters into data that can be
# consumed by the back end.
TimePeriod = namedtuple('TimePeriod', ['month', 'year'])


def get_time_periods():
    """Return a list of name tuples of the form (value, text) representing the
    different time periods for which map data can be displayed.

    The values are used internally to identify different time periods, while the
    corresponding text is displayed in the UI.
    """
    named_tuples = map(SelectOption._make, TIME_PERIODS.items())
    return list(named_tuples)


def get_month_and_year(period_key):
    """Extract the month and year from a string used internally to identify a
    time period.

    The function returns a 2-element iterable Month, Year.
    """
    month, year = period_key.split('_')
    return TimePeriod(month=month.capitalize(), year=int(year))


def get_current_period_label(period_key):
    """Given as input a string used internally to identify a time period, return
    a UI label representing the same time period.

    For example, if argument to the function is 'september_2019', return
    'September 2019'.
    """
    month, year = period_key.split('_')
    return f'{month.capitalize()} {year}'


def get_previous_period_label(period_key):
    """Given as input a string used internally to identify a time period, return
    a UI label representing time period one year earlier.

    For example, if argument to the function is 'september_2019', return
    'September 2018'.
    """
    month, year = period_key.split('_')
    return f'{month.capitalize()} {int(year) - 1}'


################################################################################
# HTML headings that are updated dynamically
################################################################################
def get_map_plot_heading(param_dict):
    """Return an HTML heading dynamically selected for the map plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    return MAP_PLOT_HEADINGS[param_dict['statistic']]


def get_map_plot_subheading(param_dict):
    """Return an HTML subheading dynamically selected for the map plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    period_key = param_dict['period']
    period_label = get_current_period_label(period_key)
    if param_dict['statistic'] == 'percent_change':
        subheading = (get_previous_period_label(period_key)
                      + ' to ' + period_label)
    else:
        subheading = 'Twelve-month period ending ' + period_label
    return subheading


def get_time_plot_heading(param_dict):
    """Return an HTML heading dynamically selected for the time plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as TIME_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    return TIME_PLOT_HEADINGS[param_dict['statistic']]


def get_time_plot_subheading(param_dict):
    """Return an HTML subheading dynamically selected for the time plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as TIME_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    return ORDERED_LOCATIONS.loc[param_dict['location'], 'Name']


################################################################################
# Options for HTML select elements that are updated dynamically
################################################################################
def get_map_plot_statistic_options(param_dict):
    """Return a list of options dynamically selected for the form control that
    determines which statistic is displayed on the map plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.

    Returns:
        List of strings, each corresponding to an option value
    """
    if param_dict['period'] == FIRST_TIME_PERIOD:
        statistic_labels = STATISTIC_LABELS.copy()
        del statistic_labels['percent_change']
    else:
        statistic_labels = STATISTIC_LABELS
    return list(statistic_labels.keys())


def get_map_plot_period_options(param_dict):
    """Return a list of options dynamically selected for the form control that
    determines which time period is displayed on the map plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.

    Returns:
        List of strings, each corresponding to an option value
    """
    if param_dict['statistic'] == 'percent_change':
        time_periods = TIME_PERIODS.copy()
        del time_periods[FIRST_TIME_PERIOD]
    else:
        time_periods = TIME_PERIODS
    return list(time_periods.keys())


def get_time_plot_od_type_options(param_dict):
    """Return a list of options dynamically selected for the form control that
    determines which type of OD death is displayed on the map plot.

    Args:
        param_dict:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as TIME_PLOT_PARAM_NAMES, which is defined in the
            current module.

    Returns:
        List of strings, each corresponding to an option value
    """
    unordered_options = get_od_types_for_location(param_dict['location'])
    # Order the options based on the order of keys in OD_TYPE_LABELS.
    return [option for option in OD_TYPE_LABELS
            if option in unordered_options]


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
     'value': 'december_2017'}
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
