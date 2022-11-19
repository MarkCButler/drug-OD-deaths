"""Views that return tables, along with supporting functions."""
from flask import Blueprint

from .database import get_od_deaths_table, get_population_table

table_views = Blueprint('tables', __name__, url_prefix='/tables')


@table_views.route('od-deaths-table')
def od_deaths_table():
    return get_od_deaths_table().to_html(index=False)


@table_views.route('population-table')
def population_table():
    return get_population_table().to_html(index=True)
