"""Views that return dynamic updates to the options shown in form controls."""
from flask import Blueprint

from .query_parameters import parse_plot_params
from .ui_labels import (
    get_map_plot_statistic_options, get_map_plot_period_options,
    get_time_plot_od_type_options, MAP_PLOT_PARAM_NAMES, TIME_PLOT_PARAM_NAMES
)

option_views = Blueprint('options', __name__, url_prefix='/form-options')


@option_views.route('map-plot-statistic')
def map_plot_statistic_options():
    """Parse query parameters sent with the request and return a list of
    choices for the statistic to use in generating the map plot.

    An HTML select element is updated by the front end based on the list of
    choices returned by the current function.

    Returns:
        List of strings, each corresponding to the value of an HTML option
        element
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    return get_map_plot_statistic_options(params)


@option_views.route('map-plot-period')
def map_plot_period_options():
    """Parse query parameters sent with the request and return a list of choices
    for the time period to use in generating the map plot.

    An HTML select element is updated by the front end based on the list of
    choices returned by the current function.

    Returns:
        List of strings, each corresponding to the value of an HTML option
        element
    """
    params = parse_plot_params(MAP_PLOT_PARAM_NAMES)
    return get_map_plot_period_options(params)


@option_views.route('time-plot-od-type')
def time_plot_od_type_options():
    """Parse query parameters sent with the request and return a list of choices
    for the type of OD death to use in generating the plot of time development.

    An HTML select element is updated by the front end based on the list of
    choices returned by the current function.

    Returns:
        List of strings, each corresponding to the value of an HTML option
        element
    """
    params = parse_plot_params(TIME_PLOT_PARAM_NAMES)
    return get_time_plot_od_type_options(params)
