'use strict';

import $ from 'jquery';
import 'datatables.net-bs5';

import {displayAppError, HTTPError} from './errors';

// Options used by the DataTables library
const dtOptions = {
  order: []
};


async function addTable(divElem, url, tableId) {
  try {
    url = url + '?id=' + tableId;
    const response = await fetch(url);
    if (response.ok) {
      divElem.innerHTML = await response.text();
      addBootstrapStyle(tableId);
      // The DataTables library used to make the table interactive is a jQuery
      // plug-in, and so jQuery syntax is used in calling the library.
      const selector = '#' + tableId;
      $(selector).DataTable(dtOptions);           // eslint-disable-line new-cap
    } else {
      throw new HTTPError(`status code ${response.status}`);
    }
  } catch (error) {
    displayAppError(error, divElem, tableId);
  }
}


function addBootstrapStyle(tableId) {
  const table = document.getElementById(tableId);
  const classArgs = ['table', 'table-primary', 'table-striped'];
  table.classList.add(...classArgs);
}


const odDeathsTable = document.getElementById('od-deaths-table-pane');
void addTable(odDeathsTable, '/tables/od-deaths-table', 'od-deaths-table');
const populationTable = document.getElementById('population-table-pane');
void addTable(populationTable, '/tables/population-table', 'population-table');
