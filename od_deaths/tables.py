"""Views that return tables, along with supporting functions."""
from flask import Blueprint, request
from pandas import Categorical

from .database import get_od_deaths_table, get_population_table
from .ui_labels import get_location_names, get_od_code_table

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
    data.Location = Categorical(data.Location, categories=get_location_names(),
                                ordered=True)
    data.Month = Categorical(data.Month, categories=ORDERED_MONTHS,
                             ordered=True)
    data = data.sort_values(by=['Location', 'Year', 'Month', 'Indicator'])
    return _to_html_table(data)


def _to_html_table(data):
    table_id = request.args.get('id', None)
    return data.to_html(index=False, justify='left', table_id=table_id)


@table_views.route('population-table')
def population_table():
    """Return an HTML table of raw population data.

    The id to be assigned to the DOM table element should be included in the url
    as a parameter.  The app front end uses 'id=population-table'.

    The table is a subset of the raw data with some column names changed to
    improve readability.
    """
    data = get_population_table()
    data.Location = Categorical(data.Location, categories=get_location_names(),
                                ordered=True)
    data = data.sort_values(by='Location')
    return _to_html_table(data)


@table_views.route('od-code-table')
def od_code_table():
    """Return an HTML table showing the correspondence between the following:
    1. Labels used in the app's UI to indicate the type of overdose
    2. Cause-of-death codes from ICD–10, the Tenth Revision of the International
    Statistical Classification of Diseases and Related Health Problems

    The id to be assigned to the DOM table element should be included in the url
    as a parameter.  The app front end uses 'id=od-code-table'.
    """
    return _to_html_table(get_od_code_table())
