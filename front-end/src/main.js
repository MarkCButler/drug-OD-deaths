/**
 * @fileoverview After importing third-party modules for side effects, add
 * plots, tables, and event listeners to the DOM.
 */

// main.scss includes the following:
// 1. A customized subset of bootstrap scss
// 2. The scss for the bootswatch theme
// 3. The css for the datatables library
// 4. The css for the selectize library
import './scss/main.scss';

// Import subsets of the javascript for fontawesome and bootstrap 5.  The import
// of app-fontawesome should occur first, because it causes SVG icons to be
// loaded asynchronously.  As these icons are rendered, the space available for
// the app's plots changes, and as a result, plots should be not loaded until
// after rendering of SVG icons is complete.
//
// In contrast, the import of app-bootstrap, which enables toggling the sidebar
// and switching tab content, does not need to block rendering of the plots.
import './js/app-fontawesome';
import './js/app-bootstrap';

// In order to optimize the user's experience with the app, the work done by the
// front end when the app is loaded needs to occur in a series of steps:
//
//   1. As discussed in a detailed comment in ./js/plots.js, the plots that are
//      initially visible when the app is loaded must not be added to the DOM
//      until after all SVG icons have been rendered by fontawesome.
//   2. Other plots and tables that require a query to the back end should not
//      be added to the DOM until after the plots that are initially visible
//      have been rendered.  We do not want to delay the rendering of the app's
//      introductory page while tables on pane that is initially hidden are
//      fetched and added to the DOM.
//
// The three modules imported below do not have side effects. Instead, they
// export functions that can be executed in a chain of .then handlers in order
// to ensure that elements are added to the DOM in the desired order.
import {initializePlots} from './js/plots';
import {initializeForms} from './js/forms';
import {initializeTables} from './js/tables';


/**
 * Asynchronously add plots and tables to the DOM along with event listeners
 * needed for interactivity.
 */
function initialize() {
  initializePlots()
    .then(
      () => {
        initializeForms();
        // Without the void operator, the IDE warns that the promise returned
        // from the function call below is ignored.  Like initializePlots,
        // initializeTables represents a time-consuming operation, and so it
        // returns a promise.  Here initializeTables is the final step in
        // initializing the DOM, and so the promise is ignored.
        void initializeTables();
      }
    );
}


// Class added to the html DOM element by fontawesome to indicate the rendering
// of the SVG icons is complete.  See:
// https://fontawesome.com/v5/docs/web/advanced/svg-asynchronous-loading
const ICONS_RENDERED = 'fontawesome-i2svg-complete';

// Create a MutationObserver to add plots to the summary pane after SVG
// rendering is completed.
const observer = new MutationObserver((mutationList, observer) => {
  for (const mutation of mutationList) {
    if (mutation.type === 'attributes' &&
      mutation.target.classList.contains(ICONS_RENDERED)) {
      initialize();
      observer.disconnect();
      break;
    }
  }
});

if (document.documentElement.classList.contains(ICONS_RENDERED)) {
  initialize();
} else {
  observer.observe(document.documentElement, {
    attributeFilter: ['class']
  });
}
