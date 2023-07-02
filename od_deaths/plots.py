"""Views that return plots, along with supporting functions."""
import json

from flask import Blueprint, make_response
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils as plotly_utils

from .database_queries import get_map_plot_data, get_time_plot_data
from .interface_labels import (
    COLORBAR_RANGES, COLORBAR_TITLES, MAP_HOVERTEMPLATES, MAP_PLOT_PARAM_NAMES,
    OD_TYPE_LABELS, STATISTIC_LABELS, TICKFORMATS, TIME_PLOT_HOVERTEMPLATES,
    TIME_PLOT_PARAM_NAMES, TIME_PLOT_YAXIS_TITLE_FORMATS
)
from .request_parameters import parse_plot_params

plot_views = Blueprint('plots', __name__, url_prefix='/plots')


@plot_views.route('/map')
def get_map_plot():
    """Parse query parameters sent with the request and return the Plotly JSON
    for the requested plot showing the distribution of OD deaths by state.

    Query parameters determine the following aspects of the plot:
      - the year-long time period in which the OD deaths occurred
      - whether the plot shows total death counts, death counts per unit
          population, or percent change in death count within the past year
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    data = get_map_plot_data(**params)
    fig = generate_map_plot(data, params)
    return _make_plot_response(fig)


def generate_map_plot(data, params):
    """Generate a data structure describing a choropleth plot that shows the
    distribution of OD deaths by state.

    Args:
        data:  dataframe with columns Location, Location_abbr, and Value
        params:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should have
            two keys:  'statistic' and 'period'.

    Returns:
        Data structure that can be converted to Plotly JSON, which in turn can
        be converted to a plot by the front-end Plotly.js library
    """
    statistic = params['statistic']

    fig = px.choropleth(
        data_frame=data,
        locations='Location_abbr',
        color='Value',
        range_color=COLORBAR_RANGES[statistic],
        locationmode='USA-states'
    )
    fig.update_traces(
        text=data['Location'],
        hovertemplate=MAP_HOVERTEMPLATES[statistic]
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
            'tickformat': TICKFORMATS[statistic],
            'title': {
                'text': COLORBAR_TITLES[statistic]
            }
        },
        'colorscale': 'RdBu',
        'reversescale': True
    }
    font = {'size': 14}
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
    fig.update_layout(
        annotations=annotations,
        coloraxis=coloraxis,
        font=font,
        geo=geo,
        margin=margin
    )


def _make_plot_response(response_data):
    response = make_response(
        json.dumps(response_data, cls=plotly_utils.PlotlyJSONEncoder)
    )
    response.headers['Content-Type'] = 'application/json'
    return response


@plot_views.route('/time')
def get_time_plot():
    """Parse query parameters sent with the request and return the Plotly JSON
    for the requested plot showing the time development of an OD-death
    statistic.

    Query parameters determine the following aspects of the plot:
      - the location for which data is plotted
      - whether the plot shows total death counts, death counts per unit
          population, or percent change in death count within the past year
      - the categories of OD deaths that are shown in the plot, e.g., deaths
          due to heroin, deaths due to prescription opioids
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
    """Generate a data structure describing a line plot that shows the time
    development of an OD-death statistic.

    Args:
        data:  dataframe with columns Period, OD_type, and Value
        params:  dictionary of query parameters in the format returned by
            request_parameters.parse_plot_params.  The dictionary should have
            three keys:  'location', 'statistic', and 'od_type'

    Returns:
        Data structure that can be converted to Plotly JSON, which in turn can
        be converted to a plot by the front-end Plotly.js library
    """
    # Data must be sorted for plotting.
    data = data.sort_values(by=['Period'])
    # Replace abbreviated OD types such as 'all_drug_od' by friendlier labels
    # such as 'All drug-overdose deaths'.
    data['OD_type'] = data['OD_type'].map(OD_TYPE_LABELS)

    # The following redundant line is added to work around a bug in plotly, see
    # https://github.com/plotly/plotly.py/issues/3441#issuecomment-1271747147
    fig = go.Figure(layout={'template': 'plotly'})

    statistic = params['statistic']
    fig = px.line(
        data,
        x='Period',
        y='Value',
        color='OD_type',
        labels={
            'OD_type': 'OD category',
            'Period': 'Date',
            'Value': STATISTIC_LABELS[statistic]
        },
        category_orders={
            'OD_type': [
                OD_TYPE_LABELS[od_type]
                for od_type in _get_ordered_od_types(params)
            ]
        },
        markers=True
    )
    fig.update_traces(
        hovertemplate=TIME_PLOT_HOVERTEMPLATES[statistic]
    )
    _set_time_plot_layout(fig, statistic)
    return fig


def _get_ordered_od_types(params):
    """Extract a list of the OD types requested in the query parameters for the
    time-development plot.

    The list of OD types returned by the function preserves the order in which
    the OD types appear in the query parameters.
    """
    od_types = params['od_type']
    if isinstance(od_types, str):
        od_types = [od_types]
    return od_types


def _set_time_plot_layout(fig, statistic):
    font = {'size': 14}
    margin = {'t': 20}
    yaxis = {
        'tickformat': TICKFORMATS[statistic],
        'title': TIME_PLOT_YAXIS_TITLE_FORMATS[statistic]
    }
    fig.update_layout(
        font=font,
        margin=margin,
        yaxis=yaxis
    )
