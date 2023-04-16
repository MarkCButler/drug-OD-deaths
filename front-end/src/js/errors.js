/**
 * @fileoverview Custom error handling for the app.
 */

/**
 * Custom error thrown after an HTTP request returns a status that is not in the
 * range 200-299.
 *
 * Example usage:
 *
 * HTTPError(`status code ${response.status}`)
 *
 * where response is a Response object returned by the fetch API.
 */
export class HTTPError extends Error {
  constructor(message) {
    super(message);
    this.name = 'HTTPError';
  }
}


/**
 * Replace the inner HTML of a DOM element with a styled error message.
 * @param {Error} error - the error that occurred
 * @param {HTMLElement} element - the DOM element that was being modified when
 *     the error occurred
 * @param {string} name - a string used to identify the DOM element, e.g., the
 *     id attribute of the DOM element.
 */
export function displayAppError(error, element, name) {
  element.style.cssText = '';
  element.className = '';
  element.classList.add('h3');
  element.classList.add('text-warning');

  element.innerHTML =
    `<p>Failed to create or update HTML element: ${name}.</p>` +
    `<p>${error}</p>`;
}
