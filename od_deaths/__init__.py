"""App factory that generates instances of the app."""
import os
from pathlib import Path

from flask import Flask, render_template

from .database_connection import initialize_connection_pool
from .database_initialization import drop_derived_data, initialize_database
from .form_options import option_views
from .html_headings import heading_views
from .html_tables import table_views
from .interface_labels import (
    get_locations, get_od_types, get_preset_plot_params, get_statistic_types,
    get_time_periods, initialize_interface, MAP_PLOT_PARAM_NAMES,
    TIME_PLOT_PARAM_NAMES, UNIT_POPULATION_LABEL
)
from .plots import plot_views
from .template_data import URLS


def get_static_folder():
    """Return the path to the app's static folder, i.e., the folder where the
    app expects static files such as CSS files to be found.

    The default path (relative to od_deaths, the root directory of the
    application) is '../static'.  If the environment variable
    OD_DEATHS_APP_STATIC_FOLDER is defined, its value is used as the path to the
    static folder.
    """
    static_folder = os.environ.get('OD_DEATHS_APP_STATIC_FOLDER')
    if not static_folder:
        static_folder = '../static'
    return static_folder


def load_configuration(app):
    """Load the app's configuration.

    A default configuration is first loaded.  This configuration is modified in
    two consecutive steps:
      - Environment variables that start with the prefix FLASK_ are added to the
          configuration, with the prefix dropped.  If the environment variable
          FLASK_ECHO_SQL is defined, for instance, then the app's config
          variable ECHO_SQL is set to the value of that variable.  The flask
          function from_prefixed_env attempts to convert values to more specific
          types than strings.
      - If the environment variable OD_DEATHS_APP_SETTINGS is defined, its value
          should be the path to a configuration file.  App settings are loaded
          from that configuration file.

    Note that each step can override previously defined configuration values.
    """
    # Default configuration.
    app.config.from_mapping(
        DATABASE_PATH=Path(app.root_path).parent / 'data' / 'OD-deaths.sqlite',
        ECHO_SQL=True,
        CLI_MODE=False
    )
    # Override from environment variables.
    app.config.from_prefixed_env()
    # Override from a configuration file if environment variable
    # OD_DEATHS_APP_SETTINGS is defined.
    if os.environ.get('OD_DEATHS_APP_SETTINGS'):
        app.config.from_envvar('OD_DEATHS_APP_SETTINGS')


def register_blueprints(app, blueprints):
    """Register a sequence of blueprints on the app.

    Args:
        app:  Application on which blueprints will be registered
        blueprints:  Iterable of blueprints, each of which will be registered on
            the application
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def register_cli_commands(app):
    """Register the app's CLI commands.

    The app's CLI commands can be used to drop/recreate the table of derived
    data, e.g., in connection with an update to the external data consumed by
    the app.
    """
    app.cli.add_command(drop_derived_data)
    app.cli.add_command(initialize_database)


def create_app():
    """Generate an instance of the app."""
    app = Flask(__name__, static_folder=get_static_folder())
    load_configuration(app)

    initialize_connection_pool(app)

    if app.config['CLI_MODE']:
        register_cli_commands(app)

        # The app CLI is used to initialize the database.  In this mode, the app
        # responds to HTTP requests with a simple warning page.
        @app.route('/')
        def index():
            return render_template('cli-mode.html')

    else:
        register_blueprints(
            app, [heading_views, option_views, plot_views, table_views]
        )
        initialize_interface(app)
        template_kwargs = {
            'locations': get_locations(),
            'od_types': get_od_types(),
            'statistic_types': get_statistic_types(),
            'time_periods': get_time_periods(),
            'urls': URLS,
            'unit_population': UNIT_POPULATION_LABEL,
            'map_plot_param_names': MAP_PLOT_PARAM_NAMES,
            'time_plot_param_names': TIME_PLOT_PARAM_NAMES,
            'plot_params': get_preset_plot_params()
        }

        @app.route('/')
        def index():
            return render_template('app.html', **template_kwargs)

    return app
