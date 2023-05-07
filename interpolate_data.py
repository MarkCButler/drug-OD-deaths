"""Interpolate the annual population estimates obtained from www.census.gov.

Interpolation is needed in order to avoid spurious jumps in time-series plots
that show number of deaths per unit population.
"""
from datetime import datetime

import numpy as np
import pandas as pd

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

YEARS = [str(year) for year in range(2014, 2020)]


def interpolate_population_data(data):
    """Create a dataframe with interpolated population estimates.

    Args:
        data:  Dataframe with column Location_abbr and with columns '2014'
            through '2019'.  This is essentially the raw data loaded from the
            .csv file, but with the State column of the .csv file replaced by
            location abbreviations.
    Returns:
        Dataframe with columns Location_abbr, Year, Month, Population.
    """
    interpolation_dates = get_interpolation_dates()
    interpolated_data = create_interpolation_dataframe(interpolation_dates)
    interpolation_timestamps = [date['timestamp']
                               for date in interpolation_dates]
    measurement_timestamps = get_measurement_timestamps()

    data = data.set_index('Location_abbr')
    for abbr in data.index:
        measured_populations = data.loc[abbr, YEARS]
        interpolated_populations = np.round(np.interp(
            x=interpolation_timestamps,
            xp=measurement_timestamps,
            fp=measured_populations
        ))
        interpolated_data[abbr] = interpolated_populations.astype(np.int_)
    return _reshape_interpolated_data(interpolated_data)


def get_interpolation_dates():
    """Generate a list of dictionaries corresponding to months for which
    interpolated population data should be available.

    Each dictionary contains keys year, month, timestamp.  For example, the
    dictionary corresponding to January 2015 is
        {'year': 2015,
         'month': 'January',
         'timestamp': datetime.datetime(2015, 1, 1, 0, 0).timestamp()}
    """
    # Monthly dates range from January 2015 to September 2019.  Note that the
    # calls below to _get_date_dict use 0-based indexing for months.
    dates = [_get_date_dict(year, month)
             for year in range(2015, 2019)
             for month in range(12)]
    dates += [_get_date_dict(2019, month) for month in range(9)]
    # We want the database table of interpolated population data to include all
    # the population estimates downloaded from www.census.gov.  (This enables
    # the app to display the raw data used as input.)  So add the dictionary for
    # July 2014 to the front of the list.
    return [_get_date_dict(2014, 6)] + dates


def _get_date_dict(year, month):
    # Note that the month argument is a zero-based index, but the datetime
    # constructor uses a 1-based index for the month argument.
    return {'year': str(year),
            'month': MONTHS[month],
            'timestamp': datetime(year, month + 1, 1).timestamp()}


def create_interpolation_dataframe(interpolation_dates):
    """Return an empty dataframe that has a MultiIndex defined to correspond to
    the dates for which interpolated population data should be available.

    Args:
        interpolation_dates:  List of dictionaries in the format returned by
            get_interpolation_dates.  Each dictionary gives information about a
            date for which the population data should be interpolated.
    """
    tuples = [(date['year'], date['month']) for date in interpolation_dates]
    index = pd.MultiIndex.from_tuples(tuples, names=['Year', 'Month'])
    return pd.DataFrame(index=index)


def get_measurement_timestamps():
    """Generate a list of timestamps corresponding to dates for which population
    estimates (or "measurements") were provided by www.census.gov.
    """
    # Yearly population estimates were for July 1.
    return [datetime(year, 7, 1).timestamp()
            for year in range(2014, 2020)]


def _reshape_interpolated_data(data):
    # The interpolation was done in a loop over locations, and for each
    # location, a column of interpolated data was added to the dataframe.  For
    # example, the 'US' iteration of the loop caused a column named 'US' to be
    # added to the dataframe.  Reshape this dataframe to have columns Year,
    # Month, Location_abbr, Population.
    #
    # First convert the MultiIndex into columns Year, Month.  Strictly speaking,
    # we did not need a MultiIndex, and we could simply have defined columns
    # Year, Month when the dataframe was created.  But the structure of the
    # dataframe being populated within the loop was simpler with a MultiIndex,
    # because all columns corresponded to locations, and the MultiIndex
    # specified monthly dates.
    data = data.reset_index()
    return pd.melt(data,
                   id_vars=['Year', 'Month'],
                   var_name='Location_abbr', value_name='Population')
