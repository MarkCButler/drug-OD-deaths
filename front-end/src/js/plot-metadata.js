'use strict';

export const plotMetadata = [
  {
    plotId: 'test-line-plot',
    url: '/plots/test-line-plot',
    visibleOnLoad: true,
    controls: null
  },
  {
    plotId: 'dummy-line-plot',
    url: '/plots/test-line-plot',
    visibleOnLoad: true,
    controls: null
  },
  {
    plotId: 'test-map-plot',
    url: 'plots/test-map-plot',
    visibleOnLoad: true,
    controls: null
  },
  {
    plotId: 'interactive-map-plot',
    url: 'plots/test-map-plot',
    visibleOnLoad: false,
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
