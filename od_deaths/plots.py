"""Views that return plots, along with supporting functions."""
import json

from flask import Blueprint, make_response
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils as plotly_utils

from .database_queries import get_map_plot_data, get_time_plot_data
from .interface_labels import (
    COLORBAR_RANGES, COLORBAR_TITLES, COLORBAR_TICKFORMATS, get_iso_date_string,
    MAP_HOVERTEMPLATES, MAP_PLOT_PARAM_NAMES, TIME_PLOT_PARAM_NAMES
)
from .request_parameters import parse_plot_params

plot_views = Blueprint('plots', __name__, url_prefix='/plots')


@plot_views.route('/map')
def get_map_plot():
    """Parse query parameters sent with the request and return the Plotly JSON
    for the requested plot showing the distribution of OD deaths by state.
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    params['period'] = get_iso_date_string(params['period'])
    data = get_map_plot_data(**params)
    fig = generate_map_plot(data, params)
    return _make_plot_response(fig)


def generate_map_plot(data, params):
    """Generate a dictionary that can be used by the Plotly library to create a
    choropleth plot showing the distribution of OD deaths by state.

    Args:
        data:  dataframe of processed data with columns Location, Location_abbr,
            and Value
        params:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should have
            two keys: 'statistic' and 'period'.

    Returns:
        Dictionary that can be converted to Plotly JSON describing the map plot
    """
    statistic = params['statistic']
    colorbar_range = COLORBAR_RANGES[statistic]

    fig = px.choropleth(
        data_frame=data,
        locations='Location_abbr',
        color='Value',
        locationmode='USA-states'
    )
    fig.update_traces(
        text=data['Location'],
        hovertemplate=MAP_HOVERTEMPLATES[statistic],
        zmin=colorbar_range[0],
        zmax=colorbar_range[1]
    )
    _set_map_layout(fig, statistic)
    return fig


def _set_map_layout(fig, statistic):
    annotations = [{
        'text': 'Hover over states to see details',
        'xref': 'paper',
        'yref': 'paper',
        'x': 0.5,
        'y': -0.1,
        'showarrow': False,
        'font': {
            'size': 16
        }
    }]
    coloraxis = {
        'colorbar': {
            'tickformat': COLORBAR_TICKFORMATS[statistic],
            'title': {
                'text': COLORBAR_TITLES[statistic]
            }
        },
        'colorscale': 'RdBu',
        'reversescale': True
    }
    geo = {
        'scope': 'usa',
        'projection': {
            'type': 'albers usa'
        },
        'showcountries': False,
        'showlakes': False,
        'showland': False
    }
    margin = {
        't': 20,
        'b': 60
    }
    fig.update_layout(annotations=annotations, coloraxis=coloraxis, geo=geo,
                      margin=margin)


def _make_plot_response(response_data):
    response = make_response(
        json.dumps(response_data, cls=plotly_utils.PlotlyJSONEncoder)
    )
    response.headers['Content-Type'] = 'application/json'
    return response


@plot_views.route('/time')
def get_time_plot():
    """Parse query parameters sent with the request and return the Plotly JSON
    for the requested plot of time development.
    """
    params = parse_plot_params(TIME_PLOT_PARAM_NAMES)
    data = get_time_plot_data(
        location_abbr=params['location'],
        statistic=params['statistic'],
        od_types=params['od_type']
    )
    fig = generate_time_plot(data, params)
    return _make_plot_response(fig)


def generate_time_plot(data, params):

    # Generate dummy data for testing the design of the map.
    # TODO: delete the code for generating dummy data
    df = px.data.gapminder().query("continent == 'Oceania'")

    # The following redundant line is added to work around a bug in plotly, see
    # https://github.com/plotly/plotly.py/issues/3441#issuecomment-1271747147
    fig = go.Figure(layout=dict(template='plotly'))

    fig = px.line(df, x='year', y='lifeExp', color='country', markers=True)
    return fig
