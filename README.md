# drug-OD-deaths-Python

This is an interactive web app written in Python for exploring data on
drug-overdose deaths in the US.

Note that a similar web app implemented in R is available at the repo

https://github.com/MarkCButler/drug-OD-deaths-R

In contrast to the project at drug-OD-deaths-R, which used the `shiny` package
to create a web app, the current project uses a full-stack tool set for web
development.  The back end is a `flask` app that uses the Python data-science
stack for data analysis, and the user interface is defined by a `Jinja2`
template that is rendered by `flask`.  The JavaScript that controls the
front-end's interactivity is bundled by means of `webpack` with customized tools
that are used to style the user interface (e.g., a small, customized subset of
`bootstrap`.)

The
[data on drug-overdose deaths](https://data.cdc.gov/NCHS/VSRR-Provisional-Drug-Overdose-Death-Counts/xkb8-kh2a),
covering the period from January 2015 to April 2020, was converted to a SQLite
database.

[Annual population estimates](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)
are interpolated.
