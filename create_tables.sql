PRAGMA foreign_keys = ON;

CREATE TABLE locations (
  Abbr TEXT NOT NULL PRIMARY KEY,
  Name TEXT NOT NULL
);

CREATE TABLE death_counts (
  Location_abbr TEXT NOT NULL,
  Year INTEGER NOT NULL,
  Month TEXT NOT NULL,
  Indicator TEXT NOT NULL,
  Death_count INTEGER NOT NULL,
  PRIMARY KEY (Location_abbr, Year, Month, Indicator),
  FOREIGN KEY (Location_abbr)
    REFERENCES locations (Abbr)
);

CREATE TABLE od_types (
    Indicator TEXT NOT NULL PRIMARY KEY ,
    OD_type TEXT NOT NULL
);

CREATE TABLE populations (
  Location_abbr TEXT NOT NULL,
  Year INTEGER NOT NULL,
  Month TEXT NOT NULL,
  Population INTEGER NOT NULL,
  PRIMARY KEY (Location_abbr, Year, Month),
  FOREIGN KEY (Location_abbr)
    REFERENCES locations (Abbr)
);
