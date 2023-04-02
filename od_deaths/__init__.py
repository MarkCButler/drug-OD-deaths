"""App factory that generates instances of the app."""
from pathlib import Path

from flask import Flask, render_template

from .database import init_app
from .plots import plot_views
from .tables import table_views
from .template_data import URLS
from .ui_labels import (
    get_locations, get_od_types, get_statistic_types, get_preset_plot_params,
    map_plot_param_names, TIME_PERIODS, time_plot_param_names
)

template_kwargs = {
    'od_types': get_od_types(),
    'statistic_types': get_statistic_types(),
    'time_periods': TIME_PERIODS,
    'urls': URLS,
    'map_plot_param_names': map_plot_param_names,
    'time_plot_param_names': time_plot_param_names,
    'plot_params': get_preset_plot_params()
}


def create_app():
    """Generate an instance of the app."""
    app = Flask(__name__, static_folder='../static')
    app.config.from_mapping(
        DATABASE_PATH=Path(app.root_path).parent / 'data' / 'OD-deaths.sqlite'
    )

    init_app(app)
    app.register_blueprint(plot_views)
    app.register_blueprint(table_views)

    @app.route('/')
    def index():
        # Interaction with the database is required to generate the list of
        # locations passed to the template. Since such interaction is only
        # supported within the context of an app, the call to function
        # get_locations is performed here rather than at the point where
        # template_kwargs is defined.
        return render_template('app.html', locations=get_locations(),
                               **template_kwargs)

    return app
