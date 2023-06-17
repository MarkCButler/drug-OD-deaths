"""Override the app's default development settings.

This module defines a set of key-value pairs that can override the app's default
settings.  For example, if the environment variable

OD_DEATHS_APP_SETTINGS

is defined to contain the path to the current file, the function call

app.config.from_envvar('OD_DEATHS_APP_SETTINGS')

will override the app's default settings with those defined in the current
module.
"""
DATABASE_PATH = '/app/data/OD-deaths.sqlite'
ECHO_SQL = False
