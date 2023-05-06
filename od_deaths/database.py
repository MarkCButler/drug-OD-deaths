"""Functions for using sqlalchemy to retrieving data from the app's sqlite
database.

The functions in this module understand the details of the database and should
hide those details from other modules.

The data model exposed to other modules by the current module consists of the
following tables:
- table of OD deaths, with columns Location, Location_abbr, Year, Month,
    Indicator, Death_count, OD_type.  The OD_type column is a calculated column
    that groups together different values of Indicator for the purpose of
    placing OD deaths in relatively simple categories.  The Location column
    gives the full name of a location, while Location_abbr gives an abbreviation
    for the location.
- table of locations, with columns Abbr, Name.
- normalized table of populations, with columns Location_abbr, Year, Population.
- raw population data, with a Location column and a set of columns corresponding
    to distinct years.  This table is exposed solely for the purpose of showing
    the raw data used as input by the app.

Note that this data model is different from the schema used by the database.

The tables returned by API functions of this module are in the form of pandas
dataframes.
"""
from flask import current_app, g
from pandas import pivot, read_sql_query
from sqlalchemy import create_engine, text

# The first and last dates for which data is available in the table of OD deaths
# are January 2015 and September 2019, respectively.
DATASET_START_YEAR = 2015
DATASET_END_YEAR = 2019

QUERY_STRINGS = {
    'all_od_deaths': """
       SELECT Location_abbr, Year, Month, Indicator, Death_count
       FROM death_counts;""",
    'all_population_data': """
        SELECT Location_abbr, Year, Population
        FROM populations;""",
    'location_names': """
        SELECT Abbr, Name
        FROM locations;""",
    'map_data': """
        SELECT Location_abbr, Death_count
        FROM death_counts
        WHERE Location_abbr != 'US'
          and YEAR = :year
          and Month = :month
          and OD_type = 'all_drug_od';""",
    # Note that the parameter :od_types in the next entry will be
    # programmatically replaced by a series of the form
    #
    # :od_type_0, :od_type_0, ...
    #
    # This is needed because sqlite3 does not support binding a series as a
    # parameter.
    'time_data': """
        SELECT Location_abbr, Year, Month, Death_count, OD_type
        FROM death_counts
        WHERE Location_abbr = :location_abbr
          and OD_type IN (:od_types);""",
    'od_types': """
    SELECT DISTINCT OD_type
    FROM death_counts
    WHERE Location_abbr = :location_abbr;"""
}


def init_app(app):
    """Initialize the current app instance for use with sqlalchemy."""
    url = 'sqlite:///' + str(app.config['DATABASE_PATH'])
    # Each instance of the app gets its own SQLAlchemy engine.
    # TODO: Set the echo parameter to true automatically in development mode
    app.config['DATABASE_ENGINE'] = create_engine(url, future=True, echo=True)
    app.teardown_appcontext(close_database_connection)


def get_database_connection():
    """Return a database connection scoped to the current request."""
    if 'database_connection' not in g:
        engine = current_app.config['DATABASE_ENGINE']
        g.database_connection = engine.connect()
    return g.database_connection


def close_database_connection(ex=None):        # pylint: disable=unused-argument
    """Close the database connection for the current request.

    When the app is created, flask.teardown_appcontext is used to register this
    function to be called when the application context ends.

    Args:
        ex: unhandled exception, passed to the function if teardown_appcontext
            was called because of an unhandled exception.
    """
    conn = g.pop('database_connection', None)
    if conn is not None:
        conn.close()


def get_map_data(month, year, add_location_names):
    """Return a table giving the number of OD deaths per state in a given
    period.

    Args:
        month: month (full name) used in filtering the data
        year: year (4-digit integer) used in filtering the data
        add_location_names:  boolean indicating whether a column of location
            names should be included in the table.  If add_location_names=False,
            the returned table has column Location_abbr but not column Location.

    Data from the table of OD deaths is returned, with OD_type='all_od_deaths'
    and with Month and Year given by the function arguments.

    The returned table has columns Location_abbr, Location (if argument
    add_location_names=True), Year, Month, Death_count.  The Indicator and
    OD_type columns of the table of OD deaths documented in the module docstring
    are not returned.
    """
    return _perform_query(
        query=text(QUERY_STRINGS['map_data']),
        params={'month': month, 'year': year},
        add_location_names=add_location_names,
    )


def get_time_data(location_abbr, od_types, add_location_names):
    """Return a table giving the number of OD deaths in a given location as a
    function of time.

    Args:
        location_abbr: location abbreviation used in filtering the data
        od_types: string or list of strings used in filtering the data
        add_location_names:  boolean indicating whether a column of location
            names should be included in the table.  If add_location_names=False,
            the returned table has column Location_abbr but not column Location.

    Data from the table of OD deaths is returned, with Location_abbr given by
    the argument location_abbr, and with the data filtered so that OD_type
    includes only the value(s) given by argument od_types.

    The returned table has columns Location_abbr, Location (if argument
    add_location_names=True), Year, Month, Death_count, OD_type.  The Indicator
    column of the table of OD deaths documented in the module docstring is not
    returned.
    """
    query, params = _get_time_query_and_params(location_abbr, od_types)
    return _perform_query(query=query, params=params,
                          add_location_names=add_location_names)


def _get_time_query_and_params(location_abbr, od_types):
    query_string = QUERY_STRINGS['time_data']
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
    param_dict = {f'od_type_{index}': element
                  for index, element in enumerate(od_types)}
    param_dict['location_abbr'] = location_abbr
    return text(query_string), param_dict


def get_location_od_types(location_abbr):
    """Return a list of the types of OD deaths stored in the database for a
    given location.

    Args:
        location_abbr: location abbreviation used in filtering the data
    Returns:
        List of strings, each a value in the OD_type column in the table of OD
        deaths
    """
    data = _perform_query(
        query=text(QUERY_STRINGS['od_types']),
        params={'location_abbr': location_abbr},
        add_location_names=False,
    )
    return data['OD_type'].tolist()


def get_od_deaths_table():
    """Return a table of raw data on OD deaths as a dataframe.

    The table is a subset of the raw data with some column names changed to
    improve readability.  After renaming, the column names are 'Location',
    'Year', 'Month', 'Indicator', and 'Death count'.
    """
    data = _perform_query(
        query=text(QUERY_STRINGS['all_od_deaths'])
    )
    columns = ['Location', 'Year', 'Month', 'Indicator', 'Death_count']
    return data[columns].rename(columns={'Death_count': 'Death count'})


def get_raw_population_table():
    """Return a table of raw population data as a dataframe.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = _perform_query(
        query=text(QUERY_STRINGS['all_population_data'])
    )
    columns = ['Location', 'Year', 'Population']
    # Reshape the table to reproduce the original form of the raw data.
    data = (
        pivot(data[columns], index='Location', columns='Year',
              values='Population')
        .reset_index()
    )
    # In the reshaped dataframe, the set of columns confusingly is named 'Year',
    # and this shows up when the dataframe is converted to an HTML table.
    data.columns.name = None
    return data


def _perform_query(query, params=None, add_location_names=True):
    """Query the database and return the result as a dataframe.

    Args:
        query:  sqlalchemy.sql.expression.TextClause object representing the SQL
            query
        params:  dictionary of parameters to be bound to the query
        add_location_names:  boolean indicating whether a column of location
            names should be added to the table.  If add_location_names=False,
            the returned table has column Location_abbr but not column Location.
    """
    conn = get_database_connection()
    data = read_sql_query(query, conn, params=params)
    if add_location_names:
        data = _add_location_names(data)
    return data


def _add_location_names(data):
    """Add a column giving the full name of each location in the table of drug
    OD deaths.

    Used to make the user interface friendlier, e.g., by including the full
    state name in the hover text of plotly maps.
    """
    state_names = (
        get_location_table()
        .rename(columns={'Name': 'Location'})
    )
    return data.join(state_names, on='Location_abbr')


def get_location_table():
    """Return a table of locations for which data on OD deaths in available.

    The table gives both the full name of each location ('Name') and an
    abbreviation ('Abbr').  The abbreviation is set as the index.
    """
    query = text(QUERY_STRINGS['location_names'])
    conn = get_database_connection()
    return read_sql_query(query, conn, index_col='Abbr')
