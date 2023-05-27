"""Functions for using sqlalchemy to retrieving data from the app's sqlite
database.

The functions in this module understand the details of the database and should
hide those details from other modules.

The data model exposed to other modules by the current module consists of the
following tables:
- table of OD deaths containing columns Location, Location_abbr, Year, Month,
    Indicator, Death_count, and OD_type.  The OD_type column is a calculated
    column that groups together different values of Indicator for the purpose of
    placing OD deaths in relatively simple categories.  The Location column
    gives the full name of a location, while Location_abbr gives an abbreviation
    for the location.
- table of locations containing columns Abbr and Name
- table of interpolated population data containing columns Location_abbr, Year,
    Month, and Population.  (Linear interpolation is used to give monthly
    populations estimates, starting from yearly population estimates from
    www.census.gov.)
- raw population data containing a Location column and a set of columns
    corresponding to distinct years.  This table is exposed solely for the
    purpose of showing the raw data used as input by the app.

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

# In the queries below, the OD_type column of the od_types table is considered
# part of the "programmer's interface" to the database, since this column
# contains short, simple strings used in the app code.  As a result, data is
# consistently filtered by OD_type rather than by Indicator.
QUERY_STRINGS = {
    'od_deaths_table': """
        SELECT locations.Name AS Location,
               death_counts.Year,
               death_counts.Month,
               death_counts.Indicator,
               death_counts.Death_count AS "Death count"
        FROM death_counts
               INNER JOIN locations ON locations.Abbr = death_counts.Location_abbr;""",
    'raw_population_data': """
        SELECT locations.Name AS Location,
               populations.Year,
               populations.Population
        FROM populations
               INNER JOIN locations ON locations.Abbr = populations.Location_abbr
        WHERE populations.Month = 'July';""",
    'location_names': """
        SELECT Abbr, Name
        FROM locations;""",
    'map_plot_death_counts': """
        SELECT death_counts.Location_abbr,
               death_counts.Death_count
        FROM death_counts
               INNER JOIN (SELECT Indicator, OD_type
                           FROM od_types
                           WHERE OD_type = 'all_drug_od') AS overdose_types
                          ON overdose_types.Indicator = death_counts.Indicator
        WHERE death_counts.Location_abbr != 'US'
          AND death_counts.Year = :year
          AND death_counts.Month = :month;""",
    'map_plot_populations': """
        SELECT Location_abbr,
               Population
        FROM populations
        WHERE Location_abbr != 'US'
          AND Year = :year
          AND Month = :month;""",
    # Note that the parameter :od_types in the next entry will be
    # programmatically replaced by a series of the form
    #
    # :od_type_0, :od_type_1, ...
    #
    # This is needed because sqlite3 does not support binding a series as a
    # parameter.
    'time_plot_death_counts': """
        SELECT death_counts.Year,
               death_counts.Month,
               death_counts.Death_count,
               overdose_types.OD_type
        FROM death_counts
               INNER JOIN (SELECT Indicator, OD_type
                           FROM od_types
                           WHERE OD_type IN (:od_types)) as overdose_types
                          ON overdose_types.Indicator = death_counts.Indicator
        WHERE death_counts.Location_abbr = :location_abbr;""",
    'time_plot_populations': """
        SELECT Year,
               Month,
               Population
        FROM populations
        WHERE Location_abbr = :location_abbr;""",
    'od_types': """
        SELECT DISTINCT od_types.OD_type
        FROM od_types
               INNER JOIN death_counts ON death_counts.Indicator = od_types.Indicator
        WHERE death_counts.Location_abbr = :location_abbr;"""
}


def initialize_database(app):
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


def execute_initialization_query(app, query_function, **kwargs):
    """Execute a database query during app initialization.

    Database queries defined in the current module use the functions
    get_database_connection and close_database_connection to manage the database
    connection.  These functions require an application context to be defined.
    An application context is defined automatically by flask during a request,
    but in order to perform a database query outside a request, an application
    context must be manually created.

    The current function creates an application context, then executes the
    function given by argument query_function, and then closes the application
    context.

    Args:
        app:  instance of the application
        query_function:  any of the API functions defined in the current module
            that performs a database query.  The corresponding query is
            performed, and the results are returned.
        kwargs:  dictionary of keyword arguments to pass when calling the
            function given by argument query_function

    Returns:
        Dataframe containing the query results returned by the database
    """
    with app.app_context():
        return query_function(**kwargs)


def get_map_plot_death_counts(month, year, add_location_names):
    """Return a table giving the number of OD deaths per state in a given
    period.

    Data from the table of OD deaths is returned, with OD_type='all_od_deaths'
    and with Month and Year equal to the corresponding function arguments.

    Args:
        month: month (full name) used in filtering the data
        year: year (4-digit integer) used in filtering the data
        add_location_names:  boolean indicating whether a column of location
            names should be included in the table.  If add_location_names=False,
            the returned table has column Location_abbr but not column Location.

    Returns:
        Table with columns Location_abbr, Location (if argument
        add_location_names=True), and Death_count
    """
    data = _perform_query(
        query=text(QUERY_STRINGS['map_plot_death_counts']),
        params={'month': month, 'year': year},
    )
    if add_location_names:
        data = _add_location_names(data)
    return data


def get_map_plot_populations(month, year):
    """Return a table giving the interpolated population of each state for a
    given month and year.

    Args:
        month: month (full name) used in filtering the data
        year: year (4-digit integer) used in filtering the data

    Returns:
        Table with columns Location_abbr and Population
    """
    return _perform_query(
        query=text(QUERY_STRINGS['map_plot_populations']),
        params={'month': month, 'year': year}
    )


def get_time_plot_death_counts(location_abbr, od_types):
    """Return a table giving the number of OD deaths in a given location as a
    function of time.

    Data from the table of OD deaths is returned, with Location_abbr equal to
    the argument location_abbr, and with the data filtered so that OD_type
    includes only the value(s) given by argument od_types.

    Args:
        location_abbr: location abbreviation used in filtering the data
        od_types: string or list of strings used in filtering the data

    Returns:
        Table with columns Year, Month, Death_count, and OD_type.
    """
    query, params = _get_time_query_and_params(location_abbr, od_types)
    return _perform_query(query=query, params=params)


def _get_time_query_and_params(location_abbr, od_types):
    query_string = QUERY_STRINGS['time_plot_death_counts']
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


def get_time_plot_populations(location_abbr):
    """Return a table giving the interpolated populations of a given location
    for all available time periods.

    Args:
        location_abbr: location abbreviation used in filtering the data

    Returns:
        Table with columns Year, Month, and Population
    """
    return _perform_query(
        query=text(QUERY_STRINGS['time_plot_populations']),
        params={'location_abbr': location_abbr}
    )


def get_od_types_for_location(location_abbr):
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
        params={'location_abbr': location_abbr}
    )
    return data['OD_type'].tolist()


def get_od_deaths_table():
    """Return a table of raw data on OD deaths as a dataframe.

    The table is a subset of the raw data with some column names changed to
    improve readability.  After renaming, the column names are 'Location',
    'Year', 'Month', 'Indicator', and 'Death count'.
    """
    return _perform_query(
        query=text(QUERY_STRINGS['od_deaths_table'])
    )


def get_raw_population_table():
    """Return a table of raw population data as a dataframe.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = _perform_query(
        query=text(QUERY_STRINGS['raw_population_data'])
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
        params:  dictionary of parameters to bind to the query
    """
    conn = get_database_connection()
    return read_sql_query(query, conn, params=params)


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
    return data.join(state_names, on='Location_abbr', how='inner')


def get_location_table():
    """Return a table of locations for which data on OD deaths in available.

    The table gives both the full name of each location ('Name') and an
    abbreviation ('Abbr').  The abbreviation is set as the index.
    """
    query = text(QUERY_STRINGS['location_names'])
    conn = get_database_connection()
    return read_sql_query(query, conn, index_col='Abbr')
