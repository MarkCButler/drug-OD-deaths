"""App factory that generates instances of the app."""
from pathlib import Path

from flask import Flask, render_template

from .control_options import option_views
from .database import initialize_database
from .html_headings import heading_views
from .html_tables import table_views
from .plots import plot_views
from .template_data import URLS
from .ui_labels import (
    get_locations, get_od_types, get_preset_plot_params, get_statistic_types,
    get_time_periods, initialize_ui_labels, MAP_PLOT_PARAM_NAMES,
    TIME_PLOT_PARAM_NAMES, UNIT_POPULATION_LABEL
)


def register_blueprints(app, blueprints):
    """Register a sequence of blueprints on the app.

    Args:
        app:  application on which blueprints will be registered
        blueprints:  iterable of blueprints, each of which will be registered on
            the application
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def create_app():
    """Generate an instance of the app."""
    app = Flask(__name__, static_folder='../static')
    app.config.from_mapping(
        DATABASE_PATH=Path(app.root_path).parent / 'data' / 'OD-deaths.sqlite'
    )

    initialize_database(app)
    initialize_ui_labels(app)
    register_blueprints(
        app, [heading_views, option_views, plot_views, table_views]
    )

    # The function initialize_ui_labels needs to be called before the dictionary
    # template_kwargs is defined, since that function initializes the table of
    # locations returned below by get_locations.
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
