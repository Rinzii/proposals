"use strict";
const redirectScript = document.currentScript;
const destination = new URL(redirectScript.dataset.destination, window.location.href);
destination.search = window.location.search;
destination.hash = window.location.hash;
window.location.replace(destination.href);
