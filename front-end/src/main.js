'use strict';

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

// Add plots and tables, along with associated controls and event listeners, to
// the DOM.
import './js/plots';
import './js/form-controls';
import './js/tables';
