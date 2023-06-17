# drug-OD-deaths-Python

This is an interactive web app written in Python for exploring data on
drug-overdose deaths in the US.

Note that a similar web app implemented in R is available at the repo

https://github.com/MarkCButler/drug-OD-deaths-R

## App interface

The app offers interactive plots showing the time development and the
geographic distribution of drug-overdose deaths.  For each plot, the app
user has a choice between three statistics to display:  number of deaths,
number of deaths per 100,000 people, and percent change in one year.

For the plot showing time development, multiple categories of drug-overdose
deaths can be compared in a single plot for a selected state or for the full
US.

The plot showing geographic distribution is a choropleth map colored by the
selected statistic.  By choosing different time periods for the data displayed
on the map, the user can monitor the variation in geographic distribution with
time.

The summary tab of the app presents three plots illustrating take-away
messages that can be found using the interactive plots in the app.

## Architecture

In contrast to the project at drug-OD-deaths-R, which used the `shiny` package
to create a web app, the current project uses a full-stack tool set for web
development.  The back end is a `flask` app that uses the Python data-science
stack for analysis and visualization of data, and the user interface is defined
by a `Jinja2` template that is rendered by `flask`.  The JavaScript that enables
user interaction is bundled by means of `webpack` with front-end libraries
(e.g., a small, customized subset of `bootstrap` and a selection of modules from
`plotly.js`.)

## Data model

The script *create_database.py* in the repo root was used to create a normalized
SQLite database.  The data separates drug-overdose deaths into categories based
on the type of drug involved. Death counts in different categories are given for
individual states and for the full US.

The app also includes CLI commands to drop/recreate a non-normalized table of
derived data.  For each location and time period, the table of derived data
includes the death count per unit population as well as the percent change in
death counts during the previous year. This table significantly simplifies the
processing performed in response to requests.

The app CLI commands for dropping/recreating the derived data support the
following process for updating the data consumed by the app:
1.  Drop the table of derived data.
2.  Update the normalized tables that remain, using constraints to preserve
data integrity.
3.  Recreate the table of derived data.

The
[data on drug-overdose deaths](https://data.cdc.gov/NCHS/VSRR-Provisional-Drug-Overdose-Death-Counts/xkb8-kh2a)
covers the period from January 2015 to April 2020, and
[annual population estimates](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)
were obtained from government census data.  When the table of derived data is
created, the census data is interpolated to provide monthly population
estimates.  Interpolation is needed in order to avoid spurious jumps in
time-series plots that show the number of deaths per unit population.

## Multi-stage Dockerfile

The repo includes a multi-stage Dockerfile and accompanying compose file.
- For front-end development, the command
  ```bash
  docker compose run front-end-dev
  ```
  builds the target `front-end-dev-env` in the Dockerfile and runs the resulting
  image as a container with an interactive shell.  Commands from the `scripts`
  object of the file *front-end/package.json* can be executed within this
  container.  The front-end source code located on the host machine is used as
  input for these commands, and output files are placed on the host machine.
- For back-end development, the command
  ```bash
  docker compose run --service-ports back-end-dev
  ```
  similarly builds the target `back-end-dev-env` in the Dockerfile and runs the
  resulting image as a container with an interactive shell.  This container can be
  used to initialize the database and run flask's built-in server during
  development.  As with the container generated for front-end development,
  commands executed within this container use source code located on the host
  machine as input.
- For deployment to production, the command
  ```bash
  docker compose up app
  ````
  builds the target `production-build` in the Dockerfile and starts the app behind
  the `gunicorn` server.  Front- and back-end production builds are performed in
  earlier stages of the Dockerfile, and the resulting artifacts are copied into
  the `production-build` stage, giving a minimal production image.
