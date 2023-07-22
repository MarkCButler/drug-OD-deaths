/**
 * Export an array of metadata needed for initializing plots and for adding
 * event listeners to the forms associated with plots.  The metadata in this
 * array allows functions defined in other modules to make changes to the DOM
 * without hard-coding details of the DOM.
 * @module plot-metadata
 */

export const plotMetadata = [
  {
    plotId: 'epidemic-peak',
    url: '/plots/time',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: [],
    headingsToUpdate: []
  },
  {
    plotId: 'growth-rate',
    url: '/plots/time',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: [],
    headingsToUpdate: []
  },
  {
    plotId: 'distribution',
    url: 'plots/map',
    visibleOnLoad: true,
    formId: null,
    tabId: 'summary',
    controls: [],
    headingsToUpdate: []
  },
  {
    plotId: 'interactive-map-plot',
    url: 'plots/map',
    visibleOnLoad: false,
    formId: 'map-plot-form',
    tabId: 'map-tab',
    controls: [
      {
        controlId: 'select-map-plot-statistic',
        selectize: false,
        optionsUpdate: {
          url: '/form-options/map-plot-statistic',
          triggeringElementIds: ['select-map-plot-period']
        }
      },
      {
        controlId: 'select-map-plot-period',
        selectize: false,
        optionsUpdate: {
          url: '/form-options/map-plot-period',
          triggeringElementIds: ['select-map-plot-statistic']
        }
      }
    ],
    headingsToUpdate: [
      {
        headingId: 'map-plot-title-1',
        url: '/headings/map-plot-heading',
        triggeringElementIds: [
          'select-map-plot-statistic'
        ]
      },
      {
        headingId: 'map-plot-title-2',
        url: '/headings/map-plot-subheading',
        triggeringElementIds: [
          'select-map-plot-statistic',
          'select-map-plot-period'
        ]
      }
    ]
  },
  {
    plotId: 'interactive-time-plot',
    url: '/plots/time',
    visibleOnLoad: false,
    formId: 'time-plot-form',
    tabId: 'time-dev-tab',
    controls: [
      {
        controlId: 'select-time-plot-location',
        selectize: false,
        optionsUpdate: null
      },
      {
        controlId: 'select-time-plot-statistic',
        selectize: false,
        optionsUpdate: null
      },
      {
        controlId: 'select-time-plot-od-type',
        selectize: true,
        optionsUpdate: {
          url: '/form-options/time-plot-od-type',
          triggeringElementIds: ['select-time-plot-location']
        }
      }
    ],
    headingsToUpdate: [
      {
        headingId: 'time-plot-title-1',
        url: '/headings/time-plot-heading',
        triggeringElementIds: ['select-time-plot-statistic']
      },
      {
        headingId: 'time-plot-title-2',
        url: '/headings/time-plot-subheading',
        triggeringElementIds: ['select-time-plot-location']
      }
    ]
  }
];
