'use strict';

import {displayAppError, HTTPError} from './errors';
import Plotly from './app-plotly';


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
    displayAppError(error, divElem, plotName);
  }
}


// TODO: In updating plots, use Plotly.react
const plotIDs = ['test-line-plot', 'dummy-line-plot', 'test-map-plot'];
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
const tabPanes = tabPaneIDs.map(id => document.getElementById(id));
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

// In chrome when the app is first loaded, one or more of the plots on the
// summary page are a bit wider the parent container.  As a result, the plots
// are not aligned on the right, which is distracting. If the window is resized,
// or if any action in the UI causes plots to be resized (such as toggling the
// sidebar), the problem is fixed and does not appear again.  The problem
// appears to be due to a bug in plotly, because in a set of nested plotly
// elements, an inner svg element has a calculated value in px that is too
// large.  If the sidebar is toggled twice (to return to the initial state of
// the UI), the calculated value of this inner svg element is corrected.
//
// As a workaround for this problem, repeat the step of adding the plots to the
// summary tab.  After the step has been repeated, all plots have the correct
// width.
for (const plotID of plotIDs) {
  const testPlot = document.getElementById(plotID);
  void addPlot(testPlot, `/plots/${plotID}`, plotID);
}
