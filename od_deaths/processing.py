"""Functions that returned processed data to be consumed by plotting
functions.
"""
from .database import get_map_data, get_time_data
from .ui_labels import get_month_and_year


def get_processed_map_data(param_dict):
    """Return a dataframe of processed data that can be used to generate a map
    plot.

    The argument param_dict gives information about the query parameters used in
    requesting the plot.  The dictionary should have two keys:
      -'statistic':  allowed values are 'death_count', 'normalized_death_count',
          and 'percent_change'
      - 'period':  the current module does not need to "understand" the value,
          because the function get_month_and_year (imported from the module
          ui_labels) is used to convert it to a named tuple with attributes
          month and year.
    """
    period = get_month_and_year(param_dict['period'])
    data = get_map_data(month=period.month, year=period.year,
                        add_location_names=True)
    return data


def get_processed_time_data(param_dict):
    """Return a dataframe of processed data that can be used to generate a plot
    of time development.

    The argument param_dict gives information about the query parameters used in
    requesting the plot.  The dictionary should have three keys:
      - 'location':  allowed values are given by the Abbr column of the table of
          locations exposed by the database module in the current package. (Note
          that a list of allowed values can be obtained programmatically from
          the function get_locations in the module ui_labels.)
      -'statistic':  allowed values are 'death_count', 'normalized_death_count',
          and 'percent_change'
      - 'od_type':  a string or a list of strings, each equal to a value
          appearing in the OD_type column in the table of OD deaths exposed by
          the database module.  (Note that the allowed values are keys in the
          dictionary OD_TYPE_LABELS in the module ui_labels.)
    """
    data = get_time_data(
        location_abbr=param_dict['location'],
        od_types=param_dict['od_type'],
        add_location_names=False
    )
    return data
