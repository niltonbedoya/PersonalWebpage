/* News Feed module for Showcase Platform.
   Fetches curated news from Radarito (/news) and renders responsive cards.
   Vanilla JS, zero dependencies, ASCII-clean.
   Bilingual ES/EN, source link included, capped at 3 cards per view:
   - Dashboard (index): 1 PCB manufacturing, 1 Partner equipment, 1 AI general.
   - Industrial spoke: 1 PCB manufacturing, 2 Partner equipment (PARMI, ERSA, NORDSON, MARANTZ).
   - Software spoke: 1 Skills/Frameworks/MCPs, 2 AI Models.
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
      pcb_manufacturing: "Fabricación PCB",
      partner_equipment: "Equipos Partner",
      skills_frameworks_mcps: "Skills & MCPs",
      ai_models: "Modelos AI",
      source_prefix: "Fuente: ",
      loading: "Cargando radar tecnológico...",
      empty: "No hay noticias disponibles en esta categoría.",
      feed_title: "Radar Tecnológico & Noticias Curadas"
    },
    en: {
      SMD_INSPECTION: "3D Inspection & X-Ray",
      THT_SOLDERING: "SMT/THT Soldering",
      AI_SOFTWARE: "Software & AI",
      pcb_manufacturing: "PCB Manufacturing",
      partner_equipment: "Partner Equipment",
      skills_frameworks_mcps: "Skills & MCPs",
      ai_models: "AI Models",
      source_prefix: "Source: ",
      loading: "Loading technology radar...",
      empty: "No news items available in this category.",
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

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function getHostname(urlStr) {
    if (!urlStr) return "";
    try {
      var url = new URL(urlStr);
      return url.hostname.replace(/^www\./, "");
    } catch (e) {
      return "link";
    }
  }

  function renderCard(item, labels) {
    var lang = getLang();
    var title = lang === "en" ? (item.title_en || item.title) : (item.title_es || item.title);
    var summary = lang === "en" ? (item.summary_en || item.summary) : (item.summary_es || item.summary);

    // Pick badge: sub_category label if available, otherwise category label
    var badgeKey = item.sub_category || item.category;
    var badgeLabel = labels[badgeKey] || labels[item.category] || badgeKey;

    var tagsHtml = "";
    if (Array.isArray(item.tags)) {
      tagsHtml = item.tags
        .slice(0, 4)
        .map(function (t) {
          return '<span class="news-tag">#' + escapeHtml(t) + "</span>";
        })
        .join(" ");
    }

    var host = getHostname(item.source_url);
    var sourceText = (labels.source_prefix || "Fuente: ") + escapeHtml(host);

    return (
      '<article class="news-card">' +
      '  <div class="news-card-header">' +
      '    <span class="news-card-badge">' + escapeHtml(badgeLabel) + "</span>" +
      '    <span class="news-card-date">' + escapeHtml(formatDate(item.published_at)) + "</span>" +
      "  </div>" +
      '  <h4 class="news-card-title"><a href="' + escapeHtml(item.source_url) + '" target="_blank" rel="noopener noreferrer" class="news-title-link">' + escapeHtml(title) + "</a></h4>" +
      '  <p class="news-card-summary">' + escapeHtml(summary) + "</p>" +
      '  <div class="news-card-tags">' + tagsHtml + "</div>" +
      '  <div class="news-card-footer">' +
      '    <a href="' + escapeHtml(item.source_url) + '" target="_blank" rel="noopener noreferrer" class="news-source-link">' +
      "      <span>" + sourceText + "</span>" +
      '      <svg class="news-external-icon" viewBox="0 0 16 16" width="12" height="12" fill="currentColor">' +
      '        <path d="M4.5 3a.5.5 0 0 0 0 1h5.793L2.146 12.146a.5.5 0 0 0 .708.708L11 4.707V10.5a.5.5 0 0 0 1 0v-7a.5.5 0 0 0-.5-.5h-7z"/>' +
      "      </svg>" +
      "    </a>" +
      "  </div>" +
      "</article>"
    );
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
    var lang = getLang();
    var pageContext = feedBox.getAttribute("data-page-context") || "index";

    var content = document.getElementById(CONTENT_CONTAINER_ID);
    if (!content) return;

    // Clean up any old dynamic tabs if present
    var existingTabs = document.getElementById("news-tabs-bar");
    if (existingTabs) {
      existingTabs.remove();
    }

    content.innerHTML = '<p class="news-loading">' + escapeHtml(labels.loading) + "</p>";

    if (pageContext === "industrial-smt") {
      // ELECTRONICA SMT — 3 Noticias:
      // a. 1 noticia sobre empresas de fabricación de circuitos impresos/integrados (pcb_manufacturing)
      // b. 2 noticias de empresas con las que trabajo (partner_equipment: PARMI, ERSA, NORDSON, MARANTZ)
      Promise.all([
        fetch("/news/?category=SMD_INSPECTION&lang=" + lang).then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=THT_SOLDERING&lang=" + lang).then(function (r) { return r.json(); }).catch(function () { return []; })
      ]).then(function (results) {
        var allIndustrial = (results[0] || []).concat(results[1] || []);
        var pcbNews = sortByDateDesc(allIndustrial.filter(function (x) { return x.sub_category === "pcb_manufacturing"; }));
        var partnerNews = sortByDateDesc(allIndustrial.filter(function (x) { return x.sub_category === "partner_equipment"; }));

        var selected = [];
        if (pcbNews.length > 0) selected.push(pcbNews[0]);
        if (partnerNews.length > 0) selected.push(partnerNews[0]);
        if (partnerNews.length > 1) selected.push(partnerNews[1]);

        renderGrid(content, selected, labels);
      }).catch(function () {
        content.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
      });
    } else if (pageContext === "software-engineering") {
      // DESARROLLO DE SOFTWARE AI — 3 Noticias:
      // a. 1 noticia sobre skills, frameworks, MCPs (skills_frameworks_mcps)
      // b. 2 noticias sobre modelos y novedades de AI (ai_models)
      fetch("/news/?category=AI_SOFTWARE&lang=" + lang)
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.json();
        })
        .then(function (items) {
          var allSoftware = items || [];
          var skillsNews = sortByDateDesc(allSoftware.filter(function (x) { return x.sub_category === "skills_frameworks_mcps"; }));
          var modelsNews = sortByDateDesc(allSoftware.filter(function (x) { return x.sub_category === "ai_models"; }));

          var selected = [];
          if (skillsNews.length > 0) selected.push(skillsNews[0]);
          if (modelsNews.length > 0) selected.push(modelsNews[0]);
          if (modelsNews.length > 1) selected.push(modelsNews[1]);

          renderGrid(content, selected, labels);
        })
        .catch(function () {
          content.innerHTML = '<p class="news-empty">' + escapeHtml(labels.empty) + "</p>";
        });
    } else {
      // DASHBOARD — 3 Noticias:
      // a. 1 noticia de empresas de fabricación de PCB / EMS (pcb_manufacturing)
      // b. 1 noticia de empresas con las que trabajo (partner_equipment: PARMI, ERSA, NORDSON, MARANTZ)
      // c. 1 noticia de AI en general (skills, frameworks o modelos)
      Promise.all([
        fetch("/news/?category=SMD_INSPECTION&lang=" + lang).then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=THT_SOLDERING&lang=" + lang).then(function (r) { return r.json(); }).catch(function () { return []; }),
        fetch("/news/?category=AI_SOFTWARE&lang=" + lang).then(function (r) { return r.json(); }).catch(function () { return []; })
      ]).then(function (results) {
        var allHardware = (results[0] || []).concat(results[1] || []);
        var allAI = results[2] || [];

        var pcbNews = sortByDateDesc(allHardware.filter(function (x) { return x.sub_category === "pcb_manufacturing"; }));
        var partnerNews = sortByDateDesc(allHardware.filter(function (x) { return x.sub_category === "partner_equipment"; }));
        var aiNews = sortByDateDesc(allAI);

        var selected = [];
        if (pcbNews.length > 0) selected.push(pcbNews[0]);
        if (partnerNews.length > 0) selected.push(partnerNews[0]);
        if (aiNews.length > 0) selected.push(aiNews[0]);

        renderGrid(content, selected, labels);
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
