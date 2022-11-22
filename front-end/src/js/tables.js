'use strict';

import $ from 'jquery';
import 'datatables.net-bs5';

import {displayAppError, HTTPError} from './errors';


async function addTable(divElem, url, tableId, tableName) {
  try {
    const response = await fetch(url);
    if (response.ok) {
      divElem.innerHTML = await response.text();
      // The DataTables library used to make the table interactive is a jQuery
      // plug-in, and so jQuery syntax is used in calling the library.
      const selector = '#' + tableId;
      $(selector).DataTable();                    // eslint-disable-line new-cap
    } else {
      throw new HTTPError(`status code ${response.status}`);
    }
  } catch (error) {
    displayAppError(error, divElem, tableName);
  }
}

// In the ids associated with tables, the endings 'bs' and 'dt' indicate that
// the id is used by the bootstrap or datatable libraries, respectively.
const odDeathsTable = document.getElementById('od-deaths-table-bs');
let url = '/tables/od-deaths-table?id=od-deaths-table-dt';
void addTable(odDeathsTable, url, 'od-deaths-table-dt', 'od-deaths-table');
url = '/tables/population-table?id=population-table-dt';
const populationTable = document.getElementById('population-table-bs');
void addTable(populationTable, url, 'population-table-dt', 'population-table');
