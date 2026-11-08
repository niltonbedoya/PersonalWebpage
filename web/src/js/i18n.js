/* Portfolio i18n Dictionary and Language Switcher (ES / EN)
   Zero-dependency, vanilla JS, persistent via localStorage.
   ASCII-clean with unicode escapes for maximum cross-platform safety. */

(function () {
  "use strict";

  var DICTIONARY = {
    es: {
      // Global Navigation & Identity
      "brand.subtitle.hub": "Dashboard",
      "brand.subtitle.smt": "Electr\u00f3nica \u2014 SMT/THT",
      "brand.subtitle.soft": "Desarrollo de Software (AI)",
      "nav.hub": "Dashboard",
      "nav.smt": "Electr\u00f3nica \u2014 SMT/THT",
      "nav.soft": "Desarrollo de Software (AI)",
      "nav.rag": "Asistente RAG",
      "btn.rag": "Consultar al Asistente RAG",
      "btn.back_hub": "&larr; Volver al Dashboard",
      "footer.back_hub": "Volver al Dashboard",
      "footer.contact_cv": "Contacto profesional &amp; CV v&iacute;a Asistente RAG",
      "footer.view_smt": "Ver Electr\u00f3nica \u2014 SMT/THT",
      "footer.view_soft": "Ver Desarrollo de Software (AI)",
      "footer.context_feed_smt": "Feed contextual: noticias SMT/THT",
      "footer.context_feed_soft": "Feed contextual: noticias AI/Software",

      // Hub Page
      "hub.title": "Dashboard \u2014 Nilton Bedoya",
      "hub.hero.pill": "Living Technical Portfolio &bull; Hybrid Architecture",
      "hub.hero.title": "Dashboard &mdash; <span class=\"hero-highlight\">Nilton Bedoya</span>",
      "hub.hero.desc": "Portfolio t\u00e9cnico h\u00edbrido en vivo de doble especializaci\u00f3n: <strong>Ingenier\u00eda SMT/THT</strong> (Inspecci\u00f3n \u00d3ptica 3D, Rayos X, Soldadura, Handling) y <strong>Arquitectura de Software Industrial &amp; Soluciones AI</strong> con inferencia de costo cero.",
      "hub.badge.left.title": "Nilton Bedoya",
      "hub.badge.left.sub": "Electr\u00f3nica SMT/THT",
      "hub.badge.right.title": "AI Development",
      "hub.badge.right.sub": "Frameworks - Skills - MCPs",
      "hub.card.smt.tag": "Hardware &amp; Precisi\u00f3n",
      "hub.card.smt.title": "Electr\u00f3nica \u2014 SMT/THT",
      "hub.card.smt.desc": "Maquinaria de inspecci\u00f3n \u00f3ptica 3D, rayos X en l\u00ednea (AXI), sistemas t\u00e9rmicos, soldadura selectiva/ola, handling y metalurgia aplicada a l\u00edneas de alta exigencia SMT/THT.",
      "hub.card.smt.btn": "Ver Electr\u00f3nica SMT/THT &rarr;",
      "hub.card.soft.tag": "Ciberinteligencia &amp; AI",
      "hub.card.soft.title": "Desarrollo de Software (AI)",
      "hub.card.soft.desc": "5 casos de estudio de software y AI, arquitecturas limpias, pipelines multiagente en FastAPI, demostraciones controladas y feeds de inteligencia tecnol\u00f3gica.",
      "hub.card.soft.btn": "Ver Software &amp; AI &rarr;",
      "hub.metrics.title": "M\u00e9tricas del Sistema",
      "hub.metric.runtime.tag": "Multiagent Runtime",
      "hub.metric.runtime.title": "M\u00e9tricas de Ingenier\u00eda",
      "hub.metric.runtime.desc": "Plataforma multiagente con enrutamiento LLM de costo cero (Groq, Google AI Studio, Cloudflare, OpenRouter).",
      "hub.metric.guard.tag": "Per\u00edmetro &lt; 150 ms",
      "hub.metric.guard.title": "Guardrail &amp; Seguridad",
      "hub.metric.guard.desc": "Intercepci\u00f3n perimetral &lt;150 ms contra jailbreak, inyecciones y off-topic.",
      "hub.metric.rag.tag": "Score &ge; 0.85",
      "hub.metric.rag.title": "RAG con Grounding",
      "hub.metric.rag.desc": "Motor RAG sobre corpus local SQLite-vec con score de fundamentaci\u00f3n &ge; 0.85.",
      "hub.news.title": "Noticias SMT/THT",
      "hub.news.loading": "Cargando noticias...",
      "hub.footer.feeds": "Feeds contextuales: SMT/THT &middot; AI/Software",

      // SMT / Electronics Page
      "smt.title": "Electr\u00f3nica \u2014 SMT/THT \u2014 Nilton Bedoya",
      "smt.hero.pill": "Cleanroom Engineering &bull; High Reliability",
      "smt.hero.title": "Electr\u00f3nica &mdash; <span class=\"hero-highlight\">SMT/THT</span>",
      "smt.hero.desc": "Maquinaria de inspecci\u00f3n \u00f3ptica 3D, rayos X en l\u00ednea, ensayos destructivos y no destructivos de adherencia (Bond Testing), sistemas t\u00e9rmicos, soldadura, handling y metalurgia para manufactura electr\u00f3nica de alta fiabilidad.",
      "smt.hero.scope": "<em>L\u00edmite de alcance: exclusi\u00f3n estricta de maquinaria Pick &amp; Place.</em>",
      "smt.badge.cleanroom.main": "Sala Limpia Alta Pureza &bull; Gowning",
      "smt.badge.cleanroom.sub": "Protocolos ISO &bull; ESD Safe",
      "smt.sec.inspection": "Sistemas de Inspecci\u00f3n y Ensayo de Fiabilidad",
      "smt.badge.parmi.main": "PARMI 3D SPI",
      "smt.badge.parmi.sub": "Programaci\u00f3n Gerber &bull; Automoci\u00f3n",
      "smt.tag.parmi": "3D SPI &middot; AOI &middot; PSI",
      "smt.card.parmi.desc1": "3D SPI &mdash; inspecci\u00f3n volum\u00e9trica de pasta y programaci\u00f3n Gerber",
      "smt.card.parmi.desc2": "3D AOI &mdash; inspecci\u00f3n de componentes y calidad de soldadura",
      "smt.card.parmi.desc3": "3D PSI &mdash; inspecci\u00f3n de conformal coating y espesores",
      "smt.tag.opt2d": "\u00d3ptica 2D",
      "smt.card.marantz.desc": "Inspecci\u00f3n \u00f3ptica 2D pre-reflow y post-reflow de componentes SMD y THT en l\u00edneas de alta cadencia.",
      "smt.tag.soldtht": "Soldadura THT",
      "smt.card.versaeye.desc": "Inspecci\u00f3n \u00f3ptica especializada de uniones de soldadura selectiva y wave soldering con control angular.",
      "smt.badge.matrix.main": "Matrix AXI",
      "smt.badge.matrix.sub": "Inspecci\u00f3n en L\u00ednea &bull; Sala Limpia",
      "smt.tag.xray": "Rayos X AXI",
      "smt.card.matrix.desc": "Inspecci\u00f3n por Rayos X en l\u00ednea (AXI) para soldaduras ocultas (BGA, QFN, c\u00e1lculo automatizado de voiding).",
      "smt.badge.nordson.main": "Nordson BT",
      "smt.badge.nordson.sub": "Stellar 4000 &bull; Bond Tester",
      "smt.tag.nordson": "Wire Pull &middot; Ball Shear",
      "smt.card.nordson.desc": "Ensayos destructivos y no destructivos de adherencia mec\u00e1nica (Wire Pull, Ball Shear, Cold Bump Pull) para validaci\u00f3n de fiabilidad de interconexiones.",
      "smt.tag.mpm": "Screen Printing",
      "smt.card.mpm.desc": "Impresoras de pasta de alta precisi\u00f3n (AccuFlex, Momentum), alineaci\u00f3n por visi\u00f3n y control reol\u00f3gico continuo.",
      "smt.sec.thermal": "Sistemas T\u00e9rmicos y Soldadura",
      "smt.badge.ersa.main": "Ersa Reflow",
      "smt.badge.ersa.sub": "Convecci\u00f3n N2 &bull; Planta SMT",
      "smt.tag.ersa": "Selectiva &middot; Refusi\u00f3n",
      "smt.card.ersa.desc": "Soldadura selectiva (mini-wave / multi-dip), soldadura por ola (Wave Soldering) y hornos de refusi\u00f3n por convecci\u00f3n forzada con control de nitr\u00f3geno.",
      "smt.tag.wave": "Wave Soldering",
      "smt.card.electrovert.desc": "Soldadura por ola (serie Vectra) con doble tobera de alta turbulencia y hornos de refusi\u00f3n industrial de alto throughput.",
      "smt.sec.metallurgy": "Metalurgia y Materiales",
      "smt.tag.paste": "Pasta de Soldar",
      "smt.card.paste.title": "Pasta de soldar",
      "smt.card.paste.desc": "Comportamiento reol\u00f3gico, fluxes no-clean y solubles en agua, granulometr\u00eda Tipo 3, 4 y 5 seg\u00fan apertura de stencil.",
      "smt.tag.alloys": "Aleaciones RoHS",
      "smt.card.alloys.title": "Aleaciones",
      "smt.card.alloys.desc": "SAC305, SN100C y formulaciones cl\u00e1sicas SnPb. Gesti\u00f3n de dross (escoria) y mantenimiento de atm\u00f3sfera inerte N2 (&lt;50 ppm O2).",
      "smt.tag.profile": "Perfilado T\u00e9rmico",
      "smt.card.profile.title": "Perfilado t\u00e9rmico",
      "smt.card.profile.desc": "Hornos de refusi\u00f3n: perfiles Ramp-to-Soak vs Ramp-to-Spike, c\u00e1lculo de Time Above Liquidus (TAL) y tasas de enfriamiento controlado.",
      "smt.sec.handling": "Handling, Automatizaci\u00f3n y Diagn\u00f3stico Hardware",
      "smt.tag.smema": "SMEMA &middot; Line Automation",
      "smt.card.transport.title": "Sistemas de Transporte y Control",
      "smt.card.transport.desc": "Cargadores, descargadores, buffers FIFO/LIFO, cintas transportadoras sincronizadas, diagn\u00f3stico y programaci\u00f3n de PLCs industriales para operaci\u00f3n 24/7 sin paradas.",
      "smt.badge.diag.main": "Hardware &bull; Calibraci\u00f3n",
      "smt.badge.diag.sub": "Nordson BT &bull; Electr\u00f3nica &amp; Celdas de Carga",
      "smt.tag.diag": "Diagn\u00f3stico Electromec\u00e1nico",
      "smt.card.diag.title": "Mantenimiento y Calibraci\u00f3n de Precisi\u00f3n",
      "smt.card.diag.desc": "Intervenci\u00f3n directa a nivel de placa electr\u00f3nica, fuentes de alimentaci\u00f3n, buses de control y calibraci\u00f3n de celda de carga en equipos Nordson BT.",
      "smt.sec.fairs": "Presencia y Ecosistema Industrial",
      "smt.badge.setelec.main": "SETELEC Showcase",
      "smt.badge.setelec.sub": "Alianzas Tecnol\u00f3gicas &bull; Ferias SMT",
      "smt.tag.fairs": "Ferias Internacionales",
      "smt.card.setelec.title": "Networking &bull; Distribuidores y Fabricantes",
      "smt.card.setelec.desc": "Colaboraci\u00f3n continua con integradores de maquinaria y especialistas de primer nivel del sector electr\u00f3nico europeo.",
      "smt.badge.inventec.main": "Inventec Chemistry",
      "smt.badge.inventec.sub": "Materiales de Soldadura &bull; Fluxes",
      "smt.tag.chem": "Qu\u00edmica de Soldadura",
      "smt.card.inventec.title": "Materiales Avanzados &bull; Soldadura y Limpieza",
      "smt.card.inventec.desc": "Gesti\u00f3n y selecci\u00f3n t\u00e9cnica de qu\u00edmicos, pastas de soldar no-clean y soluciones de limpieza electr\u00f3nica de alta fiabilidad.",
      "smt.alert.scope": "<strong>L\u00edmite de Alcance:</strong> Exclusi\u00f3n expl\u00edcita de m\u00e1quinas de inserci\u00f3n Pick &amp; Place. El perfil cubre inspecci\u00f3n, procesos t\u00e9rmicos, metalurgia y automatizaci\u00f3n.",

      // Software Page & Applications
      "soft.title": "Desarrollo de Software (AI) \u2014 Nilton Bedoya",
      "soft.hero.pill": "Cyber-Intelligence &bull; Zero-Cost LLM Routing",
      "soft.hero.title": "Desarrollo de Software &mdash; <span class=\"hero-highlight\">(AI)</span>",
      "soft.hero.desc": "Casos de estudio de software industrial, sistemas multiagente desacoplados, arquitecturas limpias y demostraciones controladas con inferencia de costo cero.",
      "soft.hero.scope": "<em>v1 sin APIs vivas expuestas. Demostraciones pregrabadas y sanitizadas bajo dise\u00f1o defensivo.</em>",
      "soft.sec.cases": "Casos de Estudio",
      "soft.badge.tickets.main": "Field Service SaaS",
      "soft.badge.tickets.sub": "M\u00e9tricas de Despacho &bull; SLAs",
      "soft.case.tickets.title": "Sistema de Tickets de Servicio",
      "soft.case.tickets.desc": "Ticketing t\u00e9cnico, seguimiento de incidencias, trazabilidad y SLAs sobre datos 100% sint\u00e9ticos (Base AB anonimizada). Enrutamiento autom\u00e1tico y clasificaci\u00f3n por severidad.",
      "soft.case.erp.title": "ERP Comercial &amp; Financiero",
      "soft.case.erp.desc": "Facturaci\u00f3n electr\u00f3nica, l\u00edneas de cr\u00e9dito, cuentas por cobrar/pagar, control de inventario y gesti\u00f3n de ventas corporativas con entidades ficticias (Base Kronenblumen).",
      "soft.case.logistics.title": "Control Log\u00edstico &amp; Packing List",
      "soft.case.logistics.desc": "Conteo y trazabilidad automatizada de ruedas, asignaci\u00f3n de contenedores y generaci\u00f3n de Packing List de exportaci\u00f3n internacional (PDF/Excel) \u2014 caso Corea.",
      "soft.case.translation.title": "Traducci\u00f3n &amp; Transcripci\u00f3n Simult\u00e1nea",
      "soft.case.translation.desc": "Pipeline de procesamiento en tiempo real de baja latencia para eventos t\u00e9cnicos. Demostraci\u00f3n en video con audio pregrabado sincronizado y m\u00e9tricas de latencia.",
      "soft.badge.cardio.main": "CardioNutri IoT",
      "soft.badge.cardio.sub": "Telemetr\u00eda Cl\u00ednica &bull; React Native",
      "soft.case.health.title": "Plataforma IoT de Salud",
      "soft.case.health.desc": "Ingesta de m\u00e9tricas wearables (ritmo card\u00edaco, SPO2, hidrataci\u00f3n), OCR de informes m\u00e9dicos con modelos locales y visi\u00f3n computacional para an\u00e1lisis nutricional.",
      "soft.case.btn": "Ver caso de estudio &rarr;",
      "soft.alert.v1": "<strong>v1 sin APIs vivas expuestas:</strong> los case studies est\u00e1n sanitizados por dise\u00f1o para eliminar costes y prevenir riesgos de fuga de credenciales o PII."
    },

    en: {
      // Global Navigation & Identity
      "brand.subtitle.hub": "Dashboard",
      "brand.subtitle.smt": "Electronics \u2014 SMT/THT",
      "brand.subtitle.soft": "Software Development (AI)",
      "nav.hub": "Dashboard",
      "nav.smt": "Electronics \u2014 SMT/THT",
      "nav.soft": "Software Development (AI)",
      "nav.rag": "RAG Assistant",
      "btn.rag": "Query RAG Assistant",
      "btn.back_hub": "&larr; Back to Dashboard",
      "footer.back_hub": "Back to Dashboard",
      "footer.contact_cv": "Professional contact &amp; CV via RAG Assistant",
      "footer.view_smt": "View Electronics \u2014 SMT/THT",
      "footer.view_soft": "View Software Development (AI)",
      "footer.context_feed_smt": "Contextual feed: SMT/THT news",
      "footer.context_feed_soft": "Contextual feed: AI/Software news",

      // Hub Page
      "hub.title": "Dashboard \u2014 Nilton Bedoya",
      "hub.hero.pill": "Living Technical Portfolio &bull; Hybrid Architecture",
      "hub.hero.title": "Dashboard &mdash; <span class=\"hero-highlight\">Nilton Bedoya</span>",
      "hub.hero.desc": "Living hybrid technical portfolio with dual specialization: <strong>SMT/THT Engineering</strong> (3D Optical Inspection, X-Ray, Soldering, Handling) and <strong>Industrial Software Architecture &amp; AI Solutions</strong> with zero-cost inference.",
      "hub.badge.left.title": "Nilton Bedoya",
      "hub.badge.left.sub": "Electronics SMT/THT",
      "hub.badge.right.title": "AI Development",
      "hub.badge.right.sub": "Frameworks - Skills - MCPs",
      "hub.card.smt.tag": "Hardware &amp; Precision",
      "hub.card.smt.title": "Electronics \u2014 SMT/THT",
      "hub.card.smt.desc": "3D optical inspection machinery, inline X-ray (AXI), thermal systems, selective/wave soldering, handling, and metallurgy applied to high-demand SMT/THT lines.",
      "hub.card.smt.btn": "View Electronics SMT/THT &rarr;",
      "hub.card.soft.tag": "Cyber-Intelligence &amp; AI",
      "hub.card.soft.title": "Software Development (AI)",
      "hub.card.soft.desc": "5 software and AI case studies, clean architectures, FastAPI multi-agent pipelines, controlled demonstrations, and technology intelligence feeds.",
      "hub.card.soft.btn": "View Software &amp; AI &rarr;",
      "hub.metrics.title": "System Metrics",
      "hub.metric.runtime.tag": "Multiagent Runtime",
      "hub.metric.runtime.title": "Engineering Metrics",
      "hub.metric.runtime.desc": "Multi-agent platform with zero-cost LLM routing (Groq, Google AI Studio, Cloudflare, OpenRouter).",
      "hub.metric.guard.tag": "&lt; 150 ms Perimeter",
      "hub.metric.guard.title": "Guardrail &amp; Security",
      "hub.metric.guard.desc": "Perimeter interception &lt;150 ms against jailbreaks, prompt injections, and off-topic queries.",
      "hub.metric.rag.tag": "Score &ge; 0.85",
      "hub.metric.rag.title": "RAG with Grounding",
      "hub.metric.rag.desc": "RAG engine over local SQLite-vec corpus with grounding score &ge; 0.85.",
      "hub.news.title": "SMT/THT Industry News",
      "hub.news.loading": "Loading news...",
      "hub.footer.feeds": "Contextual feeds: SMT/THT &middot; AI/Software",

      // SMT / Electronics Page
      "smt.title": "Electronics \u2014 SMT/THT \u2014 Nilton Bedoya",
      "smt.hero.pill": "Cleanroom Engineering &bull; High Reliability",
      "smt.hero.title": "Electronics &mdash; <span class=\"hero-highlight\">SMT/THT</span>",
      "smt.hero.desc": "3D optical inspection machinery, inline X-ray, destructive and non-destructive adhesion testing (Bond Testing), thermal systems, soldering, handling, and metallurgy for high-reliability electronics manufacturing.",
      "smt.hero.scope": "<em>Scope boundary: strict exclusion of Pick &amp; Place insertion equipment.</em>",
      "smt.badge.cleanroom.main": "High Purity Cleanroom &bull; Gowning",
      "smt.badge.cleanroom.sub": "ISO Protocols &bull; ESD Safe",
      "smt.sec.inspection": "Inspection Systems &amp; Reliability Testing",
      "smt.badge.parmi.main": "PARMI 3D SPI",
      "smt.badge.parmi.sub": "Gerber Programming &bull; Automotive",
      "smt.tag.parmi": "3D SPI &middot; AOI &middot; PSI",
      "smt.card.parmi.desc1": "3D SPI &mdash; volumetric solder paste inspection and Gerber programming",
      "smt.card.parmi.desc2": "3D AOI &mdash; component inspection and solder joint quality",
      "smt.card.parmi.desc3": "3D PSI &mdash; conformal coating and thickness inspection",
      "smt.tag.opt2d": "2D Optics",
      "smt.card.marantz.desc": "2D optical inspection pre-reflow and post-reflow for SMD and THT components on high-throughput lines.",
      "smt.tag.soldtht": "THT Soldering",
      "smt.card.versaeye.desc": "Specialized optical inspection of selective soldering and wave soldering joints with angular control.",
      "smt.badge.matrix.main": "Matrix AXI",
      "smt.badge.matrix.sub": "Inline Inspection &bull; Cleanroom",
      "smt.tag.xray": "AXI X-Ray",
      "smt.card.matrix.desc": "Inline X-ray inspection (AXI) for hidden solder joints (BGA, QFN, automated voiding calculation).",
      "smt.badge.nordson.main": "Nordson BT",
      "smt.badge.nordson.sub": "Stellar 4000 &bull; Bond Tester",
      "smt.tag.nordson": "Wire Pull &middot; Ball Shear",
      "smt.card.nordson.desc": "Destructive and non-destructive mechanical adhesion testing (Wire Pull, Ball Shear, Cold Bump Pull) for interconnection reliability validation.",
      "smt.tag.mpm": "Screen Printing",
      "smt.card.mpm.desc": "High-precision stencil printers (AccuFlex, Momentum), vision alignment, and continuous rheology control.",
      "smt.sec.thermal": "Thermal Systems &amp; Soldering",
      "smt.badge.ersa.main": "Ersa Reflow",
      "smt.badge.ersa.sub": "N2 Convection &bull; SMT Plant",
      "smt.tag.ersa": "Selective &middot; Reflow",
      "smt.card.ersa.desc": "Selective soldering (mini-wave / multi-dip), wave soldering, and forced convection reflow ovens with nitrogen atmosphere control.",
      "smt.tag.wave": "Wave Soldering",
      "smt.card.electrovert.desc": "Wave soldering (Vectra series) with dual high-turbulence nozzles and high-throughput industrial reflow ovens.",
      "smt.sec.metallurgy": "Metallurgy &amp; Materials",
      "smt.tag.paste": "Solder Paste",
      "smt.card.paste.title": "Solder Paste",
      "smt.card.paste.desc": "Rheological behavior, no-clean and water-soluble fluxes, Type 3, 4, and 5 powder sizes based on stencil apertures.",
      "smt.tag.alloys": "RoHS Alloys",
      "smt.card.alloys.title": "Alloys",
      "smt.card.alloys.desc": "SAC305, SN100C, and classic SnPb formulations. Dross management and inert N2 atmosphere maintenance (&lt;50 ppm O2).",
      "smt.tag.profile": "Thermal Profiling",
      "smt.card.profile.title": "Thermal Profiling",
      "smt.card.profile.desc": "Reflow ovens: Ramp-to-Soak vs Ramp-to-Spike profiles, Time Above Liquidus (TAL) calculation, and controlled cooling rates.",
      "smt.sec.handling": "Handling, Automation &amp; Hardware Diagnostics",
      "smt.tag.smema": "SMEMA &middot; Line Automation",
      "smt.card.transport.title": "Transport &amp; Conveyor Systems",
      "smt.card.transport.desc": "Loaders, unloaders, FIFO/LIFO buffers, synchronized conveyors, diagnosis and programming of industrial PLCs for 24/7 non-stop operation.",
      "smt.badge.diag.main": "Hardware &bull; Calibration",
      "smt.badge.diag.sub": "Nordson BT &bull; Electronics &amp; Load Cells",
      "smt.tag.diag": "Electromechanical Diagnostics",
      "smt.card.diag.title": "Precision Calibration and Maintenance",
      "smt.card.diag.desc": "Direct intervention at electronic PCB level, power supplies, control buses, and load cell calibration on Nordson BT equipment.",
      "smt.sec.fairs": "Industry Presence &amp; Ecosystem",
      "smt.badge.setelec.main": "SETELEC Showcase",
      "smt.badge.setelec.sub": "Technology Alliances &bull; SMT Expos",
      "smt.tag.fairs": "International Expos",
      "smt.card.setelec.title": "Networking &bull; Distributors &amp; Manufacturers",
      "smt.card.setelec.desc": "Ongoing collaboration with machinery integrators and premier specialists in the European electronics industry.",
      "smt.badge.inventec.main": "Inventec Chemistry",
      "smt.badge.inventec.sub": "Soldering Materials &bull; Fluxes",
      "smt.tag.chem": "Soldering Chemistry",
      "smt.card.inventec.title": "Advanced Materials &bull; Soldering &amp; Cleaning",
      "smt.card.inventec.desc": "Technical management and selection of chemicals, no-clean solder pastes, and high-reliability electronic cleaning solutions.",
      "smt.alert.scope": "<strong>Scope Boundary:</strong> Strict exclusion of Pick &amp; Place insertion machines. Expertise focuses on inspection, thermal processes, metallurgy, and automation.",

      // Software Page & Applications
      "soft.title": "Software Development (AI) \u2014 Nilton Bedoya",
      "soft.hero.pill": "Cyber-Intelligence &bull; Zero-Cost LLM Routing",
      "soft.hero.title": "Software Development &mdash; <span class=\"hero-highlight\">(AI)</span>",
      "soft.hero.desc": "Industrial software case studies, decoupled multi-agent systems, clean architectures, and controlled demonstrations with zero-cost inference.",
      "soft.hero.scope": "<em>v1 without exposed live APIs. Pre-recorded and sanitized demonstrations under defensive design.</em>",
      "soft.sec.cases": "Case Studies",
      "soft.badge.tickets.main": "Field Service SaaS",
      "soft.badge.tickets.sub": "Dispatch Metrics &bull; SLAs",
      "soft.case.tickets.title": "Field Service Ticketing Platform",
      "soft.case.tickets.desc": "Technical ticketing, incident tracking, auditability, and SLAs on 100% synthetic data (anonymized Base AB). Automated routing and severity classification.",
      "soft.case.erp.title": "Commercial &amp; Financial ERP System",
      "soft.case.erp.desc": "Electronic billing, credit lines, accounts receivable/payable, inventory control, and enterprise sales management with fictitious entities (Base Kronenblumen).",
      "soft.case.logistics.title": "Logistics Control &amp; Export Packing List",
      "soft.case.logistics.desc": "Automated wheel counting and traceability, container allocation, and international export Packing List generation (PDF/Excel) \u2014 Korea case study.",
      "soft.case.translation.title": "Simultaneous Translation &amp; Transcription Engine",
      "soft.case.translation.desc": "Low-latency real-time processing pipeline for technical conferences. Video demonstration with synchronized pre-recorded audio and latency metrics.",
      "soft.badge.cardio.main": "CardioNutri IoT",
      "soft.badge.cardio.sub": "Clinical Telemetry &bull; React Native",
      "soft.case.health.title": "Biometric Health &amp; Clinical IoT Platform",
      "soft.case.health.desc": "Wearable biometric ingestion (heart rate, SpO2, hydration), medical report OCR with local models, and computer vision for dietary analysis.",
      "soft.case.btn": "View case study &rarr;",
      "soft.alert.v1": "<strong>v1 without exposed live APIs:</strong> case studies are sanitized by design to eliminate recurring costs and avoid credential or PII leakage risks."
    }
  };

  var STORAGE_KEY = "portfolio_lang";

  function detectBrowserLang() {
    try {
      var nav = window.navigator;
      var raw = "";
      if (nav.languages && nav.languages.length > 0) {
        raw = nav.languages[0];
      } else if (nav.language) {
        raw = nav.language;
      } else if (nav.userLanguage) {
        raw = nav.userLanguage;
      }
      if (raw && typeof raw === "string") {
        var clean = raw.toLowerCase().trim();
        if (clean.indexOf("es") === 0) {
          return "es";
        }
      }
    } catch (e) {
      /* ignore navigator access error */
    }
    return "en";
  }

  function getSavedLang() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved && (saved === "es" || saved === "en")) {
        return saved;
      }
    } catch (e) {
      /* ignore storage unavailable */
    }
    return detectBrowserLang();
  }

  function setLanguage(lang) {
    if (lang !== "es" && lang !== "en") {
      lang = "es";
    }

    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* ignore storage unavailable */
    }

    document.documentElement.lang = lang;

    // Update active class on toggle buttons
    var buttons = document.querySelectorAll(".lang-btn");
    buttons.forEach(function (btn) {
      if (btn.getAttribute("data-lang") === lang) {
        btn.classList.add("active");
        btn.setAttribute("aria-pressed", "true");
      } else {
        btn.classList.remove("active");
        btn.setAttribute("aria-pressed", "false");
      }
    });

    // Translate all [data-i18n] nodes
    var transNodes = document.querySelectorAll("[data-i18n]");
    var dict = DICTIONARY[lang] || DICTIONARY.es;

    transNodes.forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (!key || dict[key] === undefined) return;
      var text = dict[key];
      if (el.getAttribute("data-i18n-html") === "true" || /<[a-z][\s\S]*>/i.test(text) || /&[a-z#0-9]+;/i.test(text)) {
        el.innerHTML = text;
      } else {
        el.textContent = text;
      }
    });

    // Translate page title if key provided
    var titleKey = document.body ? document.body.getAttribute("data-i18n-title") : null;
    if (titleKey && dict[titleKey]) {
      document.title = dict[titleKey];
    }
  }

  function initI18n() {
    var currentLang = getSavedLang();

    // Attach click handlers to language switch buttons
    document.addEventListener("click", function (e) {
      var btn = e.target.closest(".lang-btn");
      if (!btn) return;
      var targetLang = btn.getAttribute("data-lang");
      if (targetLang && (targetLang === "es" || targetLang === "en")) {
        setLanguage(targetLang);
      }
    });

    setLanguage(currentLang);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initI18n);
  } else {
    initI18n();
  }

  window.portfolioI18n = {
    setLanguage: setLanguage,
    getLanguage: getSavedLang,
    detectLanguage: detectBrowserLang,
    dictionary: DICTIONARY
  };
})();
