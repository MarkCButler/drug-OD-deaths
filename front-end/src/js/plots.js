'use strict';

// Import a subset of the javascript for plotly.
import Plotly from './app-plotly';

import {displayAppError, HTTPError} from './errors';
import {plotMetadata} from './plot-metadata';

////////////////////////////////////////////////////////////////////////////////
// Add Plotly figures to the app's DOM
////////////////////////////////////////////////////////////////////////////////
const plotlyConfig = {
  responsive: true,
  displayModeBar: false,
  scrollZoom: false
};


async function addPlot(divElem, {plotId, url}) {
  try {
    const response = await fetch(url);
    if (response.ok) {
      const plotJSON = await response.json();
      Plotly.newPlot(divElem, plotJSON.data, plotJSON.layout, plotlyConfig);
    } else {
      throw new HTTPError(`status code ${response.status}`);
    }
  } catch (error) {
    displayAppError(error, divElem, plotId);
  }
}


function addPlotsFromMetadata(metadataArray) {
  metadataArray.forEach(metadata => {
    const divElem = document.getElementById(metadata.plotId);
    void addPlot(divElem, metadata);
  });
}


addPlotsFromMetadata(plotMetadata);

////////////////////////////////////////////////////////////////////////////////
// Plotly objects do not natively understand bootstrap events, so we need to add
// handlers to resize plots after certain bootstrap events:
//   1. After the sidebar has been hidden or shown, which corresponds to events
//   hidden.bs.collapse, shown.bs.collapse on the sidebar.
//   2. After a tab pane has been hidden or shown, which corresponds to events
//   hidden.bs.tab, shown.bs.tab on the tab pane.
// When the sidebar or tab is visible, it will have the CSS class 'show'.
////////////////////////////////////////////////////////////////////////////////
const tabPanes = ['summary', 'map', 'time-dev'].map(
    id => document.getElementById(id)
);
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
    eventType => sidebar.addEventListener(eventType, refreshTabPanes)
);

// Add event listener to resize the plots of a tab that has just been made
// visible.
sidebar.addEventListener('shown.bs.tab', event => {
  const idSelector = event.target.dataset.bsTarget;
  const tabPane = document.querySelector(idSelector);
  resizeTabPanePlots(tabPane);
});
