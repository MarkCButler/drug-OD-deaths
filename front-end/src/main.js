'use strict';

// main.scss includes the following:
// 1. A customized subset of bootstrap scss
// 2. The scss for the bootswatch theme
// 3. The css for the datatables library
// 4. The css for the selectize library
import './scss/main.scss';

// Import subsets of the javascript for bootstrap 5 and fontawesome.
import './js/app-bootstrap';
import './js/app-fontawesome';

// Add plots/tables and associated event listeners to the DOM.
import './js/plots';
import './js/tables';
