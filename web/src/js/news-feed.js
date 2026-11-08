/* News Feed module for Showcase Platform.
   Fetches curated news from Radarito (/news) and renders responsive cards.
   Vanilla JS, zero dependencies, ASCII-clean.
   Caps display at max 3 cards to avoid page saturation:
   - Dashboard (index): exactly 3 cards — 1 from each sector (SMD_INSPECTION, THT_SOLDERING, AI_SOFTWARE).
   - Industrial spoke: max 3 most recent cards from SMD + THT.
   - Software spoke: max 3 most recent cards from AI_SOFTWARE.
*/

(function () {
  "use strict";

  var FEED_CONTAINER_ID = "news-feed";
  var CONTENT_CONTAINER_ID = "news-feed-content";

  var CATEGORY_LABELS = {
    es: {
      SMD_INSPECTION: "Inspección 3D & Rayos X",
      THT_SOLDERING: "Soldadura SMT/THT",
      AI_SOFTWARE: "Software & AI",
      all: "Todas las noticias",
      loading: "Cargando noticias curadas...",
      empty: "No hay noticias disponibles en esta categoría.",
      read_more: "Ver más",
      feed_title: "Radar Tecnológico & Noticias Curadas"
    },
    en: {
      SMD_INSPECTION: "3D Inspection & X-Ray",
      THT_SOLDERING: "SMT/THT Soldering",
      AI_SOFTWARE: "Software & AI",
      all: "All News",
      loading: "Loading curated news...",
      empty: "No news items available in this category.",
      read_more: "Read more",
      feed_title: "Technology Radar & Curated News"
    }
  };

  function getLang() {
    if (window.portfolioI18n && window.portfolioI18n.getLanguage) {
      return window.portfolioI18n.getLanguage();
    }
    return document.documentElement.lang === "en" ? "en" : "es";
  }

  function getLabels() {
    return CATEGORY_LABELS[getLang()] || CATEGORY_LABELS.es;
  }

  function formatDate(isoStr) {
    if (!isoStr) return "";
    try {
      var d = new Date(isoStr);
      return d.toLocaleDateString(getLang() === "en" ? "en-US" : "es-ES", {
        year: "numeric",
        month: "short",
        day: "numeric"
      });
    } catch (e) {
      return isoStr.slice(0, 10);
    }
  }

  function renderCard(item, labels) {
    var categoryLabel = labels[item.category] || item.category;
    var tagsHtml = "";
    if (Array.isArray(item.tags)) {
      tagsHtml = item.tags
        .slice(0, 3)
        .map(function (t) {
          return '<span class="news-tag">#' + escapeHtml(t) + "</span>";
        })
        .join(" ");
    }

    return (
      '<article class="news-card">' +
      '  <div class="news-card-header">' +
      '    <span class="news-card-badge">' + escapeHtml(categoryLabel) + "</span>" +
      '    <span class="news-card-date">' + escapeHtml(formatDate(item.published_at)) + "</span>" +
      "  </div>" +
      '  <h4 class="news-card-title">' + escapeHtml(item.title) + "</h4>" +
      '  <p class="news-card-summary">' + escapeHtml(item.summary) + "</p>" +
      '  <div class="news-card-tags">' + tagsHtml + "</div>" +
      "</article>"
    );
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function sortByDateDesc(items) {
    return (items || []).slice().sort(function (a, b) {
      var tA = a.published_at ? new Date(a.published_at).getTime() : 0;
      var tB = b.published_at ? new Date(b.published_at).getTime() : 0;
      return tB - tA;
    });
  }

  function renderGrid(containerEl, items, labels) {
    if (!items || !items.length) {
      containerEl.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
      return;
    }
    var html = '<div class="news-grid">';
    for (var i = 0; i < items.length; i++) {
      html += renderCard(items[i], labels);
    }
    html += "</div>";
    containerEl.innerHTML = html;
  }

  function initFeed() {
    var feedBox = document.getElementById(FEED_CONTAINER_ID);
    if (!feedBox) return;

    var labels = getLabels();
    var pageContext = feedBox.getAttribute("data-page-context") || "index";

    var content = document.getElementById(CONTENT_CONTAINER_ID);
    if (!content) return;

    // Clean up any old dynamic tabs if present to avoid DOM pollution
    var existingTabs = document.getElementById("news-tabs-bar");
    if (existingTabs) {
      existingTabs.remove();
    }

    content.innerHTML = '<p class="news-loading">' + escapeHtml(labels.loading) + "</p>";

    if (pageContext === "industrial-smt") {
      // In Industrial Spoke: Load SMD_INSPECTION & THT_SOLDERING, sort by date, show max 3
      Promise.all([
        fetch("/news/?category=SMD_INSPECTION").then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=THT_SOLDERING").then(function (r) { return r.json(); }).catch(function () { return []; })
      ]).then(function (results) {
        var combined = (results[0] || []).concat(results[1] || []);
        var sorted = sortByDateDesc(combined);
        renderGrid(content, sorted.slice(0, 3), labels);
      }).catch(function () {
        content.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
      });
    } else if (pageContext === "software-engineering") {
      // In Software Spoke: Load AI_SOFTWARE, sort by date, show max 3
      fetch("/news/?category=AI_SOFTWARE")
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (items) {
          var sorted = sortByDateDesc(items || []);
          renderGrid(content, sorted.slice(0, 3), labels);
        })
        .catch(function () {
          content.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
        });
    } else {
      // Dashboard (index): exactly 3 cards — 1 from each sector (SMD, THT, AI)
      Promise.all([
        fetch("/news/?category=SMD_INSPECTION").then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=THT_SOLDERING").then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=AI_SOFTWARE").then(function (r) { return r.json(); }).catch(function () { return []; })
      ]).then(function (results) {
        var smdSorted = sortByDateDesc(results[0] || []);
        var thtSorted = sortByDateDesc(results[1] || []);
        var aiSorted = sortByDateDesc(results[2] || []);

        var dashboardItems = [];
        if (smdSorted.length > 0) dashboardItems.push(smdSorted[0]);
        if (thtSorted.length > 0) dashboardItems.push(thtSorted[0]);
        if (aiSorted.length > 0) dashboardItems.push(aiSorted[0]);

        renderGrid(content, dashboardItems, labels);
      }).catch(function () {
        content.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
      });
    }
  }

  // Listen for language changes via portfolioI18n
  document.addEventListener("click", function (e) {
    if (e.target.closest(".lang-btn")) {
      setTimeout(initFeed, 50);
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFeed);
  } else {
    initFeed();
  }

  window.portfolioNews = {
    init: initFeed,
    refresh: initFeed
  };
})();
