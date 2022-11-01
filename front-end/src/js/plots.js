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
      const config = {
        responsive: true,
        displayModeBar: false,
        scrollZoom: false
      };
      Plotly.newPlot(divElem, plotJSON.data, plotJSON.layout, config);
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

const plotIDs = ['test-line-plot', 'test-map-plot'];
for (const plotID of plotIDs) {
  const testPlot = document.getElementById(plotID);
  void addPlot(testPlot, `/plots/${plotID}`, plotID);
}


// Plotly objects do not natively understand bootstrap events, so we need to add
// handlers to resize plots after to certain bootstrap events:
//   1. After the sidebar has been hidden or shown, which corresponds to events
//   hidden.bs.collapse, shown.bs.collapse on the sidebar.
//   2. After a tab pane has been hidden or shown, which corresponds to events
//   hidden.bs.tab, shown.bs.tab on the tab pane.
// When the sidebar or tab is visible, it will have the CSS class show.
const tabPaneIDs = ['summary', 'map', 'time-dev', 'data', 'notes'];
const tabPanes = tabPaneIDs.map((id) => document.getElementById(id));
const sidebar = document.getElementById('sidebar');


function resizeTabPanePlots(tabPane) {
  const plots = tabPane.querySelectorAll('.od-deaths-plot');
  for (const plot of plots) {
    Plotly.Plots.resize(plot);
  }
}


function refreshTabPanes() {
  for (const tabPane of tabPanes) {
    // If a tabPane is visible, resize the plots contained in it.
    if (tabPane.classList.contains('show')) {
      resizeTabPanePlots(tabPane);
      break;
    }
  }
}

// Add event listeners to resize plots after the sidebar is toggled.
['hidden.bs.collapse', 'shown.bs.collapse'].forEach(
    (eventType) => sidebar.addEventListener(eventType, refreshTabPanes)
);

// Add event listener to resize the plots of a tab that has just been made
// visible.
sidebar.addEventListener('shown.bs.tab', (event) => {
  const idSelector = event.target.dataset.bsTarget;
  const tabPane = document.querySelector(idSelector);
  resizeTabPanePlots(tabPane);
});
