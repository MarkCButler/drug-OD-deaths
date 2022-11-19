'use strict';

import {displayAppError, HTTPError} from './errors';


async function addTable(divElem, url, tableName) {
  try {
    const response = await fetch(url);
    if (response.ok) {
      divElem.innerHTML = await response.text();
    } else {
      throw new HTTPError(`status code ${response.status}`);
    }
  } catch (error) {
    displayAppError(error, divElem, tableName);
  }
}

const odDeathsTable = document.getElementById('od-deaths-table');
void addTable(odDeathsTable, '/tables/od-deaths-table', 'od-deaths-table');
const populationTable = document.getElementById('population-table');
void addTable(populationTable, '/tables/population-table', 'population-table');
