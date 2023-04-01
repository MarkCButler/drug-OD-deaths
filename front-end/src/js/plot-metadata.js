'use strict';

export const plotMetadata = [
  {
    plotId: 'epidemic-peak',
    url: '/plots/time-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: null
  },
  {
    plotId: 'growth-rate',
    url: '/plots/time-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: null
  },
  {
    plotId: 'distribution',
    url: 'plots/map-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: null
  },
  {
    plotId: 'interactive-map-plot',
    url: 'plots/map-plot',
    visibleOnLoad: false,
    formId: 'map-plot-form',
    tabId: 'map-tab',
    controls: [
      {
        controlId: 'select-map-plot-statistic',
        selectize: false
      },
      {
        controlId: 'select-map-plot-period',
        selectize: false
      }
    ]
  },
  {
    plotId: 'interactive-time-plot',
    url: '/plots/time-plot',
    visibleOnLoad: false,
    formId: 'time-plot-form',
    tabId: 'time-dev-tab',
    controls: [
      {
        controlId: 'select-time-plot-location',
        selectize: false
      },
      {
        controlId: 'select-time-plot-statistic',
        selectize: false
      },
      {
        controlId: 'select-time-plot-od-type',
        selectize: true
      }
    ]
  }
];
