"""Functions that returned processed data to be consumed by plotting
functions.
"""
from flask import current_app

from .database import get_map_data, get_time_data, DATASET_START_YEAR
from .ui_labels import get_month_and_year

# The unit used to normalize death count.
UNIT_POPULATION = 1e5


def get_processed_map_data(param_dict):
    """Return a dataframe of processed data that can be used to generate a map
    plot.

    The argument param_dict gives information about the query parameters used in
    requesting the plot.  The dictionary should have two keys:
      -'statistic':  allowed values are 'death_count', 'normalized_death_count',
          and 'percent_change'
      - 'period':  the current module does not need to "understand" the value,
          because the function get_month_and_year (imported from the module
          ui_labels) is used to convert it to a named tuple with attributes
          month and year.

    The dataframe returned by the function has columns Location, Location_abbr,
    Value.
    """
    period = get_month_and_year(param_dict['period'])
    data = get_map_data(month=period.month, year=period.year,
                        add_location_names=True)
    data = process_map_data(data, statistic=param_dict['statistic'],
                            month=period.month, year=period.year)
    current_app.logger.info('\n\n\n' + data.head().to_string() + '\n\n\n')
    current_app.logger.info('\n\n\n' + str(data.columns) + '\n\n\n')
    return data


def process_map_data(data, statistic, month, year):
    """Process the data fetched from the database as needed for a plot requested
    by the front end.

    Args:
        data:  map data fetched from the database
        statistic:  the statistic that should be displayed in the plot (one of
            the strings 'death_count', 'normalized_death_count', or
            'percent_change')
        month:  the month previously used to filter the data
        year:  the year previously used to filter the data

    The dataframe returned by the function has columns Location, Location_abbr,
    Value.
    """
    if statistic == 'percent_change':
        return _process_map_percent_change(data, month, year)
    if statistic == 'normalized_death_count':
        return _normalize_by_population(data)
    if statistic == 'death_count':
        return data.rename(columns={'Death_count': 'Value'})

    message = ('Unable to process map data because the requested statistic '
               f'"{statistic}" is not recognized.')
    raise ValueError(message)


def _process_map_percent_change(data, month, year):
    prior_year = year - 1
    _check_year_for_percent_change(year, prior_year)
    prior_year_data = (
        get_map_data(month=month, year=prior_year, add_location_names=False)
        .set_index('Location_abbr')
        .drop(columns=['Month', 'Year'])
        .rename(columns={'Death_count': 'Prior_death_count'})
    )
    data = (
        data
        .drop(columns=['Month', 'Year'])
        .join(prior_year_data, on='Location_abbr')
    )
    data['Value'] = (
        (data['Death_count'] - data['Prior_death_count']) / data['Death_count']
    )
    return data.drop(columns=['Death_count', 'Prior_death_count'])


def _check_year_for_percent_change(year, prior_year):
    if prior_year < DATASET_START_YEAR:
        message = (
            f'Attempted to calculate percent change when the year is {year}.\n'
            f'Data is not available for {prior_year}.  The first year '
            f'for which data is available is {DATASET_START_YEAR}.'
        )
        raise ValueError(message)


def _normalize_by_population(data):
    return data


def get_processed_time_data(param_dict):
    """Return a dataframe of processed data that can be used to generate a plot
    of time development.

    The argument param_dict gives information about the query parameters used in
    requesting the plot.  The dictionary should have three keys:
      - 'location':  allowed values are given by the Abbr column of the table of
          locations exposed by the database module in the current package. (Note
          that a list of allowed values can be obtained programmatically from
          the function get_locations in the module ui_labels.)
      -'statistic':  allowed values are 'death_count', 'normalized_death_count',
          and 'percent_change'
      - 'od_type':  a string or a list of strings, each equal to a value
          appearing in the OD_type column in the table of OD deaths exposed by
          the database module.  (Note that the allowed values are keys in the
          dictionary OD_TYPE_LABELS in the module ui_labels.)

    The dataframe returned by the function has columns Year, Month, OD_type, and
    Value.
    """
    data = get_time_data(
        location_abbr=param_dict['location'],
        od_types=param_dict['od_type'],
    )
    return process_time_data(data, statistic=param_dict['statistic'])


def process_time_data(data, statistic):
    return data
