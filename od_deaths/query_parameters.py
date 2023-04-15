"""Functions for handling query parameters used in HTTP requests."""
from flask import request


def parse_plot_params(plot_param_names):
    """Convert query parameters into a dictionary that can be consumed by the
    app module that processes data.

    The parameter names used by the front end in requesting plot data are
    replaced by simple strings that are understood by back-end modules.  For
    example, a string such as

    time-plot-statistic=normalized_death_count

    from the query string is converted to the key-value par

    'statistic': 'normalized_death_count'

    in the dictionary returned by the current function.

    Args:
        plot_param_names:  Dictionary (such as ui_labels.TIME_PLOT_PARAM_NAMES)
            that has the UI parameter names as values.  The allowed keys are
            'location', 'statistic', 'od_type', and 'period'.

    Returns:
        Dictionary with the same keys as the argument plot_param_names.  If the
        query parameters being parsed included multiple values for a single
        parameter name, the values are collected into a list.  Example:
            {
                'location': 'US',
                'statistic': 'normalized_death_count',
                'od_type': ['prescription_opioids', 'synthetic_opioids']
            }
    """
    param_dict = {key: request.args.getlist(plot_param_names[key])
                  for key in plot_param_names}
    for key, value in param_dict.items():
        if len(value) == 1:
            param_dict[key] = value[0]
    return param_dict
