"""Constants and functions used in generating/updating/formatting labels
displayed in different parts of the app's interface.

Each instance of label text or formatting defined in the current module is
associated with a key.  The text and formatting can be freely modified as the
interface is tweaked, provided these keys are not modified.

The keys, which correspond to data categories or filters used in the app, take
the form of dictionary keys or index values in a pandas dataframe.

In order to facilitate consistent usage of these keys, most of the constants and
functions that include hard-coded instances of the keys are defined here.

Values defined in the current module that are needed by front-end code
are delivered through a Jinja2 HTML template, which uses dictionary keys to
select the strings rendered in the template, or in response to HTTP requests
made by the front end.

Some keys defined here depend on the data model exposed by the database_queries
module.  For instance, the keys used below in OD_TYPE_LABELS correspond to
values found in the column OD_type in the table of processed data on OD deaths.

There is also a dependency between the plots module and the keys in the
dictionaries TIME_PLOT_PARAM_NAMES and MAP_PLOT_PARAM_NAMES defined below.
Functions in the plots module use the keys in these dictionaries to extract
information about the query parameters sent with requests.
"""
from dataclasses import dataclass

import pandas as pd

from .database_queries import (
    execute_initialization_query, get_location_table, get_map_plot_periods,
    get_map_plot_ranges, get_od_types_for_location
)
from .date_formatting import MONTH_NAMES


# Used in setting option tags in the HTML template.
@dataclass
class SelectOption:
    """Class representing a single option in an HTML select element."""
    value: str
    text: str


def initialize_interface(app):
    """Initialize constants in the current module whose definition requires a
    database query.

    Note that this function should be executed during app initialization, but
    only after the pool of database connections has been initialized by means of
    the function initialize_connection_pool in database_connection.py.
    """
    global ORDERED_LOCATIONS, TIME_PERIODS    # pylint: disable=global-statement

    # Each empty dataframe is initialized using data from a database query.
    # Strictly speaking, we could simply overwrite the empty dataframes, but
    # rows are appended instead.  This is done in order to enforce the accuracy
    # of the schemas defined for ORDERED_LOCATIONS and TIME_PERIODS.
    if ORDERED_LOCATIONS.empty:
        ORDERED_LOCATIONS = pd.concat([
            ORDERED_LOCATIONS,
            generate_ordered_locations(app)
        ])
    if TIME_PERIODS.empty:
        TIME_PERIODS = pd.concat([
            TIME_PERIODS,
            generate_time_periods(app)
        ])

    if not all(COLORBAR_RANGES.values()):
        map_plot_ranges = execute_initialization_query(app, get_map_plot_ranges)
        for row in map_plot_ranges.itertuples():
            COLORBAR_RANGES[row.Index] = (row.Min_value, row.Max_value)


################################################################################
# Categories of OD death
################################################################################
OD_TYPE_LABELS = {
    'all_drug_od': 'All drug-overdose deaths',
    'all_opioids': 'All opioids',
    'synthetic_opioids': 'Fentanyl and other synthetic opioids',
    'prescription_opioids': 'Natural and semisynthetic opioids',
    'heroin': 'Heroin',
    'cocaine': 'Cocaine',
    'other_stimulants': 'Methamphetamine and other stimulants'
}


def get_od_types():
    """Return a list of SelectOption instances representing the different
    categories of OD deaths.

    The values are used internally to identify different categories of OD
    deaths, while the corresponding text is displayed in the UI.
    """
    return [SelectOption(value=key, text=label)
            for key, label in OD_TYPE_LABELS.items()]


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

# Title for the map plot's color bar
COLORBAR_TITLES = {
    'death_count': 'Number of deaths',
    'normalized_death_count': f'Deaths per<br>{UNIT_POPULATION_LABEL} people',
    'percent_change': 'Percent change<br>in one year'
}

# The values in COLORBAR_RANGES are initialized by the function
# initialize_interface, which is defined in the current module.  After
# initialization, the values in COLORBAR_RANGES are pairs containing the max and
# min values that can be displayed on the map for each statistic.
# COLORBAR_RANGES thus allows the color bar range shown for the map plot to
# remain fixed regardless of which period is selected for the plot.
COLORBAR_RANGES = {
    'death_count': None,
    'normalized_death_count': None,
    'percent_change': None
}

MAP_PLOT_HEADINGS = {
    'death_count': 'Number of drug-overdose deaths',
    'normalized_death_count': ('Number of drug-overdose deaths '
                               f'per {UNIT_POPULATION_LABEL} people'),
    'percent_change': 'Percent change in drug-overdose deaths'
}

TICKFORMATS = {
    'death_count': ',d',
    'normalized_death_count': '.0f',
    'percent_change': '.0%'
}

TIME_PLOT_HEADINGS = {
    'death_count': 'Number of deaths, preceding 12-month period',
    'normalized_death_count': (f'Number of deaths per {UNIT_POPULATION_LABEL} '
                               'people, preceding 12-month period'),
    'percent_change': ('Percent change in drug-overdose deaths, '
                       'preceding 12-month period')
}

# Labels displayed when hovering over a plot of time-development.
TIME_PLOT_HOVERTEMPLATES = {
    'death_count': '%{y:,d}<br>%{x|%b %Y}<extra></extra>',
    'normalized_death_count': '%{y:.1f}<br>%{x|%b %Y}<extra></extra>',
    'percent_change': '%{y:.2p}<br>%{x|%b %Y}<extra></extra>'
}

TIME_PLOT_YAXIS_TITLE_FORMATS = {
    'death_count': {'standoff': 5},
    'normalized_death_count': {},
    'percent_change': {'standoff': 5}
}


def get_statistic_types():
    """Return a list of SelectOption instances representing the different
    statistics used to describe the OD deaths.

    The values are used internally to identify different statistics, while the
    corresponding text is displayed in the UI.
    """
    return [SelectOption(value=key, text=label)
            for key, label in STATISTIC_LABELS.items()]


################################################################################
# Locations for which data is available.
################################################################################
# The constant ORDERED_LOCATIONS is initialized by the function
# generate_ordered_locations.  After initialization, ORDERED_LOCATIONS is a
# dataframe with information about the locations for which data on OD deaths is
# available.  Here ORDERED_LOCATIONS is defined as an empty dataframe in order
# to document its schema.
ORDERED_LOCATIONS = pd.DataFrame(
    {'Name': pd.Series(dtype=str)},
    index=pd.Index([], dtype=str, name='Abbr')
)


def generate_ordered_locations(app):
    """Generate a table of ordered locations for which data is available.

    Args:
        app:  Application instance created by the function create_app in the
            current package's __init__.py

    The module-level constant ORDERED_LOCATIONS is initialized to be a dataframe
    with the following index and column:
      - index (named Abbr) giving the abbreviation used for each location
      - column Name giving the full name of each location

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


def get_locations():
    """Return a list of SelectOption instances corresponding to locations for
    which data is available.

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
# The constant TIME_PERIODS is initialized by the function
# generate_time_periods.  After initialization, TIME_PERIODS is a dataframe with
# information about the periods that can be selected for the map plot that shows
# the distribution of OD deaths in the US.  Here TIME_PERIODS is defined as an
# empty dataframe in order to document its schema.
TIME_PERIODS = pd.DataFrame(
    {'Label': pd.Series(dtype=str),
     'Includes_percent_change': pd.Series(dtype=bool)},
    index=pd.Index([], dtype=str, name='Period')
)


def generate_time_periods(app):
    """Generate a table of time periods that can be selected for the map plot
    that shows the distribution of OD deaths in the US.

    Args:
        app:  Application instance created by the function create_app in the
            current package's __init__.py

    The module-level constant TIME_PERIODS is initialized to be a dataframe with
    the following index and column:
      - index (named Period) containing ISO-format date strings (e.g.,
          2015-01) representing periods that can be selected
      - column Label containing the label that will be used for that period in
          the interface (e.g., January 2015)
      - column Includes_percent_change containing booleans that indicate
          whether the percent change in OD deaths during the previous year
          is available for that period
    """
    data = execute_initialization_query(
        app, get_map_plot_periods
    )
    data = data.sort_values(by='Period')
    data['Label'] = data.index.map(_generate_label)
    return data


def _generate_label(iso_date_string):
    year, month_number = iso_date_string.split('-')
    return MONTH_NAMES[int(month_number)] + ' ' + year


def get_time_periods():
    """Return a list of SelectOption instances representing the different time
    periods for which map data can be displayed.

    The values are used internally to identify different time periods, while the
    corresponding text is displayed in the UI.
    """
    return [SelectOption(value=row.Index, text=row.Label)
            for row in TIME_PERIODS.itertuples()]


def get_previous_period_label(period_key):
    """Given as input a string used internally to identify a time period, return
    a UI label representing time period one year earlier.

    For example, if the argument to the function is '2019-09', return
    'September 2018'.
    """
    year, month_number = period_key.split('-')
    return MONTH_NAMES[int(month_number)] + ' ' + str(int(year) - 1)


################################################################################
# HTML headings that are updated dynamically
################################################################################
def get_map_plot_heading(params):
    """Return an HTML heading dynamically selected for the map plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    return MAP_PLOT_HEADINGS[params['statistic']]


def get_map_plot_subheading(params):
    """Return an HTML subheading dynamically selected for the map plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    period_key = params['period']
    period_label = TIME_PERIODS.loc[period_key, 'Label']
    if params['statistic'] == 'percent_change':
        subheading = (get_previous_period_label(period_key)
                      + ' to ' + period_label)
    else:
        subheading = 'Twelve-month period ending ' + period_label
    return subheading


def get_time_plot_heading(params):
    """Return an HTML heading dynamically selected for the time plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as TIME_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    return TIME_PLOT_HEADINGS[params['statistic']]


def get_time_plot_subheading(params):
    """Return an HTML subheading dynamically selected for the time plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as TIME_PLOT_PARAM_NAMES, which is defined in the
            current module.
    """
    return ORDERED_LOCATIONS.loc[params['location'], 'Name']


################################################################################
# Options for HTML select elements that are updated dynamically
################################################################################
def get_map_plot_statistic_options(params):
    """Return a list of options dynamically selected for the form control that
    determines which statistic is displayed on the map plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.

    Returns:
        List of strings, each corresponding to an option value
    """
    if TIME_PERIODS.loc[params['period'], 'Includes_percent_change']:
        return list(STATISTIC_LABELS.keys())

    statistic_labels = STATISTIC_LABELS.copy()
    del statistic_labels['percent_change']
    return list(statistic_labels.keys())


def get_map_plot_period_options(params):
    """Return a list of options dynamically selected for the form control that
    determines which time period is displayed on the map plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as MAP_PLOT_PARAM_NAMES, which is defined in the
            current module.

    Returns:
        List of strings, each corresponding to an option value
    """
    if params['statistic'] == 'percent_change':
        return  list(
            TIME_PERIODS.index[
                TIME_PERIODS['Includes_percent_change']
            ]
        )

    return list(TIME_PERIODS.index)


def get_time_plot_od_type_options(params):
    """Return a list of options dynamically selected for the form control that
    determines which type of OD death is displayed on the map plot.

    Args:
        params:  Dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should include
            the same keys as TIME_PLOT_PARAM_NAMES, which is defined in the
            current module.

    Returns:
        List of strings, each corresponding to an option value
    """
    unordered_options = get_od_types_for_location(params['location'])
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
EPIDEMIC_OVERVIEW_PARAMS = [
    {'name': TIME_PLOT_PARAM_NAMES['location'],
     'value': 'US'},
    {'name': TIME_PLOT_PARAM_NAMES['statistic'],
     'value': 'death_count'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'all_drug_od'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'all_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'synthetic_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'prescription_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'heroin'}
]

GROWTH_RATE_PARAMS = [
    {'name': TIME_PLOT_PARAM_NAMES['location'],
     'value': 'US'},
    {'name': TIME_PLOT_PARAM_NAMES['statistic'],
     'value': 'percent_change'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'all_drug_od'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'all_opioids'},
    {'name': TIME_PLOT_PARAM_NAMES['od_type'],
     'value': 'synthetic_opioids'}
]

DISTRIBUTION_PARAMS = [
    {'name': MAP_PLOT_PARAM_NAMES['statistic'],
     'value': 'normalized_death_count'},
    {'name': MAP_PLOT_PARAM_NAMES['period'],
     'value': '2017-11'}
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
        'epidemic_overview': EPIDEMIC_OVERVIEW_PARAMS,
        'growth_rate': GROWTH_RATE_PARAMS,
        'distribution': DISTRIBUTION_PARAMS
    }
