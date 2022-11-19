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
- normalized table of populations, with columns Location_abbr, Year, Population.
- raw population data, with a Location column and a set of columns corresponding
    to distinct years.  This table is exposed solely for the purpose of showing
    the raw data used as input by the app.

Note that this data model is different from the schema used by the database.
"""
from flask import current_app, g
from pandas import pivot, read_sql_query
from sqlalchemy import create_engine, text

queries = {
    'all_od_deaths': text("""
       SELECT Location_abbr, Year, Month, Indicator, Death_count
       FROM death_counts;"""),
    'all_population_data': text("""
        SELECT Location_abbr, Year, Population
        FROM populations;"""),
    'location_names': text("""
        SELECT Abbr, Name
        FROM locations;"""),
    'map_data': None,
    'time_data': None
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
    function to be called when the application context end.

    Args:
        ex: unhandled exception, passed to the function if teardown_appcontext
            was called because of an unhandled exception.
    """
    conn = g.pop('database_connection', None)
    if conn is not None:
        conn.close()


def get_od_deaths_table():
    """Return a table of raw data on OD deaths as a dataframe.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = _get_expanded_table('all_od_deaths')
    columns = ['Location', 'Year', 'Month', 'Indicator', 'Death_count']
    return data[columns].rename(columns={'Death_count': 'Death count'})


def get_population_table():
    """Return a table of raw population data as a dataframe.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = _get_expanded_table('all_population_data')
    columns = ['Location', 'Year', 'Population']
    # Reshape the table to reproduce the original form of the raw data.
    return pivot(data[columns], index='Location', columns='Year',
                 values='Population')


def _get_expanded_table(query_key):
    query = queries[query_key]
    conn = get_database_connection()
    data = (
        _add_location_names(read_sql_query(query, conn))
        .rename(columns={'Abbr': 'Location_abbr'})
    )
    return data


def _add_location_names(data):
    """Add a column giving the full name of each location in the table of drug
    OD deaths.

    Used to make the user interface friendlier, e.g., by including the full
    state name in the hover text of plotly maps.
    """
    query = queries['location_names']
    conn = get_database_connection()
    state_names = (
        read_sql_query(query, conn, index_col='Abbr')
        .rename(columns={'Name': 'Location'})
    )
    return data.join(state_names, on='Location_abbr')
