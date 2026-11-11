r"""TDD: Corpus sanitization battery as a build gate (F5/T5, S3/S7/S8).

Scans every *.md file under data/ recursively and asserts:
- No email addresses (regex [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}).
- No credential assignments: password/token/secret/api_key/apikey/sk- followed
  by = or : or space with an actual value. Policy statements mentioning these
  words (e.g. "no credenciales ni claves de API") are OK because no value
  follows them.
- No phone numbers ([0-9]{3}[-.\s][0-9]{3}[-.\s][0-9]{4}).
- Real brands outside the spec-approved list (Parmi, Marantz, Ersa, Matrix,
  MPM, Electrovert, ITW EAE are OK) are flagged FOR REVIEW as a WARNING only
  — they do not fail the build, per the task ("warn, not fail").
- Every file has a title line: first non-empty line starts with "# ".

Hard gates (emails, phones, credentials, title) fail the build. Brand findings
are collected and reported so reviewers can triage, but the clean T3 corpus
passes the build gate.

All offline/deterministic, no network. A hard-gate violation is a test failure
(build gate), so the corpus must be clean before it reaches the SQLite-vec
index.
"""

import re
from pathlib import Path

import pytest

# Root-relative path to the corpus, resolved from this file so it never depends
# on the current working directory (S7: paths based on __file__, absolute).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS_DIR = REPO_ROOT / "data"

# --- Spec-approved real brands (section 2.3 + F5 T5 task description) ---------

APPROVED_BRANDS = {
    "Parmi",
    "Marantz",
    "Ersa",
    "Matrix",
    "MPM",
    "Electrovert",
    "ITW EAE",
}

# Collected brand candidates across all files (warn-only report).
BRAND_CANDIDATES = {}


def _md_files():
    """All *.md files under data/, recursively, sorted for determinism."""
    return sorted(CORPUS_DIR.rglob("*.md"))


# --- Helpers ------------------------------------------------------------------

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"[0-9]{3}[-.\s][0-9]{3}[-.\s][0-9]{4}")

# Credential key followed by = / : / space and then a real value (non-whitespace
# token). This lets policy statements ("no credenciales ni claves de API")
# pass while flagging actual leaked values (e.g. "password = hunter2").
CREDENTIAL_RE = re.compile(
    r"(password|token|secret|api_key|apikey|sk-)\s*[:= ]\s*\S+",
    re.IGNORECASE,
)

# Common Spanish section-header / technical words that are capitalized in
# markdown titles but are NOT brands. Excluded so the brand detector surfaces
# genuine brand-like tokens rather than every title-cased Spanish word.
_COMMON_WORDS = {
    # Spanish articles/pronouns/conjunctions often title-cased in headers
    "El", "La", "Los", "Las", "Un", "Una", "Y", "O", "Pero", "Sin", "Con",
    "Por", "Para", "Sobre", "Entre", "Desde", "Hasta", "Durante", "Contra",
    # Spanish nouns/adjectives common in section headers
    "Caso", "Estudio", "Alcance", "Documento", "Contenido", "Funcion",
    "Metodo", "Aplicacion", "Parametros", "Limitaciones", "Este", "Esta",
    "Estos", "Estas", "Solo", "Solo", "Ningun", "Ninguna", "Todo", "Toda",
    "Todos", "Todas", "Otro", "Otra", "Otros", "Otras", "Mismo", "Misma",
    "Mismos", "Mismas", "Tal", "Cual", "Cuales", "Donde", "Como", "Cuando",
    "Que", "Quien", "Quienes", "Cuyo", "Cuya", "Cuyos", "Cuyas",
    # Common technical/domain terms that are capitalized but not brands
    "Pick", "Place", "Pick", "Place", "Smt", "Tht", "Bga", "Qfn", "Qfp",
    "Spi", "Aoi", "Pci", "Pcb", "Plc", "Hmi", "Oem", "Erp", "Crm", "Api",
    "Iot", "Ui", "Ux", "Csv", "Pdf", "Sql", "Sla", "Oee", "DpmO", "FpY",
    "Mtbf", "Mttr", "Tal", "Led", "Leds", "Dross", "Flux", "Fluxes",
    "Ipc", "Ethernet", "Rayos", "Rayos X", "Rayosx", "AxI", "Axi", "Xrf",
    "Xray", "MpM", "Mpm",
    # Section header verbs
    "Descripcion", "Descripcion", "Solucion", "Modulos", "Modulo", "Flujo",
    "Gestion", "Emision", "Reportes", "Stack", "Lenguaje", "Base", "Capa",
    "Datos", "Todos", "Metricas", "Numero", "Tiempo", "Tasa", "Porcentaje",
    "Volumen", "Saldo", "Rotacion", "Precision", "Disponibilidad", "Notas",
    "Definicion", "Trazabilidad", "Analisis", "Validacion", "Documentacion",
    "Seguridad", "Mantenimiento", "Control", "Calidad", "Proceso", "Procesos",
    "Sistema", "Sistemas", "Equipo", "Equipos", "Planta", "Linea", "Lineas",
    "Estacion", "Estaciones", "Producto", "Productos", "Componente",
    "Componentes", "Maquina", "Maquinas", "Equipo", "Equipos", "Herramienta",
    "Herramientas", "Material", "Materiales", "Aleacion", "Aleaciones",
    "Pasta", "Pastas", "Flux", "Fundente", "Fundentes", "Temperatura",
    "Temperaturas", "Termico", "Termicos", "Perfil", "Perfiles", "Refusion",
    "Reflujo", "Ola", "Olas", "Soldadura", "Humectacion", "Humedad",
    "Calidad", "Defecto", "Defectos", "Puente", "Puentes", "Vaciado", "Vaciados",
    "Bola", "Bolas", "Terminal", "Terminales", "Pad", "Pads", "Pastilla",
    "Pastillas", "Placa", "Placas", "Placa", "Placas", "Sensor", "Sensores",
    "Alarma", "Alarmas", "Senal", "Senales", "Interface", "Interfaces",
    "Programacion", "Diagnostico", "Alarma", "Emergencia", "Emergencias",
    "Presencia", "Posicion", "Posiciones", "Velocidad", "Altura", "Ancho",
    "Espesor", "Cobertura", "Uniformidad", "Adherencia", "Contaminacion",
    "Burbujas", "Grietas", "Residuos", "Residuo", "Reciclaje", "Refino",
    "Atmosfera", "Inerte", "Nitrogeno", "Oxido", "Oxidos", "Oxigeno", "Aire",
    "Humo", "Vapores", "Extraccion", "Ventilacion", "Filtro", "Filtros",
    "Barrera", "Barreras", "Proteccion", "Equipamiento", "Guantes", "Ojos",
    "Piel", "Residuo", "Residuos", "Normativa", "Normativas", "Ambiental",
    "Industrial", "Automotriz", "Entorno", "Entornos", "Calidad", "Trazabilidad",
    "Trazas", "Acciones", "Correctivas", "Tendencia", "Analisis", "Tendencias",
    "Validacion", "Cambio", "Cambios", "Base", "Linea", "Base", "Producto",
    "Productos", "Operador", "Operadores", "Fecha", "Fechas", "Contexto",
    "Registro", "Registros", "Fuente", "Frecuencia", "Objetivo", "Objetivos",
    "Indicador", "Indicadores", "Metrica", "Metricas", "Medicion", "Mediciones",
    "Desviacion", "Desviaciones", "Gradual", "Graduales", "Cumplimiento",
    "Incidencia", "Incidencias", "Tecnico", "Tecnicos", "Usuario", "Usuarios",
    "Cliente", "Clientes", "Proveedor", "Proveedores", "Ticket", "Tickets",
    "Estado", "Estados", "Intervencion", "Intervenciones", "Comentario",
    "Comentarios", "Historial", "Prioridad", "Prioridades", "Categoria",
    "Categorias", "Tablero", "Tableros", "Filtro", "Filtros", "Rango",
    "Rangos", "Motor", "Motores", "Calculo", "Umbral", "Umbrales", "Configurado",
    "Configurados", "Reporte", "Reportes", "Desempeno", "Carga", "Cargas",
    "Trabajo", "Semana", "Semanas", "Volumen", "Volumenes", "Promedio",
    "Promedios", "Promedio", "Discrepancia", "Discrepancias", "Conciliacion",
    "Fisica", "Fisicas", "Inventario", "Inventarios", "Ubicacion", "Ubicaciones",
    "Movimiento", "Movimientos", "Stock", "Ocupacion", "Contenedor",
    "Contenedores", "Envio", "Envios", "Packing", "List", "Listas", "Destino",
    "Destinos", "Referencia", "Referencias", "Cantidad", "Cantidades", "Peso",
    "Pesos", "Volumen", "Volumenes", "Etiqueta", "Etiquetas", "Identificacion",
    "Reserva", "Reservas", "Disponibilidad", "Disponibles", "Salida", "Salidas",
    "Entrada", "Entradas", "Recepcion", "Almacenamiento", "Secuenciacion",
    "Orden", "Ordenes", "Liberacion", "Liberaciones", "Parada", "Paradas",
    "Cadena", "Cadenas", "Correa", "Cordas", "Rodillo", "Rodillos", "Vacuo",
    "Vacuno", "Paleta", "Paletas", "Estante", "Estantes", "Ranura", "Ranuras",
    "Vertical", "Vertical", "Horizontal", "Horizontal", "Entrada", "Entradas",
    "Salida", "Salidas", "Controlado", "Controlados", "Lento", "Lenta",
    "Absorbe", "Absorben", "Variaciones", "Tiempos", "Ciclo", "Ciclos",
    "Inspeccion", "Inspecciones", "Estacion", "Estaciones", "Resto", "Restante",
    "Logico", "Logicos", "Programable", "Programables", "Controlador",
    "Controladores", "Comunicacion", "Serie", "Bus", "Campo", "Entradas",
    "Salidas", "Registros", "Temporizadores", "Alarma", "Alarmas", "Historial",
    "Sensores", "Presencia", "Fin", "Carrera", "Fotoelectricos", "Fotoelectrico",
    "Actuadores", "Motores", "Electrovalvulas", "Cilindros", "Neumaticos",
    "Neumatico", "Interbloqueos", "Seguridad", "Mensajes", "Mensaje",
    "Emergencia", "Emergencias", "Pila", "Pilas", "Software", "Panel", "Paneles",
    "Operador", "Operadores", "Equipos", "Diagnostico", "Diagnosticos", "Portatiles",
    "Portatil", "Campo", "Lectura", "Lecturas", "Errores", "Error", "Sincroniza",
    "Sincronizan", "Coordinacion", "Coordinan", "Terminado", "Terminada", "Lista",
    "Listo", "Listos", "Listas", "Central", "Centrales", "Coordina", "Coordina",
    "Flujo", "Flujos", "Registra", "Registran", "Eventos", "Evento", "Produccion",
    "Eficiencia", "Global", "Globales", "Equipo", "Equipos", "Ingestion",
    "Ingestiones", "Recepcion", "Recepciones", "Metrica", "Metricas", "Serie",
    "Series", "Tiempo", "Tiempos", "Emparejamiento", "Sesion", "Sesiones",
    "Consolidacion", "Perfil", "Perfiles", "Unificado", "Unificada", "Unificados",
    "Unificadas", "Extraccion", "Extracciones", "Texto", "Textos", "Informes",
    "Informe", "Medico", "Medicos", "Centro", "Centros", "Salud", "Saluds",
    "Diagnostico", "Diagnosticos", "Resultados", "Resultado", "Analisis",
    "Analisis", "Analisis", "Platos", "Plato", "Porciones", "Porcion",
    "Nutricional", "Nutricionales", "Calorias", "Caloria", "Proteinas",
    "Proteina", "Grasas", "Grasa", "Carbohidratos", "Carbohidrato", "Aproximado",
    "Aproximada", "Panel", "Paneles", "Tendencias", "Tendencia", "Resumen",
    "Resumenes", "Registro", "Registros", "Comidas", "Comida", "Analizadas",
    "Analizada", "Ilustrativo", "Ilustrativa", "Ilustrativos", "Ilustrativas",
    "Consejo", "Consejos", "Medico", "Medicos", "Profesional", "Profesionales",
    "Pipeline", "Pipelines", "Traduccion", "Traducciones", "Transcripcion",
    "Transcripciones", "Simultanea", "Simultaneas", "Eventos", "Evento",
    "Tecnicos", "Tecnico", "Demostracion", "Demostraciones", "Controlada",
    "Controladas", "Controlado", "Controlados", "Pregrabado", "Pregrabados",
    "Pregrabada", "Pregrabadas", "Baja", "Bajas", "Latencia", "Latencias",
    "Sincronizacion", "Sincronizaciones", "Audio", "Audios", "Texto", "Textos",
    "Idioma", "Idiomas", "Objetivo", "Objetivos", "Terminologia", "Terminologias",
    "Tecnica", "Tecnicas", "Posible", "Posibles", "Modulo", "Modulos",
    "Sincronizacion", "Sincronizacion", "Timeline", "Timelines", "Momento",
    "Momentos", "Adecuado", "Adecuada", "Adecuados", "Adecuadas", "Reproductor",
    "Reproductores", "Visualizacion", "Visualizaciones", "Subtitulos", "Subtitulo",
    "Metricas", "Metrica", "Latencia", "Latencias", "Segmento", "Segmentos",
    "Extremo", "Extremos", "Extremo", "Extremos", "Extremo", "Extremos",
    "Modo", "Modos", "Demostracion", "Demostraciones", "Controlada", "Controladas",
    "Reproduccion", "Reproducciones", "Texto", "Textos", "Pregenerado",
    "Pregenerados", "Pregenerada", "Pregeneradas", "Funcionamiento", "Funcionamientos",
    "Dependencia", "Dependencias", "Servicios", "Servicio", "Vivo", "Vivos",
    "Vivos", "Lenguaje", "Lenguajes", "Servicios", "Servicio", "Backend",
    "Backends", "Frontend", "Frontends", "Interfaz", "Interfaces", "Usuario",
    "Usuarios", "Procesamiento", "Procesamientos", "Senales", "Senal", "Senales",
    "Senal", "Gestion", "Gestion", "Tiempo", "Tiempos", "Almacenamiento",
    "Almacenamientos", "Fragmentos", "Fragmento", "Audio", "Audios", "Texto",
    "Textos", "Modo", "Modos", "Demostracion", "Demostraciones", "Contenido",
    "Contenidos", "Charlas", "Charla", "Ponentes", "Ponente", "Ficticios",
    "Ficticia", "Ficticios", "Ficticias", "Anonimizados", "Anonimizada",
    "Anonimizados", "Anonimizadas", "Grabaciones", "Grabacion", "Grabaciones",
    "Grabacion", "Prueba", "Pruebas", "Personal", "Personales", "Informacion",
    "Informacion", "Informacion", "Informacion", "Personal", "Personales",
    "Direcciones", "Direccion", "Direcciones", "Numeros", "Numero", "Telefono",
    "Telefonos", "Credenciales", "Credencial", "Tokens", "Token", "Claves",
    "Clave", "API", "Apis", "Api", "Apis", "Volumen", "Volumenes", "Mensual",
    "Mensuales", "Unidades", "Unidad", "Sinteticas", "Sintetico", "Sinteticos",
    "Sinteticas", "Plazo", "Plazos", "Credito", "Creditos", "Saldo", "Saldos",
    "Cuentas", "Cuenta", "Cobrar", "Pagar", "Pendientes", "Pendiente", "Vencimiento",
    "Vencimientos", "Alertas", "Alerta", "Saldos", "Saldo", "Promedio", "Promedios",
    "Cuentas", "Cuenta", "Cobrar", "Pagar", "Rotacion", "Rotaciones", "Inventario",
    "Inventarios", "Representativo", "Representativa", "Representativos",
    "Representativas", "Tiempo", "Tiempos", "Procesamiento", "Procesamientos",
    "Factura", "Facturas", "Pago", "Pagos", "Aplicacion", "Aplicaciones",
    "Credito", "Creditos", "Creditos", "Credito", "Creditos", "Limite", "Limites",
    "Cliente", "Clientes", "Seguimiento", "Seguimientos", "Saldos", "Saldo",
    "Pendientes", "Pendiente", "Alertas", "Alerta", "Vencimiento", "Vencimientos",
    "Entradas", "Entrada", "Salidas", "Salida", "Stock", "Ajustes", "Ajuste",
    "Transferencias", "Transferencia", "Ubicaciones", "Ubicacion", "Valoracion",
    "Valoraciones", "Inventario", "Inventarios", "Libro", "Libros", "Mayor",
    "Mayores", "Sintetico", "Sintetica", "Sinteticos", "Sinteticas",
    "Estado", "Estados", "Resultados", "Resultado", "Financiera", "Financieras",
    "Financiero", "Financieros", "Balance", "Balances", "Situaciones", "Situacion",
    "Representaciones", "Representacion", "Ilustrativas", "Ilustrativa",
    "Ilustrativos", "Ilustrativo", "Control", "Control", "Acceso", "Accesos",
    "Roles", "Rol", "Registro", "Registros", "Auditoria", "Auditorias",
    "Operaciones", "Operacion", "Criticas", "Critica", "Creacion", "Creaciones",
    "Facturas", "Factura", "Aprobacion", "Aprobaciones", "Creditos", "Credito",
    "Ajustes", "Ajuste", "Inventario", "Inventarios", "Lenguaje", "Lenguajes",
    "Servicios", "Servicio", "Backend", "Backends", "Interfaz", "Interfaz",
    "Usuario", "Usuarios", "Interfaz", "Interfaz", "Usuario", "Usuarios",
    "Base", "Bases", "Datos", "Dato", "Transaccional", "Transaccionales",
    "Reportes", "Reporte", "Capa", "Capas", "Validacion", "Validaciones",
    "Reglas", "Regla", "Negocio", "Negocios", "Creditos", "Credito", "Inventario",
    "Inventarios", "Contabilidad", "Contabilidades",
    # Common English header words
    "The", "This", "That", "Then", "They", "Them", "Their", "There", "These",
    "When", "Where", "While", "Which", "Who", "Whose", "Why", "How", "What",
    "With", "From", "Has", "Had", "His", "Her", "Its", "Our", "Are", "Was",
    "Were", "Been", "Being", "Will", "Would", "Could", "Should", "May", "Might",
    "Must", "Can", "Does", "Did", "Do", "For", "And", "But", "Not", "You",
    "Your", "We", "Us", "It", "Its", "First", "Pass", "Yield", "Time", "Above",
    "Liquidus", "Ramp", "To", "Soak", "Para", "Sn", "Pb", "Ag", "Cu", "Ni",
    "SnPb", "Sac305", "Sn100C", "Type", "Types", "RoHS", "Ipc", "Ipc-A-610",
    "Ipc-A", "Ipc", "Ipc", "Ipc", "Erp", "Erp", "Crm", "Crm",
    # Model names that are approved-technical, not brand leaks (kept here so they
    # are not reported as brand candidates even though not in APPROVED_BRANDS)
    "SAC305", "SN100C", "SnPb", "VERSAEYE", "AccuFlex", "Momentum", "Vectra",
    "AccuFlex", "Momentum", "Vectra",
}

# Two-word phrases that are approved-technical content, not brand leaks.
_COMMON_TWO_WORD = {
    "Pick Place", "Rayos X", "Time Above", "Above Liquidus", "Ramp-to-Soak",
    "Time Above", "Liquidus", "Modelos AccuFlex", "PCI Inspection", "Plataforma IoT",
    "Modulo OCR", "First Pass", "Pass Yield", "Para SAC305", "APIs Viv", "APIs viv",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _find_brand_tokens(text: str):
    """Capitalized brand-like tokens not in the approved list.

    Returns genuine brand-like candidates: capitalized tokens that are not
    common Spanish/header words, not approved brands, and not known technical
    model/alloy names. Multi-word brands (e.g. ITW EAE) are matched across
    words; common two-word technical phrases are excluded.
    """
    candidates = set()
    # Single-token brands: Word, Word-Word, Word123
    for m in re.finditer(r"\b[A-Z][A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b", text):
        word = m.group(0)
        if word in APPROVED_BRANDS:
            continue
        if word in _COMMON_WORDS:
            continue
        if len(word) < 4:
            continue
        candidates.add(word)
    # Two-word capitalized phrases (potential multi-word brands)
    for m in re.finditer(r"\b[A-Z][A-Za-z0-9]+ [A-Z][A-Za-z0-9]+\b", text):
        phrase = m.group(0)
        if phrase in APPROVED_BRANDS:
            continue
        if phrase in _COMMON_TWO_WORD:
            continue
        # Skip if both words are already excluded common words.
        parts = phrase.split(" ")
        if parts[0] in _COMMON_WORDS and parts[1] in _COMMON_WORDS:
            continue
        candidates.add(phrase)
    return candidates


def _has_title_line(text: str) -> bool:
    """First non-empty line starts with "# "."""
    for line in text.splitlines():
        if line.strip():
            return line.lstrip().startswith("# ")
    return False


# --- Tests --------------------------------------------------------------------

# S3 — corpus sanitization build gate (hard failures) --------------------------

@pytest.mark.parametrize("path", _md_files(), ids=lambda p: p.name)
def test_no_email_addresses(path):
    text = _read_text(path)
    matches = EMAIL_RE.findall(text)
    assert not matches, (
        f"EMAIL LEAK in {path.name}: {matches}"
    )


@pytest.mark.parametrize("path", _md_files(), ids=lambda p: p.name)
def test_no_phone_numbers(path):
    text = _read_text(path)
    matches = PHONE_RE.findall(text)
    assert not matches, (
        f"PHONE LEAK in {path.name}: {matches}"
    )


@pytest.mark.parametrize("path", _md_files(), ids=lambda p: p.name)
def test_no_credential_assignments(path):
    text = _read_text(path)
    matches = CREDENTIAL_RE.findall(text)
    assert not matches, (
        f"CREDENTIAL LEAK in {path.name}: {matches}"
    )


# S3 — brand gate: warn-only, collect candidates for review -------------------

@pytest.mark.parametrize("path", _md_files(), ids=lambda p: p.name)
def test_unapproved_real_brands_warn_only(path):
    """Brands are warn-only (flagged for review, do not fail the build).

    Records candidates into BRAND_CANDIDATES for the summary report. Asserts
    the detector does not misclassify an approved brand as unapproved (sanity
    check on the exclusion logic).
    """
    text = _read_text(path)
    flagged = _find_brand_tokens(text)
    BRAND_CANDIDATES[path.name] = sorted(flagged)
    # Sanity: no approved brand should appear in the flagged set.
    assert not (set(flagged) & APPROVED_BRANDS), (
        f"Approved brand wrongly flagged in {path.name}: "
        f"{set(flagged) & APPROVED_BRANDS}"
    )


def test_brand_candidates_report():
    """Summary report of brand candidates flagged for review (warn-only).

    Prints every unapproved brand-like candidate found across the corpus so
    reviewers can triage. Does not fail the build (warn-not-fail).
    """
    total = sum(len(v) for v in BRAND_CANDIDATES.values())
    print("\n--- Brand candidates flagged for review (warn-only) ---")
    if total == 0:
        print("None found.")
    for name in sorted(BRAND_CANDIDATES):
        cands = BRAND_CANDIDATES[name]
        if cands:
            print(f"{name}: {cands}")
    print(f"Total candidates across corpus: {total}")
    print("------------------------------------------------------\n")
    # Warn-only: never fails the build.


# S3 — title line (hard failure) ----------------------------------------------

@pytest.mark.parametrize("path", _md_files(), ids=lambda p: p.name)
def test_every_file_has_title_line(path):
    text = _read_text(path)
    assert _has_title_line(text), (
        f"MISSING TITLE in {path.name}: first non-empty line must start with '# '"
    )


def test_corpus_is_not_empty():
    """The gate must scan at least one file, otherwise it vacuously passes."""
    files = _md_files()
    assert files, f"No *.md files found under {CORPUS_DIR}"


def test_parmi_uses_pci_for_conformal_coating_inspection():
    """PARMI conformal-coating inspection is PCI, never PSI."""
    text = _read_text(CORPUS_DIR / "smt_inspection_parmi.md")
    assert "PSI" not in text
    assert "PCI" in text
    assert "barnizado" in text.lower()
