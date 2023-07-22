/**
 * After importing the components of fontawesome needed by the app, add SVG
 * icons to the DOM.
 * @module app-fontawesome
 */

// The fontawesome docs show how to import only the SVG icons that are needed:
//
// https://fontawesome.com/docs/web/dig-deeper/svg-core

import {library, dom} from '@fortawesome/fontawesome-svg-core';
import {
  faChartLine, faDatabase, faFileLines, faList, faMap
} from '@fortawesome/free-solid-svg-icons';

library.add(faChartLine, faDatabase, faFileLines, faList, faMap);

dom.watch();
