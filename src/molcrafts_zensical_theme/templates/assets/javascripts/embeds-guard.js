/**
 * Docs embed error boundary.
 *
 * Must be loaded as `type="module"` AFTER the MolPlot/MolVis loader module so
 * top-level `await import(...)` finishes first. A classic script runs at the
 * first `await` (CE not defined yet), stamps a banner, then the chart mounts
 * underneath -- a false "bundle failed to load" overlay on a working plot.
 *
 * Still waits on `customElements.whenDefined` + timeout: instant navigation
 * and a slow CDN fallback can otherwise race. A late definition clears any
 * banner we stamped too early.
 */
(function () {
  var CHECKED = "data-molcrafts-embed-error";
  var WAIT_MS = 8000;
  var waiting = {};

  function customElementDefined(tag) {
    return typeof customElements !== "undefined" && !!customElements.get(tag);
  }

  function scriptSrcs(pattern) {
    var out = [];
    var scripts = document.scripts;
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].src;
      if (src && pattern.test(src)) out.push(src);
    }
    return out;
  }

  function clearStale(tag) {
    var nodes = document.getElementsByTagName(tag);
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var boxes = el.querySelectorAll("[data-molcrafts-embed-error-msg]");
      if (!boxes.length && !el.hasAttribute(CHECKED)) continue;
      for (var j = 0; j < boxes.length; j++) boxes[j].remove();
      el.removeAttribute(CHECKED);
      if (el.getAttribute("data-state") === "error") {
        el.removeAttribute("data-state");
      }
    }
  }

  function markUnupgraded(tag, message) {
    var nodes = document.getElementsByTagName(tag);
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.hasAttribute(CHECKED)) continue;
      el.setAttribute(CHECKED, "");
      el.setAttribute("data-state", "error");
      if (el.querySelector("[data-molcrafts-embed-error-msg]")) continue;
      var box = document.createElement("div");
      box.setAttribute("data-molcrafts-embed-error-msg", "");
      box.setAttribute("role", "alert");
      box.className = "molcrafts-embed-error";
      box.textContent = message;
      el.appendChild(box);
    }
    return nodes.length;
  }

  function reportMolplot() {
    var count = document.getElementsByTagName("molplot-chart").length;
    if (!count || customElementDefined("molplot-chart")) return;
    var srcs = scriptSrcs(/molplot/i);
    var hint =
      srcs.length === 0
        ? "Set extra.molcrafts.enable_molplot = true so the theme loads assets/molplot/elements.js (then the npm CDN)."
        : "Scripts that look like MolPlot: " + srcs.join(", ");
    console.error(
      "[molcrafts] found " +
        count +
        " <molplot-chart> element(s) but customElements.get('molplot-chart') is undefined. " +
        hint,
    );
    markUnupgraded(
      "molplot-chart",
      "molplot-chart: custom element is not defined -- the MolPlot bundle failed to load.",
    );
  }

  function reportMolvis() {
    var count = document.getElementsByTagName("molvis-viewer").length;
    if (!count || customElementDefined("molvis-viewer")) return;
    var srcs = scriptSrcs(/molvis/i);
    var hint =
      srcs.length === 0
        ? "No script whose src mentions molvis is on this page."
        : "Scripts that look like MolVis: " + srcs.join(", ");
    console.error(
      "[molcrafts] found " +
        count +
        " <molvis-viewer> element(s) but customElements.get('molvis-viewer') is undefined. " +
        hint,
    );
    markUnupgraded(
      "molvis-viewer",
      "molvis-viewer: custom element is not defined -- the MolVis bundle failed to load.",
    );
  }

  function waitThen(tag, fail) {
    if (customElementDefined(tag)) {
      waiting[tag] = false;
      clearStale(tag);
      return;
    }
    if (!document.getElementsByTagName(tag).length) return;
    if (waiting[tag]) return;
    waiting[tag] = true;

    var settled = false;
    function ok() {
      if (settled) return;
      settled = true;
      waiting[tag] = false;
      clearStale(tag);
    }
    function giveUp() {
      if (settled) return;
      if (customElementDefined(tag)) {
        ok();
        return;
      }
      settled = true;
      waiting[tag] = false;
      fail();
    }

    if (typeof customElements !== "undefined" && customElements.whenDefined) {
      customElements.whenDefined(tag).then(ok);
    }
    setTimeout(giveUp, WAIT_MS);
  }

  function check() {
    waitThen("molplot-chart", reportMolplot);
    waitThen("molvis-viewer", reportMolvis);
  }

  check();
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(check);
  }
})();
