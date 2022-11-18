"""Functions for using sqlalchemy to retrieving data from the app's sqlite
database."""
from flask import current_app, g
from pandas import read_sql_query
from sqlalchemy import create_engine, text

queries = {
    'all_od_deaths': text("""
       SELECT State, Year, Month, Indicator, Value
       FROM death_counts;"""),
    'state_names': text("""
        SELECT State, Name
        FROM states;"""),
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
    """Return the table of data on OD deaths as a dataframe."""
    query = queries['all_od_deaths']
    conn = get_database_connection()
    data = _add_state_names(read_sql_query(query, conn))
    columns = ['Name', 'Year', 'Month', 'Indicator', 'Value']
    data = data[columns]
    mapper = {'Name': 'Location',
              'Value': 'Death count'}
    return data.rename(mapper=mapper, axis='columns')


def _add_state_names(data):
    """Add a column giving the full name of each location in the table of drug
    OD deaths.

    Used to make the user interface friendlier, e.g., by including the full state
    name in the hover text of plotly maps.
    """
    query = queries['state_names']
    conn = get_database_connection()
    state_names = read_sql_query(query, conn, index_col='State')
    return data.join(state_names, on='State')
