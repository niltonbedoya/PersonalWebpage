# data/ — Corpus técnico sanitizado y datasets de prueba

Esperado por la spec (`docs/prompt_maestro_de_inicio.md` §6.1). Se llena en la
fase F5 (RAG): corpus sanitizado para indexado en SQLite-vec más datasets para
las baterías de grounding del Auditor y de resiliencia de Centinela.

Reglas: sin PII, sin credenciales, sin marcas reales, sin APIs vivas (v1).
