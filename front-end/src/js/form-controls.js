/**
 * @fileoverview Export a function that customizes form controls and adds event
 * listeners needed for the app's interactivity.
 */

// Import the selectize library and its dependency jquery.
import $ from 'jquery';
import '@selectize/selectize';

import {plotMetadata} from './plot-metadata';
import {updatePlot} from './plots';


export function initializeFormControls() {
  selectizeIds.forEach(controlId => {
    // The selectize library used to enhance the select elements is a jquery
    // plug-in, and so jquery syntax is used in calling the library.
    const selector = '#' + controlId;
    $(selector).selectize({
      plugins: ['remove_button'],
      onChange: getSelectizeChangeHandler(controlId)
    });
  });

  for (const [formId, metadata] of Object.entries(formMetadata)) {
    const form = document.getElementById(formId);
    form.addEventListener('change', () => {
      const formData = new FormData(form);
      const params = new URLSearchParams(formData);
      updatePlot(metadata.plotId, metadata.url, params.toString());
    });
  }
}


// Create an object mapping form IDs to back-end URLs.
const formMetadata = plotMetadata.reduce(
  (accumObj, metadata) => {
    if (metadata.formId) {
      return {
        ...accumObj,
        [metadata.formId]: {url: metadata.url, plotId: metadata.plotId}
      };
    }
    return accumObj;
  },
  []
);

// Extract an array of metadata for all interactive plot controls.  This is used
// below to create the array selectizeIds.
const plotControlMetadata = plotMetadata.reduce(
  (accumArray, metadata) => {
    if (metadata.controls) {
      return [...accumArray, ...metadata.controls];
    }
    return accumArray;
  },
  []
);

// Extract an array of IDs for form controls that should be modified with the
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


// The cost of using the selectize library on a form control is that the
// control's behavior no longer follows the HTML standard.  In particular, a
// "selectized" form control does not dispatch a standard 'change' event.  The
// workaround offered by the library is the ability to define a custom handler
// that runs when a change occurs in the selectized form control.
function getSelectizeChangeHandler(controlId) {
  return function() {
    const formControl = document.getElementById(controlId);
    // Dispatch an event that will be handled by the form.
    const changeEvent = new Event('change', {bubbles: true});
    formControl.dispatchEvent(changeEvent);
  };
}
