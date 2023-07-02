"""Interpolate the annual population estimates obtained from www.census.gov.

Interpolation is needed in order to avoid spurious jumps in time-series plots
that show number of deaths per unit population.
"""
from datetime import datetime

import numpy as np
import pandas as pd

from .date_formatting import MONTH_NUMBERS, ORDERED_MONTHS


def interpolate_population_data(population_data, dates):
    """Create a dataframe with interpolated population estimates.

    Args:
        population_data:  Dataframe with columns Location_abbr, Year, and
            Population corresponding to the original population data from
            www.census.gov
        dates:  Dataframe with columns Year, Month giving the dates for which
            population estimates are needed

    Returns:
        Dataframe of interpolated data with columns Location_abbr, Year, Month,
        and Population
    """
    dates, timestamps = prepare_interpolation_dates(dates)
    population_data, data_timestamps = prepare_population_data(population_data)
    # Create an empty dataframe that has a MultiIndex corresponding to year and
    # month for each interpolation date.
    interpolated_data = dates.set_index(['Year', 'Month'])
    for location in population_data.index:
        location_populations = population_data.loc[location]
        interpolation = np.round(np.interp(
            x=timestamps,
            xp=data_timestamps,
            fp=location_populations
        ))
        interpolated_data[location] = interpolation.astype(np.int_)
    return _reshape_interpolated_data(interpolated_data)


def prepare_interpolation_dates(dates):
    """Sort the rows of a dataframe by increasing data and generate a pandas
    Series of timestamps corresponding to the sorted dates.

    Args:
        dates:  Dataframe containing columns Year and Month

    Returns:
        Tuple (dates, timestamps)
          - dates is the function argument modified to have rows sorted by
              increasing date
          - timestamps is a pandas Series of timestamps corresponding to the
              sorted dates
    """
    dates = sort_chronologically(dates)
    return dates, get_timestamps(dates)


def sort_chronologically(data):
    """Sort the rows of a dataframe by date, where date is specified by a
    year-month combination.

    Args:
        data:  Dataframe containing columns Year and Month (possibly in addition
            to other columns)

    Returns:
        The function argument modified to have rows sorted by increasing date
    """
    data['Month'] = pd.Categorical(data['Month'],
                                   categories=ORDERED_MONTHS,
                                   ordered=True)
    data = data.sort_values(by=['Year', 'Month'])
    return data.assign(Month=data['Month'].astype(str))


def get_timestamps(data):
    """Generate a pandas Series containing timestamps that correspond to dates
    in a dataframe.

    Args:
        data:  Dataframe containing columns Year and Month (possibly in addition
            to other columns).  Each year-month combination is used to generate
            a timestamp.

    Returns:
        Series of timestamps
    """
    def _get_timestamp(row):
        year = row['Year']
        month_number = MONTH_NUMBERS[row['Month'].lower()]
        return datetime(year, month_number, 1).timestamp()

    return data[['Year', 'Month']].apply(_get_timestamp, axis=1)


def prepare_population_data(data):
    """Return a reshaped dataframe of population data along with timestamps for
    the population estimates.

    Args:
        data:  Dataframe with columns Location_abbr, Year, and Population
            corresponding to the original population data from www.census.gov

    Returns:
        Tuple (data, timestamps)
          - data is the function argument reshaped to have all population data
              for a given location in one row.  The columns are ordered by
              increasing data.
          - timestamps is an iterable of timestamps corresponding to the
              population estimates in the original data
    """
    # Pivot the data to have all population data for a given location in one
    # row.
    data = pd.pivot(data, index='Location_abbr', columns='Year',
                    values='Population')
    # Ensure that the columns of the dataframe are sorted, since rows of data
    # will be used in the interpolation process.
    data = data.sort_index(axis='columns')
    timestamps = [datetime(int(year), 7, 1).timestamp()
                  for year in data.columns]
    return data, timestamps


def _reshape_interpolated_data(data):
    # The interpolation was done in a loop over locations, and for each
    # location, a column of interpolated data was added to the dataframe.  For
    # example, the 'US' iteration of the loop caused a column named 'US' to be
    # added to the dataframe.  Reshape this dataframe to have columns Year,
    # Month, Location_abbr, Population.
    #
    # First convert the existing MultiIndex with levels Year, Month into columns
    # Year, Month in order to facilitate the process of reshaping the dataframe.
    #
    # Note that strictly speaking, we did not need a MultiIndex while adding
    # columns of interpolated data.  We could simply have defined columns Year,
    # Month when the dataframe was created.  But the structure of the dataframe
    # being populated within the loop was more natural with a MultiIndex,
    # because all columns corresponded to locations, and the MultiIndex
    # specified monthly dates.
    data = data.reset_index()
    return pd.melt(data, id_vars=['Year', 'Month'],
                   var_name='Location_abbr', value_name='Population')
