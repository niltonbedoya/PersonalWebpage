/* News Feed module for Showcase Platform.
   Fetches curated news from Radarito (/news) and renders responsive cards.
   Vanilla JS, zero dependencies, ASCII-clean. */

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

  function loadCategoryNews(category, containerEl, labels) {
    containerEl.innerHTML = '<p class="news-loading">' + escapeHtml(labels.loading) + "</p>";

    fetch("/news/?category=" + encodeURIComponent(category))
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (items) {
        if (!items || !items.length) {
          containerEl.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
          return;
        }
        var gridHtml = '<div class="news-grid">';
        for (var i = 0; i < items.length; i++) {
          gridHtml += renderCard(items[i], labels);
        }
        gridHtml += "</div>";
        containerEl.innerHTML = gridHtml;
      })
      .catch(function (err) {
        containerEl.innerHTML =
          '<p class="news-empty" style="color:var(--muted);">' +
          escapeHtml(labels.empty) +
          "</p>";
      });
  }

  function initFeed() {
    var feedBox = document.getElementById(FEED_CONTAINER_ID);
    if (!feedBox) return;

    var labels = getLabels();
    var pageContext = feedBox.getAttribute("data-page-context") || "index";

    // Set heading if provided
    var heading = feedBox.querySelector("h3");
    if (heading && !heading.hasAttribute("data-custom-title")) {
      heading.textContent = labels.feed_title;
    }

    var content = document.getElementById(CONTENT_CONTAINER_ID);
    if (!content) return;

    if (pageContext === "industrial-smt") {
      // In Industrial Spoke: Load SMD_INSPECTION & THT_SOLDERING
      content.innerHTML = '<p class="news-loading">' + escapeHtml(labels.loading) + "</p>";
      Promise.all([
        fetch("/news/?category=SMD_INSPECTION").then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=THT_SOLDERING").then(function (r) { return r.json(); }).catch(function () { return []; })
      ]).then(function (results) {
        var combined = (results[0] || []).concat(results[1] || []);
        if (!combined.length) {
          content.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
          return;
        }
        var html = '<div class="news-grid">';
        for (var i = 0; i < combined.length; i++) {
          html += renderCard(combined[i], labels);
        }
        html += "</div>";
        content.innerHTML = html;
      });
    } else if (pageContext === "software-engineering") {
      // In Software Spoke: Load AI_SOFTWARE
      loadCategoryNews("AI_SOFTWARE", content, labels);
    } else {
      // Hub Index: Render category tabs and load default
      var currentCat = "SMD_INSPECTION";
      var tabsContainer = document.getElementById("news-tabs-bar");
      if (!tabsContainer) {
        tabsContainer = document.createElement("div");
        tabsContainer.id = "news-tabs-bar";
        tabsContainer.className = "news-tabs";
        feedBox.insertBefore(tabsContainer, content);
      }

      function updateTabs() {
        tabsContainer.innerHTML =
          '<button type="button" class="news-tab-btn ' + (currentCat === "SMD_INSPECTION" ? "active" : "") + '" data-cat="SMD_INSPECTION">' +
          escapeHtml(labels.SMD_INSPECTION) +
          "</button>" +
          '<button type="button" class="news-tab-btn ' + (currentCat === "THT_SOLDERING" ? "active" : "") + '" data-cat="THT_SOLDERING">' +
          escapeHtml(labels.THT_SOLDERING) +
          "</button>" +
          '<button type="button" class="news-tab-btn ' + (currentCat === "AI_SOFTWARE" ? "active" : "") + '" data-cat="AI_SOFTWARE">' +
          escapeHtml(labels.AI_SOFTWARE) +
          "</button>";

        var btns = tabsContainer.querySelectorAll(".news-tab-btn");
        btns.forEach(function (b) {
          b.addEventListener("click", function () {
            currentCat = b.getAttribute("data-cat");
            updateTabs();
            loadCategoryNews(currentCat, content, labels);
          });
        });
      }

      updateTabs();
      loadCategoryNews(currentCat, content, labels);
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
