"""Functions that returned processed data to be consumed by plotting
functions.
"""
from flask import current_app

from .database import (
    DATASET_START_YEAR, get_map_plot_death_counts, get_map_plot_populations,
    get_time_plot_death_counts, get_time_plot_populations
)
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
    data = get_map_plot_death_counts(month=period.month, year=period.year,
                                     add_location_names=True)
    data = process_map_data(data, statistic=param_dict['statistic'],
                            month=period.month, year=period.year)
    current_app.logger.info('\n\n\n' + data.head().to_string() + '\n\n\n')
    return data


def process_map_data(data, statistic, month, year):
    """Process the data fetched from the database as needed for a map plot
    requested by the front end.

    Args:
        data:  map data fetched from the database containing columns
            Location_abbr, Location, Death_count.  The death counts in this
            table correspond to the period specified by arguments month, year.
        statistic:  the statistic that should be displayed in the plot (one of
            the strings 'death_count', 'normalized_death_count', or
            'percent_change')
        month:  the month previously used to filter the data
        year:  the year previously used to filter the data

    Returns:
        Dataframe with columns Location, Location_abbr, and Value.  The
        statistic argument to the function determines what data is present in
        the Value column.  For example, if the argument is
        normalized_death_count, the Value column gives the number of deaths per
        UNIT_POPULATION.
    """
    if statistic == 'percent_change':
        return _find_percent_change_map_data(data, month, year)
    if statistic == 'normalized_death_count':
        return _normalize_map_data(data, month, year)
    if statistic == 'death_count':
        return data.rename(columns={'Death_count': 'Value'})

    message = ('Unable to process map data because the requested statistic '
               f'"{statistic}" is not recognized.')
    raise ValueError(message)


def _find_percent_change_map_data(data, month, year):
    prior_year = year - 1
    _check_year_for_percent_change(year, prior_year)
    prior_year_data = (
        get_map_plot_death_counts(month=month, year=prior_year,
                                  add_location_names=False)
        .set_index('Location_abbr')
        .rename(columns={'Death_count': 'Prior_death_count'})
    )
    data = data.join(prior_year_data, on='Location_abbr', how='inner')
    data['Value'] = (
        (data['Death_count'] - data['Prior_death_count'])
        / data['Prior_death_count']
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


def _normalize_map_data(data, month, year):
    """Normalize by population the death counts for the map plot.

    Args:
        data:  map data fetched from the database, containing columns
            Location_abbr, Location, and Death_count.  The death counts in this
            table correspond to the period specified by arguments month, year.
        month:  the month previously used to filter the data
        year:  the year previously used to filter the data

    Returns:
        Dataframe with columns Location, Location_abbr, and Value.  The Value
        column gives the number of deaths per UNIT_POPULATION.
    """
    population_data = (
        get_map_plot_populations(month, year)
        .set_index('Location_abbr')
    )
    data = data.join(population_data, on='Location_abbr', how='inner')
    data['Value'] = (
        data['Death_count'] * UNIT_POPULATION / data['Population']
    )
    return data.drop(columns=['Death_count', 'Population'])


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
    data = get_time_plot_death_counts(
        location_abbr=param_dict['location'],
        od_types=param_dict['od_type'],
    )
    data = process_time_data(data, statistic=param_dict['statistic'],
                             location_abbr=param_dict['location'])
    current_app.logger.info('\n\n\n' + data.head().to_string() + '\n\n\n')
    return data


def process_time_data(data, statistic, location_abbr):
    """Process the data fetched from the database as needed for a
    time-development plot requested by the front end.

    Args:
        data:  time-development data fetched from the database containing
            columns Year, Month, Death_count, and OD_type.  The death counts in
            this table correspond to the location specified by argument
            location_abbr.
        statistic:  the statistic that should be displayed in the plot (one of
            the strings 'death_count', 'normalized_death_count', or
            'percent_change')
        location_abbr: location abbreviation previously used to filter the data

    Returns:
        Dataframe with columns Year, Month, OD_type, and Value.  The statistic
        argument to the function determines what data is present in the Value
        column.  For example, if the argument is normalized_death_count, the
        Value column gives the number of deaths per UNIT_POPULATION.
    """
    if statistic == 'percent_change':
        return _find_percent_change_time_data(data)
    if statistic == 'normalized_death_count':
        return _normalize_time_data(data, location_abbr)
    if statistic == 'death_count':
        return data.rename(columns={'Death_count': 'Value'})

    message = ('Unable to process map data because the requested statistic '
               f'"{statistic}" is not recognized.')
    raise ValueError(message)


def _find_percent_change_time_data(data):
    # Create a modified copy of the data and then do a self join.  The modified
    # copy intentionally has the values in the Year column incremented by 1,
    # with the result that the death count corresponds to (year-1), where year
    # is the value of the incremented Year column.
    prior_year_data = (
        data.assign(Year=data['Year'] + 1)
        .set_index(['Year', 'Month', 'OD_type'])
        .rename(columns={'Death_count': 'Prior_death_count'})
    )
    data = data.join(prior_year_data, on=['Year', 'Month', 'OD_type'],
                     how='inner')
    data['Value'] = (
            (data['Death_count'] - data['Prior_death_count'])
            / data['Prior_death_count']
    )
    return data.drop(columns=['Death_count', 'Prior_death_count'])


def _normalize_time_data(data, location_abbr):
    """Normalize by population the death counts for the time-development plot.

    Args:
        data:  time-development data fetched from the database containing
            columns Year, Month, Death_count, and OD_type.  The death counts in
            this table correspond to the location specified by argument
            location_abbr.
        location_abbr: location abbreviation previously used to filter the data

    Returns:
        Dataframe with columns Year, Month, OD_type, and Value.  The Value
        column gives the number of deaths per UNIT_POPULATION.
    """
    population_data = (
        get_time_plot_populations(location_abbr)
        .set_index(['Year', 'Month'])
    )
    data = data.join(population_data, on=['Year', 'Month'], how='inner')
    data['Value'] = (
            data['Death_count'] * UNIT_POPULATION / data['Population']
    )
    return data.drop(columns=['Death_count', 'Population'])
