/* ==========================================================================
   Paradise Hotel Busan & Haeundae Area Guide
   Plain JS: smooth scroll, mobile nav toggle, attractions search,
   back-to-top button.
   ========================================================================== */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    setupMobileNav();
    setupSmoothScroll();
    setupAttractionSearch();
    setupBackToTop();
  });

  /* --------------------------------------------------------------
     Mobile nav toggle
     -------------------------------------------------------------- */
  function setupMobileNav() {
    var toggle = document.querySelector(".menu-toggle");
    var links = document.querySelector(".nav-links");
    if (!toggle || !links) return;

    toggle.addEventListener("click", function () {
      var isOpen = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    // Close mobile nav when a link is tapped
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* --------------------------------------------------------------
     Smooth scroll for in-page anchor links
     (CSS already provides smooth scrolling, but this also handles
     focus management for accessibility.)
     -------------------------------------------------------------- */
  function setupSmoothScroll() {
    var anchors = document.querySelectorAll('a[href^="#"]');
    anchors.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var href = a.getAttribute("href");
        if (!href || href === "#") return;
        var target = document.querySelector(href);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        // Move focus for screen readers
        target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
      });
    });
  }

  /* --------------------------------------------------------------
     Attractions search / filter
     Matches against card text + data-tags attribute.
     -------------------------------------------------------------- */
  function setupAttractionSearch() {
    var input = document.getElementById("attractionSearch");
    var grid = document.getElementById("attractionGrid");
    var noResults = document.getElementById("noResults");
    if (!input || !grid) return;

    var cards = Array.prototype.slice.call(
      grid.querySelectorAll(".attraction")
    );

    input.addEventListener("input", function () {
      var query = input.value.trim().toLowerCase();
      var matchCount = 0;

      cards.forEach(function (card) {
        var text = card.textContent.toLowerCase();
        var tags = (card.getAttribute("data-tags") || "").toLowerCase();
        var match = !query || text.indexOf(query) !== -1 || tags.indexOf(query) !== -1;
        card.style.display = match ? "" : "none";
        if (match) matchCount++;
      });

      if (noResults) {
        noResults.hidden = matchCount !== 0;
      }
    });
  }

  /* --------------------------------------------------------------
     Back-to-top button
     -------------------------------------------------------------- */
  function setupBackToTop() {
    var btn = document.getElementById("backToTop");
    if (!btn) return;

    var THRESHOLD = 400;

    function update() {
      if (window.scrollY > THRESHOLD) {
        btn.hidden = false;
      } else {
        btn.hidden = true;
      }
    }

    window.addEventListener("scroll", update, { passive: true });
    update();

    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
