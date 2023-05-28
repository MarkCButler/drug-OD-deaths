"""Generate SQLite database of normalized tables from csv files."""
from pathlib import Path
import sqlite3
import sys

import pandas as pd

DB_PATH = Path('data') / 'OD-deaths.sqlite'
SCRIPT_PATH = Path('create_tables.sql')
POPULATION_PATH = Path('data') / 'population.csv'
DEATH_COUNTS_PATH = Path('data') / 'VSRR_Provisional_Drug_Overdose_Death_Counts.csv'

# The population.csv file was created by manually modifying an .xlsx file
# downloaded from www.census.gov.  The csv file contains population estimates
# for the US and each of the 50 states.  For each of the years 2014 - 2019,
# there is an estimate of the population on July 1.
population_data = (
    pd.read_csv(POPULATION_PATH)
    .rename(columns={'State': 'Location'})
    .melt(id_vars=['Location'],
          var_name='Year',
          value_name='Population')
)

# Extract from the csv file of death counts the columns and rows needed for
# the app.  Also filter out rows that are missing the death count, in order to
# simplify later processing.
to_load = ['State', 'Year', 'Month', 'Indicator', 'Data Value', 'State Name']
deaths_data = (
    pd.read_csv(DEATH_COUNTS_PATH, usecols=to_load)
    .rename(columns={'Data Value': 'Death_count'})
)
bool_index = (~deaths_data['State'].isin(['DC', 'YC'])
              & ~deaths_data['Death_count'].isna()
              & deaths_data['Indicator'].str.contains(r'T\d|Drug Overdose Deaths')
              & ~deaths_data['Indicator'].str.contains(r'incl\. methadone'))
deaths_data = deaths_data[bool_index].reset_index(drop=True)

# Define an OD type for each value of the Indicator column.  The OD type
# bypasses the technical terminology used in the Indicator column and also
# groups different values within this column into the familiar categories shown
# in the app interface.
#
# Note that the order of the commands that define the OD type is significant.
# For instance, the indicator
#
# 'Opioids (T40.0-T40.4,T40.6)'
#
# is detected early in the series of cases by checking for the substring
# 'T40.0', and after this check, simple substrings such as 'T40.4' uniquely
# identify the remaining indicators.
od_type = deaths_data['Indicator'].copy()
od_type[od_type.str.contains('T40.0')] = 'all_opioids'
od_type[od_type.str.contains('T40.1')] = 'heroin'
od_type[od_type.str.contains('T40.2')] = 'prescription_opioids'
od_type[od_type.str.contains('T40.[34]')] = 'synthetic_opioids'
od_type[od_type.str.contains('T40.5')] = 'cocaine'
od_type[od_type.str.contains('T43')] = 'other_stimulants'
od_type[od_type.str.contains('Drug Overdose')] = 'all_drug_od'

# Create of table of OD types.
od_type_data = (
    pd.DataFrame({'Indicator': deaths_data['Indicator'].copy(),
                  'OD_type': od_type})
    .drop_duplicates()
)

# Create a table that gives the full state name for each state abbreviation.
location_data = (
    deaths_data[['State', 'State Name']]
    .drop_duplicates()
    .rename(columns={'State': 'Abbr', 'State Name': 'Name'})
)

# The SQLite commands used to create tables define the location abbreviation in
# the 'locations' table as a primary key, and location abbreviations in other
# tables are foreign keys referencing the primary key of the 'locations' table.
#
# Consistent with this schema, drop the 'State Name' column from deaths_data,
# and replace the full location name in population_data by the abbreviation.
deaths_data = (deaths_data.drop(columns='State Name')
               .rename(columns={'State': 'Location_abbr'}))
to_replace = dict(zip(location_data['Name'], location_data['Abbr']))
population_data['Location'] = population_data['Location'].replace(to_replace)
population_data.rename(columns={'Location': 'Location_abbr'}, inplace=True)

if DB_PATH.exists():
    response = input(f'The database {DB_PATH} already exists.  '
                     'Do you wish to replace it (yes/no)? ')
    if response == 'yes':
        DB_PATH.unlink()
    else:
        print('\nExiting.\n\n')
        sys.exit()

db_con = sqlite3.connect(DB_PATH)
with db_con:
    cursor = db_con.cursor()
    cursor.executescript(SCRIPT_PATH.read_text(encoding='utf-8'))
    # Since the death_counts table includes foreign keys from the tables
    # od_types and locations, these tables must be populated with data before
    # death_counts is populated.
    od_type_data.to_sql('od_types', con=db_con,
                        if_exists='append', index=False)
    location_data.to_sql('locations', con=db_con,
                         if_exists='append', index=False)
    deaths_data.to_sql('death_counts', con=db_con,
                       if_exists='append', index=False)
    population_data.to_sql('populations', con=db_con,
                           if_exists='append', index=False)

db_con.close()
