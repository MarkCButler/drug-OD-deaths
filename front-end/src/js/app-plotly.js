'use strict';

// The dependencies being imported by this module use CommonJS syntax for
// imports and exports.  In particular, the arguments to the function
// Plotly.register are defined by module.exports objects in plotly.js/lib.  To
// simplify the code required to obtain the correct arguments to
// Plotly.register, the current module uses the CommonJS syntax for imports and
// exports, rather than ES6 import syntax used in the rest of the od_deaths
// project.
const Plotly = require('plotly.js/lib/core');

// Load in the trace types you need.
Plotly.register([require('plotly.js/lib/bar')]);

// Export the custom build
module.exports = Plotly;
