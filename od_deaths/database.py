"""Functions for using sqlalchemy to retrieving data from the app's sqlite
database."""
from flask import current_app, g
from sqlalchemy import create_engine


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


def init_app(app):
    """Initialize the current app instance for use with sqlalchemy."""
    url = 'sqlite:///' + str(app.config['DATABASE_PATH'])
    app.config['DATABASE_ENGINE'] = create_engine(url, future=True)
    app.teardown_appcontext(close_database_connection)
