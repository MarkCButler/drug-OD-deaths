/**
 * @fileoverview Export convenience functions that wrap interactions with the
 * fetch API.
 */

import {HTTPError} from './errors';


/**
 * Return a promise representing JSON fetched from a back-end URL.
 * @param {string} url
 * @param {string} paramString
 * @returns {Promise} Promise that resolves to JSON fetched from the back-end
 */
export function fetchJson(url, paramString) {
  return fetchData(url, paramString, 'json');
}


/**
 * Return a promise representing text fetched from a back-end URL.
 * @param {string} url
 * @param {string} paramString
 * @returns {Promise} Promise that resolves to text fetched from the back-end
 */
export function fetchText(url, paramString) {
  return fetchData(url, paramString, 'text');
}


async function fetchData(url, paramString, type) {
  type = type.toLowerCase();
  const response = await fetch(url + '?' + paramString);
  if (response.ok) {
    const extractData = {
      json: () => response.json(),
      text: () => response.text()
    };
    return extractData[type]();
  } else {
    throw new HTTPError(`status code ${response.status}`);
  }
}
