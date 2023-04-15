/**
 * @fileoverview Export a function that customizes form controls and adds event
 * listeners needed for the app's interactivity.
 */

// Import the selectize library and its dependency jquery.
import $ from 'jquery';
import '@selectize/selectize';

import {fetchJson, fetchText} from './app-fetch';
import {plotMetadata} from './plot-metadata';
import {updatePlot} from './plots';
import {displayAppError} from './errors';


/**
 * Customize form controls and add event listeners.
 */
export function initializeFormControls() {
  applySelectize();
  for (const [formId, metadata] of Object.entries(formMetadata)) {
    addFormListeners(formId, metadata);
  }
}


// Create an object mapping form ID to metadata about dynamic updates that
// should occur when form values are modified interactively.
const formMetadata = plotMetadata.reduce(
  (accumObj, metadata) => {
    if (metadata.formId) {
      const extractedMetadata = {
        url: metadata.url,
        plotId: metadata.plotId,
        headings: metadata.headings
      };
      return {
        ...accumObj,
        [metadata.formId]: extractedMetadata
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


// For the form-control IDs in the array selectizeIds, use the selectize
// library to enhance the features of the form control.
function applySelectize() {
  selectizeIds.forEach(controlId => {
    // The selectize library used to enhance the select elements is a jquery
    // plug-in, and so jquery syntax is used in calling the library.
    const selector = '#' + controlId;
    $(selector).selectize({
      plugins: ['remove_button'],
      onChange: getSelectizeChangeHandler(controlId)
    });
  });
}


function addFormListeners(formId, metadata) {
  makePlotAndOptionsInteractive(formId, metadata);
  if (metadata.headings) {
    makeHeadingsInteractive(formId, metadata);
  }
}


function makePlotAndOptionsInteractive(formId, metadata) {
  const form = document.getElementById(formId);
  const plotDiv = document.getElementById(metadata.plotId);

  form.addEventListener('change', () => {
    const paramString = getParamString(form);
    const jsonPromise = fetchJson(metadata.url, paramString);
    jsonPromise
      .then(json => updatePlot(plotDiv, json))
      .catch(error => displayAppError(error, plotDiv, metadata.plotId));
    // Add another .then and .catch to handle updating the form options.
  });
}


function makeHeadingsInteractive(formId, metadata) {
  const form = document.getElementById(formId);

  form.addEventListener('change', () => {
    const paramString = getParamString(form);
    metadata.headings.forEach(headingMetadata => {
      const headingId = headingMetadata.headingId;
      const headingElement = document.getElementById(headingId);
      fetchText(headingMetadata.url, paramString)
        .then(text => {
          headingElement.textContent = text;
        })
        .catch(error => displayAppError(error, headingElement, headingId));
    });
  });
}


function getParamString(form) {
  const formData = new FormData(form);
  return new URLSearchParams(formData).toString();
}
