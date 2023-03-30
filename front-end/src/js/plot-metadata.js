'use strict';

export const plotMetadata = [
  {
    plotId: 'epidemic-peak',
    url: '/plots/test-line-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: null
  },
  {
    plotId: 'growth-rate',
    url: '/plots/test-line-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: null
  },
  {
    plotId: 'distribution',
    url: 'plots/test-map-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: null
  },
  {
    plotId: 'interactive-map-plot',
    url: 'plots/test-map-plot',
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
    url: '/plots/test-line-plot',
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
