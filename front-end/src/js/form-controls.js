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
      const controlsToUpdate = metadata.controls.filter(
        control => control.optionsUpdate
      );
      const extractedMetadata = {
        url: metadata.url,
        plotId: metadata.plotId,
        headingsToUpdate: metadata.headingUpdate,
        controlsToUpdate: controlsToUpdate
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

// Extract an array of metadata for all interactive form controls.  This is used
// below to create the array selectizeIds.
const formControlMetadata = plotMetadata.reduce(
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
const selectizeIds = formControlMetadata.reduce(
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
  addPlotListeners(formId, metadata);
  addOptionsListeners(formId, metadata);
  if (metadata.headingsToUpdate) {
    addHeadingsListeners(formId, metadata);
  }
}


function addPlotListeners(formId, metadata) {
  const form = document.getElementById(formId);
  const plotDiv = document.getElementById(metadata.plotId);

  form.addEventListener('change', () => {
    const paramString = getParamString(form);
    fetchJson(metadata.url, paramString)
      .then(json => updatePlot(json, plotDiv))
      .catch(error => displayAppError(error, plotDiv, metadata.plotId));
  });
}


function addOptionsListeners(formId, metadata) {
  const form = document.getElementById(formId);
  // For each form control that needs to be updated in a listener, create an
  // object containing metadata and HTML elements used during the update
  // process.
  const controlUpdateObjects = metadata.controlsToUpdate.map(
    getControlUpdateObject
  );

  form.addEventListener('change', () => {
    const paramString = getParamString(form);
    controlUpdateObjects.forEach(
      ({url, ...elements}) => {
        if (elements.triggeringElements.includes(event.target)) {
          const selectElement = elements.selectElement;
          fetchJson(url, paramString)
            .then(json =>
              updateSelectOptions(json, selectElement, elements.allOptions)
            )
            .catch(error =>
              displayAppError(error, elements.divAncestor, selectElement.id)
            );
        }
      }
    );
  });
}


function addHeadingsListeners(formId, metadata) {
  const form = document.getElementById(formId);
  // For each heading that needs to be updated in a listener, create an object
  // containing metadata and HTML elements used during the update process.
  const headingUpdateObjects = metadata.headingsToUpdate.map(
    getHeadingUpdateObject
  );

  form.addEventListener('change', () => {
    const paramString = getParamString(form);
    headingUpdateObjects.forEach(
      ({url, ...elements}) => {
        if (elements.triggeringElements.includes(event.target)) {
          const headingElement = elements.headingElement;
          fetchText(url, paramString)
            .then(text => {
              headingElement.textContent = text;
            })
            .catch(
              error => displayAppError(error, headingElement, headingElement.id)
            );
        }
      }
    );
  });
}


function getParamString(form) {
  const formData = new FormData(form);
  return new URLSearchParams(formData).toString();
}


/**
 * Return an object that facilitates updating the options of an HTML select
 * element.
 * @param {Object} controlMetadata - object containing metadata about the select
 *     element for which options should be updated
 * @returns {Object} object containing metadata and HTML elements used during
 *     the update process
 */
function getControlUpdateObject(controlMetadata) {
  const selectElement = document.getElementById(controlMetadata.controlId);
  const optionsUpdate = controlMetadata.optionsUpdate;
  const controlUpdateObject = {
    url: optionsUpdate.url,
    selectElement: selectElement,
    // Use the closest div ancestor to display any error message.
    divAncestor: selectElement.closest('div'),
    triggeringElements: optionsUpdate.triggeringElementIds.map(
      document.getElementById, document
    )
  };

  // Add an object allOptions that stores all options initially created for the
  // select element.  The key-value pairs are of the form
  // { <option value>: <option> }
  const allOptions = {};

  if (selectElement.classList.contains('selectized')) {
    // Options are stored as objects.
  } else {
    // Options are stored as HTML option elements.
    for (const option of selectElement.options) {
      allOptions[option.value] = option;
    }
    controlUpdateObject['allOptions'] = allOptions;
  }

  return controlUpdateObject;
}


/**
 * Update the options for a select element using JSON received from the back
 * end.
 * @param {Array} json - Array of option values that the select element should
 *     have after the update
 * @param {HTMLElement} selectElement - The select element for which the options
 *     should be updated
 * @param {Object} allOptions - An object that stores all options initially
 *     created for the select element.  Each key-value pair is of the form
 *     { <option value>: <option> }.
 */
function updateSelectOptions(json, selectElement, allOptions) {
  if (selectElement.classList.contains('selectized')) {
    // TODO: Add a function to do the update for a selectized element.
  } else {
    updateHTMLSelectElement(json, selectElement, allOptions);
  }
}


function updateHTMLSelectElement(requiredValues, selectElement, allOptions) {
  // Iterate over requiredValues, modifying the options in selectElement.options
  // as needed.
  requiredValues.forEach((requiredValue, index) => {
    const currentOption = selectElement.options[index];
    if (currentOption) {
      // If selectElement.options[index] exists but does not have the value
      // given by requiredValue, add or remove an option from
      // selectElement.options.
      if (requiredValue !== currentOption.value) {
        // If the value of the next option in selectElement is equal to
        // requiredValue, then remove currentOption from the select element.
        // Otherwise, add an option with the required value.
        const nextOptionValue = selectElement.options[index+1].value;
        if (requiredValue === nextOptionValue) {
          selectElement.remove(index);
        } else {
          selectElement.add(allOptions[requiredValue], currentOption);
        }
      }
    } else {
      // If selectElement.options[index] does not exist, just add an option for
      // the next required value to the end of selectElement.options.
      selectElement.add(allOptions[requiredValue]);
    }
  });

  // Discard any options remaining at the end of selectElement.options after the
  // loop.
  selectElement.options.length = requiredValues.length;
}


/**
 * Return an object that facilitates updating an HTML heading associated with a
 * plot.
 * @param {Object} headingMetadata - object containing metadata about the HTML
 *     heading to be updated
 * @returns {Object} object containing metadata and HTML elements used during
 *     the update process
 */
function getHeadingUpdateObject(headingMetadata) {
  return {
    url: headingMetadata.url,
    headingElement: document.getElementById(headingMetadata.headingId),
    triggeringElements: headingMetadata.triggeringElementIds.map(
      document.getElementById, document
    )
  };
}
