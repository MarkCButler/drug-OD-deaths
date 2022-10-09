"""Views that return plots, along with supporting functions."""
import json

from flask import Blueprint, make_response
import plotly
import plotly.express as px

plot_views = Blueprint('plots', __name__, url_prefix='/plots')

# TODO: 1. Replace the test plot with a choropleth map from plotly
#       2. Edit app-plotly.js to include only the traces used in the R version of the app


@plot_views.route('/test-plot')
def get_test_plot():
    fig = px.bar(x=['a', 'b', 'c'], y=[1, 3, 2])
    response = make_response(
        json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    )
    response.headers['Content-Type'] = 'application/json'
    return response
