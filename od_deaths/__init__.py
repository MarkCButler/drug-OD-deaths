"""App factory that generates instances of the app."""
from pathlib import Path

from flask import Flask, render_template

# Included for exploratory purposes.  To be removed later.
import json
from flask import make_response
import plotly
import plotly.express as px


def create_app():
    """Generate an instance of the app."""
    app = Flask(__name__, static_folder='../static')
    app.config.from_mapping(
        DATABASE_PATH=Path(app.root_path).parent / 'data' / 'OD-deaths.sqlite'
    )

    from .database import init_app     # pylint: disable=import-outside-toplevel
    init_app(app)

    @app.route('/')
    def index():
        return render_template('app.html')

    @app.route('/test-plot')
    def get_test_plot():
        fig = px.bar(x=['a', 'b', 'c'], y=[1, 3, 2])
        response = make_response(
            json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    return app
