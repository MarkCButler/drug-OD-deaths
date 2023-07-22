/**
 * Export a function that customizes form controls and adds event listeners
 * needed for the app's interactivity.
 * @module forms
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
export function initializeForms() {
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
        headingsToUpdate: metadata.headingsToUpdate,
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

// Settings for the selectize library.
const selectizeSettings = {
  plugins: ['remove_button'],
  valueField: 'value',
  labelField: 'text'
};


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
    // console.log('Dispatched ', changeEvent);
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
      onChange: getSelectizeChangeHandler(controlId),
      ...selectizeSettings
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
  return {
    url: optionsUpdate.url,
    selectElement: selectElement,
    // Use the closest div ancestor to display any error message.
    divAncestor: selectElement.closest('div'),
    triggeringElements: optionsUpdate.triggeringElementIds.map(
      document.getElementById, document
    ),
    // Store all options initially created for the select element.
    allOptions: getAllOptions(selectElement)
  };
}


/**
 * Return an object that stores all options initially created for an HTML select
 * element
 * @param {HTMLSelectElement} selectElement
 * @returns {Object} object that stores all options initially created for the
 *     select element.  The object keys are option values. If the selectize
 *     library has been used to enhance the functionality of the select element,
 *     the object values are option text labels displayed in the UI; otherwise,
 *     the object values are HTMLOptionElements.
 */
function getAllOptions(selectElement) {
  const allOptions = {};
  if (selectElement.classList.contains('selectized')) {
    const selectizeOptions = selectElement.selectize.options;
    for (const key of Object.keys(selectizeOptions)) {
      allOptions[key] = selectizeOptions[key]['text'];
    }
  } else {
    for (const option of selectElement.options) {
      allOptions[option.value] = option;
    }
  }
  return allOptions;
}


/**
 * Update the options for an HTML select element.
 * @param {Array} optionValues - Array of option values that the select element
 *     should have after the update
 * @param {HTMLSelectElement} selectElement - The select element for which the
 *     options should be updated
 * @param {Object} allOptions - An object that stores all options initially
 *     created for the select element.  The object keys are option values. If
 *     the selectize library has been used to enhance the functionality of the
 *     select element, the object values are option text labels displayed in the
 *     UI; otherwise, the object values are HTMLOptionElements.
 */
function updateSelectOptions(optionValues, selectElement, allOptions) {
  if (selectElement.classList.contains('selectized')) {
    updateSelectizedElement(optionValues, selectElement, allOptions);
  } else {
    updateHTMLSelectElement(optionValues, selectElement, allOptions);
  }
}


function updateSelectizedElement(optionValues, selectElement, allOptions) {
  // The reason that keys 'value' and 'text' are used below in updatedOptions is
  // that selectizeSettings defines these as the valueField and labelField,
  // respectively.
  const updatedOptions = optionValues.map(
    value => ({
      'value': value,
      'text': allOptions[value]
    })
  );
  const selectedValues = selectElement.selectize.items.filter(
    value => optionValues.includes(value)
  );
  if (selectedValues.length === 0) {
    selectedValues[0] = optionValues[0];
  }
  const selectizeControl = selectElement.selectize;
  selectizeControl.clear();
  selectizeControl.clearOptions(true);
  selectizeControl.addOption(updatedOptions);
  selectizeControl.setValue(selectedValues);
  selectizeControl.refreshState(false);
}


function updateHTMLSelectElement(optionValues, selectElement, allOptions) {
  // Iterate over optionValues, modifying the options in selectElement.options
  // as needed.
  optionValues.forEach((optionValue, index) => {
    const currentOption = selectElement.options[index];
    if (currentOption) {
      // If selectElement.options[index] exists but does not have the value
      // given by optionValue, add or remove an option from
      // selectElement.options.
      if (optionValue !== currentOption.value) {
        // If the value of the next option in selectElement is equal to
        // optionValue, then remove currentOption from the select element.
        // Otherwise, add an option with the required value.
        const nextOptionValue = selectElement.options[index+1].value;
        if (optionValue === nextOptionValue) {
          selectElement.remove(index);
        } else {
          selectElement.add(allOptions[optionValue], currentOption);
        }
      }
    } else {
      // If selectElement.options[index] does not exist, just add an option for
      // the next required value to the end of selectElement.options.
      selectElement.add(allOptions[optionValue]);
    }
  });

  // Discard any options remaining at the end of selectElement.options after the
  // loop.
  selectElement.options.length = optionValues.length;
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
