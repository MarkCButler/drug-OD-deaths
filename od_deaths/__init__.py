from pathlib import Path

from flask import Flask, render_template


def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config.from_mapping(
        DATABASE=Path(app.root_path).parent / 'data' / 'OD-deaths.sqlite'
    )

    @app.route('/')
    def index():
        return render_template('app.html')

    return app
