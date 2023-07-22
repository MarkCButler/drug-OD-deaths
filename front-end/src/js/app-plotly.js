/**
 * After importing the components of plotly needed by the app, export the Plotly
 * object for use by other modules in the app.
 * @module app-plotly
 */

'use strict';

// The dependencies being imported by this module use CommonJS syntax for
// imports and exports.  In particular, the arguments to the function
// Plotly.register are defined by module.exports objects in plotly.js/lib/core.
// To simplify the code required to obtain the correct arguments to
// Plotly.register, the current module uses the CommonJS syntax for imports and
// exports, rather than ES6 syntax used in the rest of the od_deaths project.
//
// Note that 'use strict' is needed in this module in order to enforce strict
// mode in the webpack build output, unlike in the modules that use ES6 syntax
// for import/export.

const Plotly = require('plotly.js/lib/core');

// Load in the trace types needed for the app.
Plotly.register([
  require('plotly.js/lib/scatter'),
  require('plotly.js/lib/choropleth')]
);

// Export the custom build
module.exports = Plotly;
