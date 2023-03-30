'use strict';

// Import a subset of the javascript for plotly.
import Plotly from './app-plotly';

import {displayAppError, HTTPError} from './errors';
import {plotMetadata} from './plot-metadata';

// Class added to the html DOM element by fontawesome to indicate the rendering
// of the SVG icons is complete.
const ICONS_RENDERED = 'fontawesome-i2svg-complete';


export function updatePlot(plotId, url, paramString) {
  console.log(plotId);
  console.log(url);
  console.log(paramString);
  const plotDiv = document.getElementById(plotId);
  // TODO: Call getPlotJSON and use Plotly.react to update the plot
}


////////////////////////////////////////////////////////////////////////////////
// Add plotly figures to the app's DOM
////////////////////////////////////////////////////////////////////////////////

// The figures in the summary tab (which is displayed when the app is first
// loaded) need to be handled differently than the figures in other tabs.
//
// For the summary tab, the requirement is that plotly figures are not added to
// the DOM until all SVG icons have been rendered by fontawesome.  The reason is
// that as SVG icons are rendered, the space available for the app's figures
// changes.  Since the figures are autosized to fit the available space, a race
// condition between figure rendering and icon rendering can lead to
// misalignment of figures.
//
// The other tabs that contain figures are initially not visible.  If a plotly
// figure is added to a tab that is not visible, the autosize algorithm used
// by plotly fails, and the figure is assigned a default size.  Failure of the
// autosize algorithm affects the responsivity of the figure in subtle ways that
// break the responsive boostrap layout. In particular, if the autosize
// algorithm is successful, the figure is enclosed by div of class
// "svg-container" with a style attribute "width:100%," but if the autosize
// algorithm is not successful, this width is given in pixels.  If
// config.responsive is set to true for the figure, then this width in pixels
// will be updated when the window is resized.  A race condition can develop
// between updates of this width in pixels and the changes associated with the
// responsive bootstrap layout.  The layout that you get depends on how quickly
// you resize the window.
//
// In order to avoid this race condition, plots are not added to a tab until it
// is visible for the first time.
const visiblePlotMetadata = plotMetadata.filter(
  metadata => metadata.visibleOnLoad
);
const hiddenPlotMetadata = plotMetadata.filter(
  metadata => !metadata.visibleOnLoad
);

const plotlyConfig = {
  responsive: true,
  displayModeBar: false,
  scrollZoom: false
};


async function getPlotJSON(plotDiv, url, paramString) {
  const response = await fetch(url + '?' + paramString);
  if (response.ok) {
    return response.json();
  } else {
    throw new HTTPError(`status code ${response.status}`);
  }
}


function addPlotsFromMetadata(metadataArray) {
  metadataArray.forEach(metadata => {
    const plotDiv = document.getElementById(metadata.plotId);
    const paramString = getParamString(metadata.formId, plotDiv);
    getPlotJSON(plotDiv, metadata.url, paramString)
      .then(plotJSON => {
        Plotly.newPlot(plotDiv, plotJSON.data, plotJSON.layout, plotlyConfig);
      })
      .catch(error => displayAppError(error, plotDiv, metadata.plotId));
  });
}


function getParamString(formId, plotDiv) {
  if (formId) {
    return getFormParamString(formId);
  } else {
    return getParamStringFromDataset(plotDiv);
  }
}


function getFormParamString(formId) {
  const formData = new FormData(document.getElementById(formId));
  return new URLSearchParams(formData).toString();
}


function getParamStringFromDataset(plotDiv) {
  const paramArray = JSON.parse(plotDiv.dataset.odPlotParams);
  const formData = new FormData();
  paramArray.forEach((name, value) => {
    formData.append(name, value);
  });
  return new URLSearchParams(formData).toString();
}


// Create a MutationObserver to add plots to the summary pane after SVG
// rendering is completed.  As explained at
// https://fontawesome.com/v5/docs/web/advanced/svg-asynchronous-loading
// the class fontawesome-i2svg-complete is added to the html tag once the
// rendering process is complete.
const observer = new MutationObserver((mutationList, observer) => {
  for (const mutation of mutationList) {
    if (mutation.type === 'attributes' &&
        mutation.target.classList.contains(ICONS_RENDERED)) {
      addPlotsFromMetadata(visiblePlotMetadata);
      observer.disconnect();
      break;
    }
  }
});

if (document.documentElement.classList.contains(ICONS_RENDERED)) {
  addPlotsFromMetadata(visiblePlotMetadata);
} else {
  observer.observe(document.documentElement, {
    attributeFilter: ['class']
  });
}

// For each plot in a hidden tab pane, fetch the JSON describing the plot from
// the server and set up an event listener to create the plot as soon as the tab
// pane becomes visible.  As explained above, plotly's autosize algorithm fails
// if the plot is generated before the tab pane is visible, which can lead to a
// race condition between plotly resizing and bootstrap updates of the layout.
hiddenPlotMetadata.forEach(metadata => {
  const tab = document.getElementById(metadata.tabId);
  const plotDiv = document.getElementById(metadata.plotId);
  const paramString = getParamString(metadata.formId, plotDiv);
  getPlotJSON(plotDiv, metadata.url, paramString)
    .then(plotJSON => {
      tab.addEventListener('shown.bs.tab', () => {
        Plotly.newPlot(plotDiv, plotJSON.data, plotJSON.layout, plotlyConfig);
      }, {once: true});
    })
    .catch(error => displayAppError(error, plotDiv, metadata.plotId));
});

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

// TODO:  Consider adding code to give a reasonable aspect ratio as the width of
//   the viewport decreases.
