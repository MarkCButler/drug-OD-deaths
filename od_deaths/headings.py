"""Views that return dynamic updates to HTML headings."""
from flask import Blueprint

from .query_parameters import parse_plot_params
from .ui_labels import (
    get_map_plot_heading, get_map_plot_subheading, get_time_plot_heading,
    get_time_plot_subheading, MAP_PLOT_PARAM_NAMES, TIME_PLOT_PARAM_NAMES
)

heading_views = Blueprint('headings', __name__, url_prefix='/headings')


@heading_views.route('map-plot-heading')
def map_plot_heading():
    """Parse query parameters sent with the request and return a text heading
    dynamically selected for the map plot.
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    return get_map_plot_heading(params)


@heading_views.route('map-plot-subheading')
def map_plot_subheading():
    """Parse query parameters sent with the request and return a text subheading
    dynamically selected for the map plot.
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    return get_map_plot_subheading(params)


@heading_views.route('time-plot-heading')
def time_plot_heading():
    """Parse query parameters sent with the request and return a text heading
    dynamically selected for the time plot.
    """
    params = parse_plot_params(TIME_PLOT_PARAM_NAMES)
    return get_time_plot_heading(params)


@heading_views.route('time-plot-subheading')
def time_plot_subheading():
    """Parse query parameters sent with the request and return a text subheading
    dynamically selected for the time plot.
    """
    params = parse_plot_params(TIME_PLOT_PARAM_NAMES)
    return get_time_plot_subheading(params)
