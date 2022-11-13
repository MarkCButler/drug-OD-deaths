'use strict';


export class HTTPError extends Error {
  constructor(message) {
    super(message);
    this.name = 'HTTPError';
  }
}


export function displayAppError(error, divElem, name) {
  divElem.style.cssText = '';
  divElem.className = '';
  divElem.classList.add('h3');
  divElem.classList.add('text-warning');

  divElem.innerHTML = `<p>Failed to fetch or generate ${name}.</p>` +
                      `<p>${error}</p>`;
}
