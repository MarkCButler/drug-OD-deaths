/**
 * @fileoverview Export an array of metadata needed for initializing plots and
 * for adding event listeners to the forms associated with plots.  The metadata
 * in this array allows functions defined in other modules to make changes to
 * the DOM without hard-coding details of the DOM.
 */

export const plotMetadata = [
  {
    plotId: 'epidemic-peak',
    url: '/plots/time-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    headings: null,
    controls: null
  },
  {
    plotId: 'growth-rate',
    url: '/plots/time-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    headings: null,
    controls: null
  },
  {
    plotId: 'distribution',
    url: 'plots/map-plot',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    headings: null,
    controls: null
  },
  {
    plotId: 'interactive-map-plot',
    url: 'plots/interactive-map-plot',
    visibleOnLoad: false,
    formId: 'map-plot-form',
    tabId: 'map-tab',
    headings: [
      {
        headingId: 'map-plot-title-1',
        url: '/headings/map-plot-heading'
      },
      {
        headingId: 'map-plot-title-2',
        url: '/headings/map-plot-subheading'
      }
    ],
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
    url: '/plots/interactive-time-plot',
    visibleOnLoad: false,
    formId: 'time-plot-form',
    tabId: 'time-dev-tab',
    headings: [
      {
        headingId: 'time-plot-title-1',
        url: '/headings/time-plot-heading'
      },
      {
        headingId: 'time-plot-title-2',
        url: '/headings/time-plot-subheading'
      }
    ],
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
