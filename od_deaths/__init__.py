"""App factory that generates instances of the app."""
from pathlib import Path

from flask import Flask, render_template

from .database import init_app
from .plots import plot_views
from .template_data import URLS


def create_app():
    """Generate an instance of the app."""
    app = Flask(__name__, static_folder='../static')
    app.config.from_mapping(
        DATABASE_PATH=Path(app.root_path).parent / 'data' / 'OD-deaths.sqlite'
    )

    init_app(app)

    app.register_blueprint(plot_views)

    @app.route('/')
    def index():
        return render_template('app.html', urls=URLS)

    return app
