'use strict';

import Plotly from './app-plotly';


class HTTPError extends Error {
  constructor(message) {
    super(message);
    this.name = 'HTTPError';
  }
}


async function addPlot(divElem, url, plotName) {
  try {
    const response = await fetch(url);
    if (response.ok) {
      const plotJSON = await response.json();
      Plotly.newPlot(divElem, plotJSON);
    } else {
      throw new HTTPError(`status code ${response.status}`);
    }
  } catch (error) {
    displayPlotError(error, divElem, plotName);
  }
}


function displayPlotError(error, divElem, plotName) {
  if (!divElem.classList.contains('h3')) {
    divElem.classList.add('h3');
  }
  if (!divElem.classList.contains('text-warning')) {
    divElem.classList.add('text-warning');
  }
  divElem.innerHTML = `<p>Failed to fetch or generate ${plotName}.</p>` +
                      `<p>${error}</p>`;
}

// TODO: In updating plots, use Plotly.react

const testPlot = document.getElementById('test-plot');
void addPlot(testPlot, '/plots/test-plot', 'test-plot');
