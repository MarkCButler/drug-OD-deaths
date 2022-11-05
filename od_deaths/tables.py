"""Views that return tables, along with supporting functions."""

from flask import Blueprint

table_views = Blueprint('tables', __name__, url_prefix='/tables')
