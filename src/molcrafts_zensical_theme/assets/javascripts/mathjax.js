/* MathJax bootstrap for Zensical + pymdownx.arithmatex (generic=true).
 *
 * Load this BEFORE the MathJax library itself, e.g. in zensical.toml:
 *
 *   extra_javascript = [
 *     "assets/javascripts/mathjax.js",  # or the theme copy via path below
 *     "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
 *   ]
 *
 * The theme also injects the same config + document$ re-typeset from main.html
 * so consuming sites only need the MathJax CDN entry. This file remains useful
 * when a site overrides main.html or loads MathJax without the theme hooks.
 */
window.MathJax = {
  tex: {
    // arithmatex (generic=true) already rewrites $…$ / $$…$$ to these forms.
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    // Only process spans that arithmatex emitted; skip the rest of the page.
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

function molcraftsTypesetMath() {
  if (!window.MathJax || typeof window.MathJax.typesetPromise !== "function") {
    return;
  }
  try {
    if (window.MathJax.startup?.output?.clearCache) {
      window.MathJax.startup.output.clearCache();
    }
    if (typeof window.MathJax.typesetClear === "function") {
      window.MathJax.typesetClear();
    }
    if (typeof window.MathJax.texReset === "function") {
      window.MathJax.texReset();
    }
    window.MathJax.typesetPromise();
  } catch (_) {
    // MathJax may not be fully started yet; the next document$ tick retries.
  }
}

// Material/Zensical instant navigation replaces .md-content without a full
// reload. Re-typeset after every document$ emission so formulas appear on the
// first visit, not only after a hard refresh.
if (typeof document$ !== "undefined" && document$.subscribe) {
  document$.subscribe(molcraftsTypesetMath);
} else if (typeof document !== "undefined") {
  // Fallback when document$ is not yet available (script order / non-instant).
  document.addEventListener("DOMContentLoaded", molcraftsTypesetMath);
}
