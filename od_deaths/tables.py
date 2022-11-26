"""Views that return tables, along with supporting functions."""
from flask import Blueprint, request
from pandas import Categorical

from .database import get_od_deaths_table, get_population_table
from .labels import ORDERED_LOCATIONS

table_views = Blueprint('tables', __name__, url_prefix='/tables')

# Used in ordering table rows by chronological order of month names.
ORDERED_MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
]


@table_views.route('od-deaths-table')
def od_deaths_table():
    """Return an HTML table of raw data on OD deaths.

    The id to be assigned to the DOM table element should be included in the url
    as a parameter.  The app front end uses 'id=od-deaths-table'.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = get_od_deaths_table()
    data.Location = Categorical(data.Location, categories=ORDERED_LOCATIONS,
                                ordered=True)
    data.Month = Categorical(data.Month, categories=ORDERED_MONTHS,
                             ordered=True)
    data = data.sort_values(by=['Location', 'Year', 'Month', 'Indicator'])
    table_id = request.args.get('id', None)
    return data.to_html(index=False, table_id=table_id)


@table_views.route('population-table')
def population_table():
    """Return an HTML table of raw population data.

    The id to be assigned to the DOM table element should be included in the url
    as a parameter.  The app front end uses 'id=population-table'.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = get_population_table()
    data.Location = Categorical(data.Location, categories=ORDERED_LOCATIONS,
                                ordered=True)
    data = data.sort_values(by='Location')
    table_id = request.args.get('id', None)
    return data.to_html(index=False, table_id=table_id)
