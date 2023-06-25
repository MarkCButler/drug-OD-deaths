"""Functions for using sqlalchemy to retrieving data from the app's sqlite
database.

The functions in this module understand the details of the database and provide
an API that hides most of those details from other modules.

The data model exposed to other modules by the current module consists of the
following tables:
- table of processed data on OD deaths containing columns Location_abbr,
    Location, Period, OD_type, Statistic, and Value.
- table of locations containing columns Abbr and Name
- raw data on OD deaths containing columns Location, Year, Month, Indicator, and
    Death count.  This table is exposed solely for the purpose of displaying the
    raw data used as input by the app.
- raw population data containing a Location column and a set of columns
    corresponding to distinct years.  This table is exposed solely for the
    purpose of displaying the raw data used as input by the app.

Note that this data model is different from the schema used by the database.

The tables returned by API functions of this module are in the form of pandas
dataframes.
"""
from pandas import pivot, read_sql_query
from sqlalchemy import text

from .database_connection import get_database_connection

SQL_STRINGS = {
    'raw_od_deaths_data': """
        SELECT
          locations.Name AS Location,
          death_counts.Year,
          death_counts.Month,
          death_counts.Indicator,
          death_counts.Death_count AS "Death count"
        FROM
          death_counts
            INNER JOIN locations
                       ON locations.Abbr = death_counts.Location_abbr;""",
    'raw_population_data': """
        SELECT
          locations.Name AS Location,
          populations.Year,
          populations.Population
        FROM
          populations
            INNER JOIN locations
                       ON locations.Abbr = populations.Location_abbr;""",
    'location_names': """
        SELECT Abbr, Name
        FROM locations;""",
    'map_plot_data': """
        SELECT
          Location_abbr,
          Location,
          Value
        FROM
          derived_data
        WHERE Location_abbr != 'US'
          AND OD_type = 'all_drug_od'
          AND Period = :period
          AND Statistic = :statistic;""",
    # Note that the parameter :od_types in the next entry will be
    # programmatically replaced by a series of the form
    #
    # :od_type_0, :od_type_1, ...
    #
    # This is needed because sqlite3 does not support binding a series as a
    # parameter.
    'time_plot_data': """
        SELECT
          Period,
          OD_type,
          Value
        FROM
          derived_data
        WHERE Location_abbr = :location_abbr
          AND Statistic = :statistic
          AND OD_type IN (:od_types);""",
    'od_types': """
        SELECT DISTINCT OD_type
        FROM derived_data
        WHERE Location_abbr = :location_abbr;""",
    'map_plot_periods': """
        SELECT DISTINCT
          Period,
          Statistic
        FROM
          derived_data
        WHERE OD_type = 'all_drug_od'
          AND Statistic IN ('death_count', 'percent_change');"""
}


def execute_initialization_query(app, query_function, **kwargs):
    """Execute a database query during app initialization.

    Database queries defined in the current module use functions from the
    database_connection module to manage the database connection.  These
    functions require an application context to be defined. An application
    context is defined automatically by flask during a request, but in order to
    perform a database query outside a request, an application context must be
    manually created.

    The current function creates an application context, then executes the
    function given by argument query_function, and then closes the application
    context.

    Args:
        app:  Instance of the application
        query_function:  Any of the API functions defined in the current module
            that perform a database query.  The corresponding query is
            performed, and the results are returned.
        kwargs:  Dictionary of keyword arguments to pass when calling the
            function given by argument query_function

    Returns:
        The return value of query_function
    """
    with app.app_context():
        return query_function(**kwargs)


def get_map_plot_data(statistic, period):
    """Return a table giving the number of OD deaths per state in a given
    period.

    Data from the table of processed data is returned, with
    OD_type='all_od_deaths' and with Statistic and Period equal to the
    corresponding function arguments.

    Note that the arguments statistic and parameter should be present in the
    corresponding columns of the table of processed data, since these arguments
    are used as filters in querying the database.

    Args:
        statistic:  Statistic used in filtering the data.  Allowed values:
            death_count, normalized_death_count, or percent_change.
        period:  Time period used in filtering the data.  Values are year-month
            combinations in ISO format, e.g., 2015-01.

    Returns:
        Table with columns Location_abbr, Location, and Value
    """
    return _perform_query(
        query=text(SQL_STRINGS['map_plot_data']),
        params={'statistic': statistic, 'period': period},
    )


def get_time_plot_data(location_abbr, statistic, od_types):
    """Return a table giving the number of OD deaths in a given location as a
    function of time.

    Data from the table of processed data is returned, with Location_abbr and
    Statistic equal to the corresponding function arguments, and with OD_type
    equal to any of the values given by the argument od_types.

    Note that the arguments location_abbr and statistic, along with any values
    included in the argument od_types, should be present in the corresponding
    columns of the table of processed data, since these arguments are used as
    filters in querying the database.

    Args:
        location_abbr:  Location abbreviation used in filtering the data.
            Values are two-letter abbreviations such as US or CA.
        statistic:  Statistic used in filtering the data. Allowed values:
            death_count, normalized_death_count, or percent_change.
        od_types:  String or list of strings used in filtering the data.
            Allowed values:  all_drug_od, all_opioids, prescription_opioids,
            synthetic_opioids, heroin, cocaine, or other_stimulants.

    Returns:
        Table with columns Period, OD_type, and Value
    """
    query, params = _get_time_query_and_params(location_abbr, statistic,
                                               od_types)
    return _perform_query(query=query, params=params)


def _get_time_query_and_params(location_abbr, statistic, od_types):
    query_string = SQL_STRINGS['time_plot_data']
    # Special handling is needed because od_types may be a list of strings.
    # SQLAlchemy supports binding a series parameter using the following
    # commands:
    #
    # from sqlalchemy import bindparam
    # query = text(query_string)
    # query.bindparams(bindparam('od_types', expanding=True))
    #
    # However, a test of these commands yielded an error from the driver
    # sqlite3, which does not support binding a series as a parameter.  Instead,
    # modify the query string to include parameters od_type_0, od_type_1, etc.
    if isinstance(od_types, str):
        od_types = [od_types]
    numbered_od_types = [f':od_type_{index}'
                         for index in range(len(od_types))]
    query_string = query_string.replace(
        ':od_types',
        ', '.join(numbered_od_types)
    )
    params = {f'od_type_{index}': od_type
              for index, od_type in enumerate(od_types)}
    params.update({
        'location_abbr': location_abbr,
        'statistic': statistic
    })
    return text(query_string), params


def get_map_plot_periods():
    """Return a table of periods that can be selected for the map plot that
    shows the distribution of OD deaths in the US.

    Returns:
        Dataframe with the following index and column:
          - index (named Period) containing ISO-format date strings (e.g.,
              2015-01) representing periods that can be selected
          - column Includes_percent_change containing booleans that indicate
              whether the percent change in OD deaths during the previous year
              is available for that period
    """
    data = _perform_query(
        query=text(SQL_STRINGS['map_plot_periods']),
    )
    all_periods = (
        data.loc[data['Statistic'] == 'death_count', ['Period']]
        .set_index('Period')
    )
    periods_with_percent_change = (
        data.loc[data['Statistic'] == 'percent_change', ['Period']]
        .set_index('Period')
        .assign(Includes_percent_change=True)
    )
    return (
        all_periods.join(periods_with_percent_change, on='Period', how='left')
        .fillna(value=False)
    )


def get_location_table():
    """Return a table of locations for which data on OD deaths in available.

    The table gives both the full name of each location ('Name') and an
    abbreviation ('Abbr').  The abbreviation is set as the index.
    """
    query = text(SQL_STRINGS['location_names'])
    conn = get_database_connection()
    return read_sql_query(query, conn, index_col='Abbr')


def get_od_types_for_location(location_abbr):
    """Return a list of the types of OD deaths stored in the database for a
    given location.

    Args:
        location_abbr:  Location abbreviation used in filtering the data.  This
            value should be present in the Location_abbr column of the table of
            processed data.  Values are two-letter abbreviations such as US or
            CA.

    Returns:
        List of strings, each a value in the OD_type column in the table of OD
        deaths
    """
    data = _perform_query(
        query=text(SQL_STRINGS['od_types']),
        params={'location_abbr': location_abbr}
    )
    return data['OD_type'].tolist()


def get_raw_od_deaths_table():
    """Return a table of raw data on OD deaths as a dataframe.

    Returns:
        Table representing a subset of the raw data with some column names
        changed to improve readability.  After renaming, the column names are
        Location, Year, Month, Indicator, and Death count.
    """
    return _perform_query(
        query=text(SQL_STRINGS['raw_od_deaths_data'])
    )


def get_raw_population_table():
    """Return a table of raw population data as a dataframe.

    Returns:
        Table representing a subset of the raw data with one column name changed
        to improve readability.  The column names are Location, 2014, 2015, ...,
        2020.
    """
    data = _perform_query(
        query=text(SQL_STRINGS['raw_population_data'])
    )
    # Reshape the table to reproduce the original form of the raw data.
    data = (
        pivot(data, index='Location', columns='Year', values='Population')
        .reset_index()
    )
    # In the reshaped dataframe, the set of columns confusingly is named 'Year',
    # and this shows up when the dataframe is converted to an HTML table.
    data.columns.name = None
    return data


def _perform_query(query, params=None):
    """Query the database and return the result as a dataframe.

    Args:
        query:  sqlalchemy.sql.expression.TextClause object representing the SQL
            query
        params:  Dictionary of parameters to bind to the query
    """
    conn = get_database_connection()
    return read_sql_query(query, conn, params=params)
