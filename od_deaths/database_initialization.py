"""Define CLI commands that drop/recreate the table of derived data.

The tables created by the SQLite script create_tables.sql (stored in the repo
root) preserve in normalized form the data consumed by the app.

The CLI command initialize-database defined in the current module processes data
from these normalized tables and creates an additional table of derived data.
This table is created in order to simplify the processing performed by the app
in response to requests.

If the table of derived data already exists when initialize-database is
executed, the table is dropped and then recreated.  A separate CLI command
drop-derived-data simply drops the table of derived data.

These CLI commands provide support for a process that preserves data integrity
when the original data consumed by the app is updated:
    1.  Drop the table of derived data.
    2.  Update the normalized tables that remain, using constraints to preserve
        data integrity.
    3.  Recreate the table of derived data.
"""
import click
import pandas as pd
from sqlalchemy import text

from .data_interpolation import interpolate_population_data
from .database_connection import get_database_connection
from .date_formatting import ISO_MONTH_LABELS
from .ui_labels import UNIT_POPULATION

SQL_STRINGS = {
    'create_new_table': """
        CREATE TABLE derived_data (
          Location_abbr TEXT    NOT NULL,
          Location      TEXT    NOT NULL,
          Period        TEXT    NOT NULL,
          OD_type       TEXT    NOT NULL,
          Statistic     TEXT    NOT NULL,
          Value         NUMERIC NOT NULL,
          PRIMARY KEY (Location_abbr, Period, OD_type, Statistic),
          FOREIGN KEY (Location_abbr)
            REFERENCES locations (Abbr)
        );""",
    'delete_old_table': """
        DROP TABLE IF EXISTS derived_data;""",
    'get_dates': """
        SELECT DISTINCT Year, Month
        FROM death_counts;""",
    'get_joined_od_data': """
        SELECT
          od_data.Location_abbr,
          locations.Name AS Location,
          od_data.Year,
          od_data.Month,
          od_data.OD_type,
          od_data.Death_count
        FROM
          locations
            INNER JOIN (SELECT
                          death_counts.Location_abbr,
                          death_counts.Year,
                          death_counts.Month,
                          od_types.OD_type,
                          SUM(death_counts.Death_count) AS Death_count
                        FROM
                          death_counts
                            INNER JOIN od_types
                                       ON od_types.Indicator = death_counts.Indicator
                        GROUP BY death_counts.Location_abbr,
                                 death_counts.Year,
                                 death_counts.Month,
                                 od_types.OD_type) AS od_data
                       ON od_data.location_abbr = locations.Abbr;""",
    'get_population_data': """
        SELECT Location_abbr, Year, Population
        FROM populations;"""
}


@click.command()
def drop_derived_data():
    """Drop the table of derived data from the database if the table exists."""
    conn = get_database_connection()
    conn.execute(text(SQL_STRINGS['delete_old_table']))
    conn.commit()


@click.command()
def initialize_database():
    """Create / recreate the table of derived data used by the app.

    If the table already exists, it is dropped and then recreated.

    The table created / recreated has columns Location_abbr, Location, Date,
    OD_type, Statistic, Value.
    """
    create_empty_table()
    population_data = (
        get_interpolated_population_data()
        .set_index(['Location_abbr', 'Year', 'Month'])
    )
    derived_data = (
        _query_database(SQL_STRINGS['get_joined_od_data'])
        .join(population_data, on=['Location_abbr', 'Year', 'Month'],
              how='inner')
    )
    derived_data = reformat_dates(add_calculated_statistics(derived_data))
    write_derived_data(derived_data)


def create_empty_table():
    """Create an empty table of derived data.

     If the table already exists, it is dropped.
     """
    conn = get_database_connection()
    conn.execute(text(SQL_STRINGS['delete_old_table']))
    conn.execute(text(SQL_STRINGS['create_new_table']))
    conn.commit()


def get_interpolated_population_data():
    """Return a table of population data that includes interpolated values for
    all dates in the normalized table death_counts.

    Returns:
        Dataframe with columns Location_abbr, Year, Month, and Population
    """
    population_data = _query_database(SQL_STRINGS['get_population_data'])
    dates = _query_database(SQL_STRINGS['get_dates'])
    return interpolate_population_data(population_data, dates)


def add_calculated_statistics(data):
    """Update the table of derived data to include calculated statistics.

    The statistic present in the original data is the count of deaths.  The
    current function adds normalized death count (deaths per unit population)
    and percent change (in the death count as compared to the previous year).

    Returns:
        Dataframe with columns Location_abbr, Location, Year, Month, OD_type,
        Statistic, and Value
    """
    data = data.rename(columns={'Death_count': 'death_count'})
    to_apply = [_add_normalized_death_count, _add_percent_change,
                _reshape_derived_data]
    for func in to_apply:
        data = func(data)
    return data


def _add_normalized_death_count(data):
    data['normalized_death_count']= (
            data['death_count'] * UNIT_POPULATION / data['Population']
    )
    return data.drop(columns='Population')


def _add_percent_change(data):
    # Create a modified copy of the data and then do a self join.  The modified
    # copy intentionally has the values in the Year column incremented by 1,
    # with the result that the death count corresponds to (year-1), where year
    # is the value of the incremented Year column.
    prior_year_data = (
        data[['Location_abbr', 'Year', 'Month', 'OD_type', 'death_count']]
        .assign(Year=data['Year'] + 1)
        .set_index(['Location_abbr', 'Year', 'Month', 'OD_type'])
        .rename(columns={'death_count': 'prior_death_count'})
    )
    data = data.join(
        prior_year_data,
        on=['Location_abbr', 'Year', 'Month', 'OD_type'],
        how='left'
    )
    data['percent_change'] = (
            (data['death_count'] - data['prior_death_count'])
            / data['prior_death_count']
    )
    return data.drop(columns='prior_death_count')


def _reshape_derived_data(data):
    columns_to_keep = ['Location_abbr', 'Location', 'Year', 'Month', 'OD_type']
    return data.melt(id_vars=columns_to_keep,
                     var_name='Statistic',
                     value_name='Value')


def reformat_dates(data):
    """Add a table of ISO-format date strings to the table of derived data.

    The date strings have the form YYYY-MM, e.g. 2015-04.

    Returns:
        Dataframe with columns Location_abbr, Location, Date, OD_type,
        Statistic, and Value
    """

    def _get_iso_date_string(row):
        year = str(row['Year'])
        month = ISO_MONTH_LABELS[row['Month']]
        return year + '-' + month

    data['Period'] = data[['Year', 'Month']].apply(_get_iso_date_string, axis=1)
    return data.drop(columns=['Year', 'Month'])


def write_derived_data(data):
    """Write the table of derived data to the database."""
    # Rows with NA for the Value were created when the statistic
    # 'percent_change' was added to the dataframe, since percent change could
    # not be calculated for the first year of dates for which death counts are
    # available.  Drop these rows.
    data = data.dropna(axis='index', subset='Value')
    conn = get_database_connection()
    data.to_sql('derived_data', con=conn, if_exists='append', index=False)
    conn.commit()


def _query_database(sql_string):
    conn = get_database_connection()
    return pd.read_sql_query(text(sql_string), conn)
