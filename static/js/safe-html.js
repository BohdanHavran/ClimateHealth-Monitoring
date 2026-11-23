(function (root) {
  "use strict";
  function escapeHtml(value) {
    const entities = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
    return String(value ?? "").replace(/[&<>"']/g, (character) => entities[character]);
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { escapeHtml };
  } else {
    root.escapeHtml = escapeHtml;
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
