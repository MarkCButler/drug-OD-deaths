'use strict';

export const plotMetadata = [
  {
    plotId: 'test-line-plot',
    url: '/plots/test-line-plot',
    tabPane: 'summary',
    controls: null
  },
  {
    plotId: 'dummy-line-plot',
    url: '/plots/test-line-plot',
    tabPane: 'summary',
    controls: null
  },
  {
    plotId: 'test-map-plot',
    url: 'plots/test-map-plot',
    tabPane: 'summary',
    controls: null
  },
  {
    plotId: 'interactive-map-plot',
    url: 'plots/test-map-plot',
    tabPane: 'map',
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
    tabPane: 'time-dev',
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
