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

const testTable = document.getElementById('od-deaths-table');
void addTable(testTable, '/tables/od-deaths-table', 'od-deaths-table');
