'use strict';

// Import the selectize library and its dependency jquery.
import $ from 'jquery';
import '@selectize/selectize';

import {plotMetadata} from './plot-metadata';

// Extract an array of metadata for all interactive plot controls.
const plotControlMetadata = plotMetadata.reduce(
  (accumArray, metadata) => {
    if (metadata.controls) {
      return [...accumArray, ...metadata.controls];
    }
    return accumArray;
  },
  []
);

// Extract an array of IDs for controls that should be modified with the
// selectize library.
const selectizeIds = plotControlMetadata.reduce(
  (accumArray, metadata) => {
    if (metadata.selectize) {
      return [...accumArray, metadata.controlId];
    }
    return accumArray;
  },
  []
);

selectizeIds.forEach(controlId => {
  // The selectize library used to enhance the select elements is a jquery
  // plug-in, and so jquery syntax is used in calling the library.
  const selector = '#' + controlId;
  $(selector).selectize();
});

// TODO: In updating plots, use Plotly.react
