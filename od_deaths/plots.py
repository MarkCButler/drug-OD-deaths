"""Views that return plots, along with supporting functions."""
import json

from flask import Blueprint, make_response
import plotly.graph_objects as go
import plotly.utils as plotly_utils

plot_views = Blueprint('plots', __name__, url_prefix='/plots')


@plot_views.route('/test-plot')
def get_test_plot():
    fig = go.Figure(go.Scattergeo())
    fig.update_geos(
        visible=False, resolution=110, scope="usa",
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Blue"
    )
    fig.update_layout(height=300, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    response = make_response(
        json.dumps(fig, cls=plotly_utils.PlotlyJSONEncoder)
    )
    response.headers['Content-Type'] = 'application/json'
    return response
