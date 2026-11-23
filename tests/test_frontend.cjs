"use strict";
const assert = require("node:assert/strict");
const { escapeHtml } = require("../static/js/safe-html.js");
assert.equal(escapeHtml('<img src=x onerror="alert(1)">'), "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;");
assert.equal(escapeHtml("O'Brian & <test>"), "O&#39;Brian &amp; &lt;test&gt;");
assert.equal(escapeHtml(null), "");
assert.equal(escapeHtml(0), "0");
assert.equal(escapeHtml("Київ"), "Київ");
console.log("PASS: 5 HTML-escaping assertions (not browser/E2E coverage)");
