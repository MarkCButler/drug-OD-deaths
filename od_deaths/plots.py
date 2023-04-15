"""Views that return plots, along with supporting functions."""
import json

from flask import Blueprint, make_response
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils as plotly_utils

from .processed_data import get_processed_map_data, get_processed_time_data
from .query_parameters import parse_plot_params
from .ui_labels import (
    COLORBAR_TITLES, COLORBAR_TICKFORMATS, MAP_HOVERTEMPLATES,
    MAP_PLOT_PARAM_NAMES, TIME_PLOT_PARAM_NAMES
)

plot_views = Blueprint('plots', __name__, url_prefix='/plots')


# TODO: For consistency between modules (as well as with the template), move the
#   functions for time-plot views below the functions for map-plot views.
@plot_views.route('/interactive-time-plot')
def get_time_plot_and_options():
    """Parse query parameters sent by the front end and return JSON that can be
    used to update both the plot and the options visible on the corresponding
    form.

    The JSON returned has two keys: 'plot' and 'form-options'.

    The reason the same back-end url is used to deliver a simultaneous update of
    both the plot and the visible form options is that in the general case, both
    types of updates require a database query and data processing.  If separate
    HTTP requests were used to update the plot and the visible form options, the
    back end would in some cases have to repeat a database query and redo some
    data processing.
    """
    return get_time_plot()


@plot_views.route('/time-plot')
def get_time_plot():
    """Parse query parameters sent by the front end and return the Plotly JSON
    for the requested plot of time development.
    """
    params = parse_plot_params(TIME_PLOT_PARAM_NAMES)
    data = get_processed_time_data(params)

    # Generate dummy data for testing the design of the map.
    # TODO: delete the code for generating dummy data
    df = px.data.gapminder().query("continent == 'Oceania'")

    # The following redundant line is added to work around a bug in plotly, see
    # https://github.com/plotly/plotly.py/issues/3441#issuecomment-1271747147
    fig = go.Figure(layout=dict(template='plotly'))

    fig = px.line(df, x='year', y='lifeExp', color='country', markers=True)
    return _make_plot_response(fig)


def _make_plot_response(fig):
    response = make_response(
        json.dumps(fig, cls=plotly_utils.PlotlyJSONEncoder)
    )
    response.headers['Content-Type'] = 'application/json'
    return response


# Generate dummy data for testing the design of the map.
# TODO: delete the code for generating dummy data.
from numpy.random import default_rng
import pandas as pd
states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}
state_columns = list(zip(*states.items()))


# Given a choice of statistic, the colorbar range is set to the max and min
# values of that statistic for the dataset.  The colorbar range remains
# fixed when the selected year changes.
colorbar_ranges = {}


@plot_views.route('/interactive-map-plot')
def get_map_plot_and_options():
    """Parse query parameters sent by the front end and return JSON that can be
    used to update both the plot and the options visible on the corresponding
    form.

    The JSON returned has two keys: 'plot' and 'form-options'.

    The reason the same back-end url is used to deliver a simultaneous update of
    both the plot and the visible form options is that in the general case, both
    types of updates require a database query and data processing.  If separate
    queries were used for the plot and the visible form options, the back end
    would in some cases have to repeat a database query and redo some data
    processing.
    """
    return get_map_plot()


@plot_views.route('/map-plot')
def get_map_plot():
    """Parse query parameters sent by the front end and return the Plotly JSON
    for the requested plot of US distribution.
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    data = get_processed_map_data(params)

    # Dummy value, will be an input passed to the function that plots the map.
    statistic_label = 'normalized_death_count'
    # TODO: Add query that gets the absolute maximum and minimum for the
    #   statistic_label and then stores them (e.g., as a function property).  If
    #   the values have already been fetched for the current statistic, then use
    #   the stored values.

    # if statistic_label not in colorbar_ranges:
    #     colorbar_ranges[statistic_label] = _get_range(statistic_label)

    # TODO: delete this temporary kluge once the above query and range storage
    #   has been implemented.
    colorbar_ranges = {
        'death_count': (55, 5959),
        'normalized_death_count': (5.9, 55.4),
        'percent_change': (-.333, .573)
    }

    colorbar_range = colorbar_ranges[statistic_label]

    # Generate dummy data for testing the design of the map.
    # TODO: delete the code for generating dummy data.
    rng = default_rng()
    values = rng.uniform(*colorbar_range, 51)
    data_dict = {'state_abb': state_columns[0],
                 'state_names': state_columns[1],
                 'values': values}
    data = pd.DataFrame(data_dict)

    # Test the design of the map.
    fig = px.choropleth(
        data_frame=data,
        locations='state_abb',
        color='values',
        locationmode='USA-states'
    )
    fig.update_traces(
        text=data['state_names'],
        hovertemplate=MAP_HOVERTEMPLATES[statistic_label],
        zmin=colorbar_range[0],
        zmax=colorbar_range[1]
    )
    _set_map_layout(fig, statistic_label)
    return _make_plot_response(fig)


def _set_map_layout(fig, statistic_label):
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
            'tickformat': COLORBAR_TICKFORMATS[statistic_label],
            'title': {
                'text': COLORBAR_TITLES[statistic_label]
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
