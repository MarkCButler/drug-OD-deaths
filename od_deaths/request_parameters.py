"""Functions for handling query parameters used in HTTP requests."""
from flask import request


def parse_plot_params(plot_param_names):
    """Convert query parameters sent with a plot request into a dictionary that
    can be consumed by the app module that generates the plot.

    The parameter names used by the front end in requesting plot data are
    replaced by simple strings that are understood by back-end modules.  For
    example, a string such as

    time-plot-statistic=normalized_death_count

    from the query string is converted to the key-value par

    'statistic': 'normalized_death_count'

    in the dictionary returned by the current function.

    Args:
        plot_param_names:  One of the dictionaries TIME_PLOT_PARAM_NAMES,
            MAP_PLOT_PARAM_NAMES defined in the module ui_labels.    The keys in
            TIME_PLOT_PARAM_NAMES are 'location', 'statistic', and 'od_type',
            while the keys in MAP_PLOT_PARAM_NAMES are 'statistic' and 'period'.
            The corresponding values in each dictionary are parameter names used
            by the front end in requesting plots.

    Returns:
        Dictionary with the same keys as the argument plot_param_names.  If the
        query parameters being parsed included multiple values for a single
        parameter name, the values are collected into a list.  Example:
            {
                'location': 'US',
                'statistic': 'normalized_death_count',
                'od_type': ['all_opioids', 'synthetic_opioids']
            }
    """
    param_dict = {key: request.args.getlist(plot_param_names[key])
                  for key in plot_param_names}
    for key, value in param_dict.items():
        if len(value) == 1:
            param_dict[key] = value[0]
    return param_dict
