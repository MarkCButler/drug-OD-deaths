/*******************************************************************************
  The tables created by the SQLite commands below preserve in normalized form
  the data consumed by the app.  Derived data used by the app is calculated
  and stored in a separate table in the database when the app is first
  instantiated. (See the docstring for the module
  od_deaths.database_initialization for a discussion of the motivation to
  separate derived data from the data consumed by the app.)
*******************************************************************************/
PRAGMA foreign_keys = ON;

CREATE TABLE od_types (
  Indicator TEXT NOT NULL PRIMARY KEY,
  OD_type   TEXT NOT NULL
);

CREATE TABLE locations (
  Abbr TEXT NOT NULL PRIMARY KEY,
  Name TEXT NOT NULL
);

CREATE TABLE death_counts (
  Location_abbr TEXT    NOT NULL,
  Year          INTEGER NOT NULL,
  Month         TEXT    NOT NULL,
  Indicator     TEXT    NOT NULL,
  Death_count   INTEGER NOT NULL,
  PRIMARY KEY (Location_abbr, Year, Month, Indicator),
  FOREIGN KEY (Location_abbr)
    REFERENCES locations (Abbr),
  FOREIGN KEY (Indicator)
    REFERENCES od_types (Indicator)
);

CREATE TABLE populations (
  Location_abbr TEXT    NOT NULL,
  Year          INTEGER NOT NULL,
  Population    INTEGER NOT NULL,
  PRIMARY KEY (Location_abbr, Year),
  FOREIGN KEY (Location_abbr)
    REFERENCES locations (Abbr)
);
