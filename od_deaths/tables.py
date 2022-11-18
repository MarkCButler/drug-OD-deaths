"""Views that return tables, along with supporting functions."""
from flask import Blueprint

from .database import get_od_deaths_table

table_views = Blueprint('tables', __name__, url_prefix='/tables')


@table_views.route('od-deaths-table')
def test_od_deaths_table():
    data = get_od_deaths_table()
    return data.to_html(index=False)
