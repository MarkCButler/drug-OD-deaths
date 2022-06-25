'use strict';

import Plotly from 'plotly.js/dist/plotly-basic.js';


class HTTPError extends Error {
  constructor(message) {
    super(message);
    this.name = 'HTTPError';
  }
}


function addPlot(divElem, url, plotName) {
  fetch(url)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new HTTPError(`status code ${response.status}`);
        }
      })
      .then((plotJSON) => {
        const config = {responsive: true};
        const data = plotJSON['data'];
        const layout = plotJSON['layout'];
        Plotly.newPlot(testPlot, data, layout, config);
      })
      .catch((error) => {
        testPlot.classList.add('h3', 'text-warning');
        testPlot.innerHTML = `<p>Failed to fetch or generate ${plotName}.</p>` +
                             `<p>${error}</p>`;
      });
}

const testPlot = document.getElementById('test-plot');
addPlot(testPlot, '/test-plot', 'test-plot');
