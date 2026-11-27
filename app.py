import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import io
import urllib.parse
import random
import os
import base64
from contextlib import contextmanager

st.set_page_config(
    page_title="Laboratorio de Teoría de Juegos | DeC - EPN",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- IDENTIDAD VISUAL OFICIAL: https://economia.epn.edu.ec/ (DeC - EPN) ---
# Paleta extraída directamente de theme.9.css de economia.epn.edu.ec y logotipo DeC:
# - Azul Marino Primario (uk-section-primary / uk-button-primary): #18243E -> #190F47
# - Naranja Terracota Secundario (uk-section-secondary / uk-button-secondary): #E96132 -> #F46318
# - Púrpura Institucional de Títulos (uk-h1..h6): #3D1A4A
# - Dorado DeC: #F0B840 | Rojo DeC: #E01818
# - Tipografía oficial del portal: 'Varela Round'
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Varela+Round&family=Inter:wght@400;500;600;700&display=swap');

    /* Fondo principal claro institucional (independiente del modo oscuro del navegador) */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #F7F8FC !important;
        color: #18243E !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    [data-testid="stHeader"] {
        background-color: rgba(247, 248, 252, 0.88) !important;
    }

    /* Tipografía de títulos estilo economia.epn.edu.ec (Varela Round + #3D1A4A / #18243E) */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Varela Round', 'Segoe UI', sans-serif !important;
        color: #18243E !important;
        letter-spacing: -0.01em;
    }
    [data-testid="stMain"] h2, [data-testid="stMain"] h3 {
        color: #3D1A4A !important;
    }
    [data-testid="stMain"] p, [data-testid="stMain"] li, [data-testid="stMain"] label {
        color: #2D3748 !important;
    }

    /* --- BARRA LATERAL AZUL MARINO INSTITUCIONAL (#18243E -> #190F47) --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #18243E 0%, #190F47 100%) !important;
        border-right: 4px solid #E96132 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] a {
        color: #F0B840 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.18) !important;
    }
    /* Tarjetas blancas para escudos y código QR en la barra lateral */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        background-color: #FFFFFF !important;
        padding: 8px !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22) !important;
    }
    /* Caja destacada en barra lateral */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: rgba(233, 97, 50, 0.2) !important;
        border: 1px solid #E96132 !important;
        border-radius: 10px !important;
    }
    /* Inputs dentro de la barra lateral */
    [data-testid="stSidebar"] [data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E96132 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] input {
        color: #18243E !important;
        -webkit-text-fill-color: #18243E !important;
        background-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-baseweb="input"] button svg {
        fill: #18243E !important;
    }
    /* Botones dentro de la barra lateral */
    [data-testid="stSidebar"] button {
        background: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.35) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(45deg, #E96132 40%, #F46318) !important;
        border-color: #E96132 !important;
        color: #FFFFFF !important;
    }

    /* --- BANNER SUPERIOR INSTITUCIONAL (ESTILO HERO economia.epn.edu.ec) --- */
    .dec-hero-banner {
        background: linear-gradient(125deg, #18243E 0%, #190F47 65%, #3D1A4A 100%);
        border-radius: 16px;
        padding: 20px 26px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        box-shadow: 0 14px 34px rgba(24, 36, 62, 0.18);
        border-bottom: 5px solid #E96132;
        position: relative;
        overflow: hidden;
    }
    .dec-hero-badge {
        display: inline-block;
        background: linear-gradient(45deg, #E96132 40%, #F46318);
        color: #FFFFFF !important;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 8px;
    }
    .dec-hero-title {
        font-family: 'Varela Round', 'Segoe UI', sans-serif !important;
        color: #FFFFFF !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 4px 0 !important;
        line-height: 1.2;
    }
    .dec-hero-sub {
        color: rgba(255, 255, 255, 0.86) !important;
        font-size: 0.94rem;
        margin: 0 !important;
    }
    .dec-hero-logo-box {
        background: #FFFFFF;
        padding: 10px 14px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .dec-hero-logo-box img {
        height: 66px;
        width: auto;
        display: block;
    }

    /* --- INDICADOR DE LAS 6 ETAPAS DEL PROTOCOLO --- */
    .dec-stepper {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 18px;
    }
    .dec-step {
        flex: 1 1 130px;
        padding: 8px 10px;
        border-radius: 9px;
        font-size: 0.78rem;
        font-weight: 600;
        text-align: center;
        background: #FFFFFF;
        color: #64748B;
        border: 1px solid #E2E8F0;
    }
    .dec-step.done {
        background: #EEF2FA;
        color: #18243E;
        border-color: #CBD5E1;
    }
    .dec-step.active {
        background: linear-gradient(45deg, #E96132 40%, #F46318);
        color: #FFFFFF !important;
        border-color: #E96132;
        box-shadow: 0 4px 12px rgba(233, 97, 50, 0.32);
    }

    @media (max-width: 640px) {
        .dec-hero-banner {
            padding: 15px 16px;
        }
        .dec-hero-title {
            font-size: 1.32rem;
        }
        .dec-hero-logo-box img {
            height: 48px;
        }
        .dec-step {
            flex: 1 1 45%;
            font-size: 0.72rem;
            padding: 6px 8px;
        }
    }

    /* --- BOTONES DE ACCIÓN (uk-button-secondary #E96132 y uk-button-primary #18243E) --- */
    [data-testid="stMain"] button[kind="primary"],
    [data-testid="stMain"] button[kind="primaryFormSubmit"],
    [data-testid="stMain"] [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(45deg, #E96132 40%, #F46318) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Varela Round', 'Segoe UI', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 6px 18px rgba(233, 97, 50, 0.35) !important;
        transition: all 0.22s ease-in-out !important;
    }
    [data-testid="stMain"] button[kind="primary"] *,
    [data-testid="stMain"] button[kind="primaryFormSubmit"] *,
    [data-testid="stMain"] [data-testid="stFormSubmitButton"] button * {
        color: #FFFFFF !important;
    }
    [data-testid="stMain"] button[kind="primary"]:hover,
    [data-testid="stMain"] button[kind="primaryFormSubmit"]:hover,
    [data-testid="stMain"] [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(45deg, #18243E 40%, #3D1A4A) !important;
        box-shadow: 0 8px 22px rgba(24, 36, 62, 0.38) !important;
        transform: translateY(-1px) !important;
    }

    /* Botones secundarios en el área principal */
    [data-testid="stMain"] button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1.8px solid #18243E !important;
        color: #18243E !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stMain"] button[kind="secondary"] * {
        color: #18243E !important;
    }
    [data-testid="stMain"] button[kind="secondary"]:hover {
        background-color: #18243E !important;
        border-color: #18243E !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMain"] button[kind="secondary"]:hover * {
        color: #FFFFFF !important;
    }

    /* --- TARJETAS Y FORMULARIOS (uk-card-default de economia.epn.edu.ec) --- */
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-top: 4px solid #18243E !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px 0 rgba(24, 36, 62, 0.07) !important;
    }
    [data-testid="stMain"] [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-top: 4px solid #E96132 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px 0 rgba(24, 36, 62, 0.07) !important;
    }

    /* Inputs en el área principal */
    [data-testid="stMain"] [data-baseweb="input"],
    [data-testid="stMain"] [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #CBD5E1 !important;
        color: #18243E !important;
    }
    [data-testid="stMain"] input {
        color: #18243E !important;
        -webkit-text-fill-color: #18243E !important;
    }

    /* Barra de progreso con degradado institucional DeC */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #18243E 0%, #E96132 65%, #F0B840 100%) !important;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Varela Round', 'Segoe UI', sans-serif !important;
        color: #18243E !important;
        font-weight: 600;
        padding: 10px 18px;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(233, 97, 50, 0.1) !important;
        border-bottom: 3px solid #E96132 !important;
        color: #E96132 !important;
    }

    /* Métricas */
    [data-testid="stMetricValue"] {
        font-family: 'Varela Round', 'Segoe UI', sans-serif !important;
        color: #18243E !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #5A6578 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

MAX_RONDAS = 5
DEFAULT_CUPO = 20
DEFAULT_APP_URL = st.secrets.get("APP_URL", "https://juego-keynes-epn.streamlit.app/")

@st.cache_data
def get_logo_b64():
    if os.path.exists("logo_dec.png"):
        with open("logo_dec.png", "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def render_encabezado_institucional(titulo, subtitulo):
    logo_b64 = get_logo_b64()
    logo_html = (
        f'<div class="dec-hero-logo-box"><img src="data:image/png;base64,{logo_b64}" alt="Logo DeC EPN"></div>'
        if logo_b64 else ""
    )
    st.markdown(f"""
    <div class="dec-hero-banner">
        <div>
            <div class="dec-hero-badge">Departamento de Economía Cuantitativa · EPN</div>
            <div class="dec-hero-title">{titulo}</div>
            <p class="dec-hero-sub">{subtitulo}</p>
        </div>
        {logo_html}
    </div>
    """, unsafe_allow_html=True)

def render_stepper(paso_activo):
    pasos = [
        (1, "1º Inscripción"),
        (2, "2º Sala de Espera"),
        (3, "3º Elegir Número"),
        (4, "4º Esperar Jugadas"),
        (5, "5º Resultados"),
        (6, "6º Siguiente Ronda"),
    ]
    items_html = []
    for num, texto in pasos:
        cls = "active" if num == paso_activo else ("done" if num < paso_activo else "")
        items_html.append(f'<div class="dec-step {cls}">{texto}</div>')
    st.markdown(f'<div class="dec-stepper">{"".join(items_html)}</div>', unsafe_allow_html=True)

@st.cache_data
def generar_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        encoded = urllib.parse.quote_plus(url)
        return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded}"

# ==============================================================================
# CONEXIÓN, ESQUEMA Y MÁQUINA DE ESTADOS SINCRONIZADA (6 ETAPAS)
# ==============================================================================
@contextmanager
def get_conn():
    conn = sqlite3.connect("juegos_clase.db", check_same_thread=False, timeout=20)
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS participantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                juego TEXT,
                cedula TEXT,
                estudiante TEXT,
                universidad TEXT,
                UNIQUE(juego, cedula)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS respuestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                juego TEXT,
                ronda INTEGER,
                estudiante TEXT,
                cedula TEXT,
                universidad TEXT,
                decision REAL,
                UNIQUE(juego, ronda, cedula)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listos_ronda (
                juego TEXT,
                ronda INTEGER,
                cedula TEXT,
                PRIMARY KEY (juego, ronda, cedula)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS estado_sesion (
                juego TEXT PRIMARY KEY,
                ronda_activa INTEGER DEFAULT 1,
                estado TEXT DEFAULT 'abierta',
                fase TEXT DEFAULT 'inscripcion',
                cupo_estudiantes INTEGER DEFAULT 20,
                solo_profesor_avanza INTEGER DEFAULT 1
            )
        """)
        # Migraciones seguras si la base de datos proviene de una versión previa
        cols_resp = [c[1] for c in conn.execute("PRAGMA table_info(respuestas)").fetchall()]
        if "cedula" not in cols_resp:
            conn.execute("ALTER TABLE respuestas ADD COLUMN cedula TEXT")
        if "universidad" not in cols_resp:
            conn.execute("ALTER TABLE respuestas ADD COLUMN universidad TEXT")

        cols_est = [c[1] for c in conn.execute("PRAGMA table_info(estado_sesion)").fetchall()]
        if "fase" not in cols_est:
            conn.execute("ALTER TABLE estado_sesion ADD COLUMN fase TEXT DEFAULT 'inscripcion'")
        if "cupo_estudiantes" not in cols_est:
            conn.execute(f"ALTER TABLE estado_sesion ADD COLUMN cupo_estudiantes INTEGER DEFAULT {DEFAULT_CUPO}")
        if "solo_profesor_avanza" not in cols_est:
            conn.execute("ALTER TABLE estado_sesion ADD COLUMN solo_profesor_avanza INTEGER DEFAULT 1")

init_db()

def sincronizar_estado_juego(juego):
    """
    Evalúa y actualiza automáticamente las transiciones del protocolo de 6 etapas:
    - Etapa 1 & 2 ('inscripcion') -> Etapa 3 ('jugando', Ronda 1) al llegar a cupo_estudiantes inscritos.
    - Etapa 3 & 4 ('jugando')     -> Etapa 5 ('resultados') al llegar a cupo_estudiantes jugadas en la ronda.
    - Etapa 5 & 6 ('resultados')  -> Etapa 3 ('jugando', Ronda r+1) cuando el profesor la activa
                                     (o automáticamente si solo_profesor_avanza=0 y todos marcan Listo).
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT ronda_activa, fase, cupo_estudiantes, solo_profesor_avanza FROM estado_sesion WHERE juego = ?",
            (juego,)
        ).fetchone()
        if not row:
            conn.execute(
                """INSERT INTO estado_sesion (juego, ronda_activa, estado, fase, cupo_estudiantes, solo_profesor_avanza)
                   VALUES (?, 1, 'abierta', 'inscripcion', ?, 1)""",
                (juego, DEFAULT_CUPO)
            )
            ronda_activa, fase, cupo, solo_prof = 1, "inscripcion", DEFAULT_CUPO, 1
        else:
            ronda_activa = int(row[0] or 1)
            fase = str(row[1] or "inscripcion")
            cupo = max(1, int(row[2] or DEFAULT_CUPO))
            solo_prof = int(row[3]) if row[3] is not None else 1

        num_inscritos = conn.execute(
            "SELECT COUNT(*) FROM participantes WHERE juego = ?", (juego,)
        ).fetchone()[0]

        # Transición automática Etapa 2 -> Etapa 3: Todos los participantes esperados se inscribieron
        if fase == "inscripcion" and num_inscritos >= cupo:
            fase = "jugando"
            ronda_activa = 1
            conn.execute(
                "UPDATE estado_sesion SET fase = 'jugando', ronda_activa = 1, estado = 'abierta' WHERE juego = ?",
                (juego,)
            )

        num_respuestas = conn.execute(
            "SELECT COUNT(*) FROM respuestas WHERE juego = ? AND ronda = ?",
            (juego, ronda_activa)
        ).fetchone()[0]

        # Transición automática Etapa 4 -> Etapa 5: Todos los participantes jugaron la ronda activa
        if fase == "jugando" and num_respuestas >= cupo:
            fase = "resultados"
            conn.execute(
                "UPDATE estado_sesion SET fase = 'resultados', estado = 'cerrada' WHERE juego = ?",
                (juego,)
            )

        num_listos = conn.execute(
            "SELECT COUNT(*) FROM listos_ronda WHERE juego = ? AND ronda = ?",
            (juego, ronda_activa)
        ).fetchone()[0]

        # Transición opcional Etapa 5 -> Etapa 6 -> Etapa 3 (si el modo automático está habilitado)
        if fase == "resultados" and not solo_prof and num_listos >= cupo:
            if ronda_activa < MAX_RONDAS:
                ronda_activa += 1
                fase = "jugando"
                conn.execute(
                    "UPDATE estado_sesion SET ronda_activa = ?, fase = 'jugando', estado = 'abierta' WHERE juego = ?",
                    (ronda_activa, juego)
                )
                num_respuestas = conn.execute(
                    "SELECT COUNT(*) FROM respuestas WHERE juego = ? AND ronda = ?",
                    (juego, ronda_activa)
                ).fetchone()[0]
                num_listos = 0
            else:
                fase = "finalizado"
                conn.execute(
                    "UPDATE estado_sesion SET fase = 'finalizado', estado = 'cerrada' WHERE juego = ?",
                    (juego,)
                )

    return {
        "ronda_activa": ronda_activa,
        "fase": fase,
        "cupo": cupo,
        "solo_profesor_avanza": bool(solo_prof),
        "num_inscritos": num_inscritos,
        "num_respuestas": num_respuestas,
        "num_listos": num_listos,
    }

def actualizar_sesion(juego, ronda_activa=None, fase=None, cupo=None, solo_profesor_avanza=None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO estado_sesion (juego, ronda_activa, estado, fase, cupo_estudiantes, solo_profesor_avanza)
               VALUES (?, 1, 'abierta', 'inscripcion', ?, 1)
               ON CONFLICT(juego) DO NOTHING""",
            (juego, DEFAULT_CUPO)
        )
        if ronda_activa is not None:
            conn.execute("UPDATE estado_sesion SET ronda_activa = ? WHERE juego = ?", (int(ronda_activa), juego))
        if fase is not None:
            est_txt = "abierta" if fase == "jugando" else "cerrada"
            conn.execute("UPDATE estado_sesion SET fase = ?, estado = ? WHERE juego = ?", (fase, est_txt, juego))
        if cupo is not None:
            conn.execute("UPDATE estado_sesion SET cupo_estudiantes = ? WHERE juego = ?", (max(1, int(cupo)), juego))
        if solo_profesor_avanza is not None:
            conn.execute("UPDATE estado_sesion SET solo_profesor_avanza = ? WHERE juego = ?", (1 if solo_profesor_avanza else 0, juego))

def reiniciar_juego_db(juego, borrar_todo=False, mantener_cupo=DEFAULT_CUPO):
    with get_conn() as conn:
        if borrar_todo:
            conn.execute("DELETE FROM participantes")
            conn.execute("DELETE FROM respuestas")
            conn.execute("DELETE FROM listos_ronda")
            conn.execute("DELETE FROM estado_sesion")
        else:
            conn.execute("DELETE FROM participantes WHERE juego = ?", (juego,))
            conn.execute("DELETE FROM respuestas WHERE juego = ?", (juego,))
            conn.execute("DELETE FROM listos_ronda WHERE juego = ?", (juego,))
        conn.execute(
            """INSERT INTO estado_sesion (juego, ronda_activa, estado, fase, cupo_estudiantes, solo_profesor_avanza)
               VALUES (?, 1, 'abierta', 'inscripcion', ?, 1)
               ON CONFLICT(juego) DO UPDATE SET
                   ronda_activa = 1,
                   estado = 'abierta',
                   fase = 'inscripcion',
                   cupo_estudiantes = excluded.cupo_estudiantes""",
            (juego, max(1, int(mantener_cupo)))
        )

# ==============================================================================
# FRAGMENTOS EN TIEMPO REAL (ACTUALIZACIÓN CADA 2 SEGUNDOS) - ESTUDIANTE
# ==============================================================================
@st.fragment(run_every=2)
def render_sala_espera_inscripcion(juego, estudiante):
    s = sincronizar_estado_juego(juego)
    if s["fase"] != "inscripcion":
        st.rerun()

    inscritos = s["num_inscritos"]
    cupo = s["cupo"]
    faltan = max(0, cupo - inscritos)
    progreso = min(1.0, inscritos / cupo) if cupo > 0 else 0.0

    with st.container(border=True):
        st.markdown(f"### ⏳ Sala de Espera — ¡Bienvenido/a, {estudiante}!")
        st.write(
            "Tu inscripción ha sido registrada con éxito. En cuanto se inscriban todos los participantes "
            "(o el profesor dé inicio a la sesión), se habilitará automáticamente la **Ronda 1** en tu pantalla."
        )
        st.progress(progreso)
        c1, c2, c3 = st.columns(3)
        c1.metric("👥 Estudiantes inscritos", f"{inscritos} / {cupo}")
        c2.metric("⏳ Faltan por inscribirse", faltan)
        c3.metric("📡 Estado", "Esperando inicio")
        st.caption("🟢 Conectado en tiempo real — Esta pantalla se actualiza automáticamente cada 2 segundos.")

@st.fragment(run_every=2)
def render_monitor_fase_durante_seleccion(juego, ronda_esperada):
    """Vigila cambios de fase/ronda cada 2s sin recargar ni interrumpir el formulario numérico del alumno."""
    s = sincronizar_estado_juego(juego)
    if s["fase"] != "jugando" or s["ronda_activa"] != ronda_esperada:
        st.rerun()
    st.caption(
        f"👥 Avance de la clase en Ronda {ronda_esperada}: **{s['num_respuestas']} de {s['cupo']}** jugadas enviadas "
        f"🟢 *(en vivo)*"
    )

@st.fragment(run_every=2)
def render_sala_espera_jugadas(juego, ronda_actual, mi_decision):
    s = sincronizar_estado_juego(juego)
    if s["fase"] != "jugando" or s["ronda_activa"] != ronda_actual:
        st.rerun()

    jugadas = s["num_respuestas"]
    cupo = s["cupo"]
    faltan = max(0, cupo - jugadas)
    progreso = min(1.0, jugadas / cupo) if cupo > 0 else 0.0

    with st.container(border=True):
        st.markdown(f"### ⏳ Ronda {ronda_actual} — Esperando a que todos los participantes jueguen")
        st.write(
            "Tu elección ya está guardada de forma confidencial. Los resultados y la meta ganadora (2/3 del promedio) "
            "se revelarán automáticamente apenas todos hayan enviado su número."
        )
        st.progress(progreso)
        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Tu número enviado", f"{mi_decision:.1f}")
        c2.metric("🗳️ Jugadas recibidas", f"{jugadas} / {cupo}")
        c3.metric("⏳ Pendientes por jugar", faltan)
        st.caption("🟢 Actualizando en vivo cada 2 segundos...")

@st.fragment(run_every=2)
def render_resultados_ronda_estudiante(juego, ronda_res, cedula, estudiante):
    s = sincronizar_estado_juego(juego)
    if s["fase"] != "resultados" or s["ronda_activa"] != ronda_res:
        st.rerun()

    with get_conn() as conn:
        df_ronda = pd.read_sql_query(
            "SELECT estudiante, cedula, universidad, decision FROM respuestas WHERE juego = ? AND ronda = ?",
            conn, params=(juego, ronda_res)
        )
        ya_listo = conn.execute(
            "SELECT 1 FROM listos_ronda WHERE juego = ? AND ronda = ? AND cedula = ?",
            (juego, ronda_res, cedula)
        ).fetchone() is not None

    fila_mia = df_ronda[df_ronda["cedula"] == cedula]
    participo = not fila_mia.empty
    mi_decision = float(fila_mia["decision"].iloc[0]) if participo else None

    promedio_clase = float(df_ronda["decision"].mean()) if not df_ronda.empty else 0.0
    meta_clase = (2.0 / 3.0) * promedio_clase
    total_jugadores = len(df_ronda)

    ganadores_txt = "—"
    es_ganador = False
    if not df_ronda.empty:
        df_ronda["distancia"] = (df_ronda["decision"] - meta_clase).abs()
        min_dist = df_ronda["distancia"].min()
        ganadores_df = df_ronda[df_ronda["distancia"] == min_dist]
        ganadores_txt = ", ".join([f"{r['estudiante']} ({r['decision']:.1f})" for _, r in ganadores_df.iterrows()])
        if participo and abs(mi_decision - meta_clase) == min_dist:
            es_ganador = True

    with st.container(border=True):
        st.markdown(f"### 📊 Resultados Oficiales — Ronda {ronda_res} de {MAX_RONDAS}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tu número", f"{mi_decision:.1f}" if participo else "Sin jugada")
        c2.metric("Promedio de la clase", f"{promedio_clase:.2f}")
        c3.metric("🎯 Meta (2/3)", f"{meta_clase:.2f}")

        st.divider()
        st.markdown(f"🏆 **Ganador(es) de la Ronda {ronda_res}:** {ganadores_txt}")
        st.caption(f"👥 Total de jugadas computadas en esta ronda: **{total_jugadores}**")

        if participo:
            distancia_mi = abs(mi_decision - meta_clase)
            st.write(f"📏 **Tu distancia a la meta ganadora:** **{distancia_mi:.2f}** unidades")
            if es_ganador:
                st.success("🏆 **¡Felicitaciones! Obtuviste la jugada más cercana a la meta en esta ronda.**")
            elif distancia_mi <= 3.0:
                st.success("🌟 ¡Excelente intuición! Tu número estuvo sumamente cerca de la meta ganadora.")
            elif mi_decision > meta_clase:
                st.info(
                    f"💡 **Retroalimentación:** Tu número ({mi_decision:.1f}) estuvo **por encima** de la meta ({meta_clase:.2f}). "
                    "Recuerda que la meta es 2/3 del promedio; en la siguiente ronda el grupo suele ajustar sus números hacia abajo."
                )
            else:
                st.info(
                    f"💡 **Retroalimentación:** Tu número ({mi_decision:.1f}) estuvo **por debajo** de la meta ({meta_clase:.2f}). "
                    "Observa el comportamiento del grupo para calibrar tu siguiente jugada."
                )
        else:
            st.warning("Te incorporaste después del cierre de esta ronda. Podrás participar en la siguiente.")

    # --- ETAPA 6: ACTIVACIÓN DE LA SIGUIENTE RONDA ---
    if ronda_res < MAX_RONDAS:
        st.divider()
        with st.container(border=True):
            st.markdown(f"#### ⏭️ Etapa 6: Paso a la Ronda {ronda_res + 1}")
            if s["solo_profesor_avanza"]:
                if not ya_listo:
                    if st.button(f"✋ Marcar que estoy listo para la Ronda {ronda_res + 1}", type="primary", use_container_width=True):
                        with get_conn() as conn:
                            conn.execute(
                                "INSERT OR IGNORE INTO listos_ronda (juego, ronda, cedula) VALUES (?, ?, ?)",
                                (juego, ronda_res, cedula)
                            )
                        st.rerun()
                else:
                    st.success(f"✅ Estás listo/a ({s['num_listos']}/{s['cupo']} estudiantes listos).")
                st.caption(
                    f"🟢 **Atento/a:** Tu pantalla abrirá automáticamente la **Ronda {ronda_res + 1}** "
                    "en el instante en que el profesor la active."
                )
            else:
                if not ya_listo:
                    if st.button(
                        f"➡️ Confirmar y pasar a la Ronda {ronda_res + 1} ({s['num_listos']}/{s['cupo']} listos)",
                        type="primary",
                        use_container_width=True
                    ):
                        with get_conn() as conn:
                            conn.execute(
                                "INSERT OR IGNORE INTO listos_ronda (juego, ronda, cedula) VALUES (?, ?, ?)",
                                (juego, ronda_res, cedula)
                            )
                        sincronizar_estado_juego(juego)
                        st.rerun()
                else:
                    st.info(
                        f"⏳ Esperando al resto de compañeros para activar la Ronda {ronda_res + 1}: "
                        f"**{s['num_listos']} de {s['cupo']}** listos 🟢 *(actualizando cada 2s)*"
                    )
    else:
        st.divider()
        mostrar_resumen_final_estudiante(juego, cedula, estudiante)

def mostrar_resumen_final_estudiante(juego, cedula, estudiante):
    if not st.session_state.get("globos_final_mostrados", False):
        st.balloons()
        st.session_state["globos_final_mostrados"] = True

    st.success(f"🎉 **¡Felicitaciones, {estudiante}! Se han completado las {MAX_RONDAS} rondas del experimento.**")
    with get_conn() as conn:
        df_todas = pd.read_sql_query(
            "SELECT ronda, cedula, decision FROM respuestas WHERE juego = ? ORDER BY ronda ASC",
            conn, params=(juego,)
        )
    if not df_todas.empty:
        filas = []
        for r in range(1, MAX_RONDAS + 1):
            df_r = df_todas[df_todas["ronda"] == r]
            if df_r.empty:
                continue
            prom = df_r["decision"].mean()
            meta = (2.0 / 3.0) * prom
            mia = df_r[df_r["cedula"] == cedula]
            mi_val = float(mia["decision"].iloc[0]) if not mia.empty else None
            filas.append({
                "Ronda": f"Ronda {r}",
                "Tu Número": f"{mi_val:.1f}" if mi_val is not None else "—",
                "Promedio Clase": f"{prom:.2f}",
                "Meta (2/3)": f"{meta:.2f}",
                "Tu Distancia": f"{abs(mi_val - meta):.2f}" if mi_val is not None else "—"
            })
        if filas:
            st.subheader("📋 Historial completo de tus 5 rondas:")
            st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
    st.info("👀 Observa el proyector para el análisis final de convergencia hacia el Equilibrio de Nash.")

# ==============================================================================
# BARRA LATERAL: CONFIGURACIÓN Y NAVEGACIÓN
# ==============================================================================
col_sb1, col_sb2 = st.sidebar.columns([1, 1])
with col_sb1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8c/Escudo_de_la_Escuela_Polit%C3%A9cnica_Nacional.png", width=75)
with col_sb2:
    if os.path.exists("logo_dec.png"):
        st.image("logo_dec.png", width=78)

st.sidebar.title("Laboratorio Keynes")
rol = st.sidebar.radio("Modo de vista:", ["👨‍🎓 Estudiante", "👨‍🏫 Profesor (Proyector)"])

juego = "p-Beauty Contest (2/3 del promedio)"
st.sidebar.info("🎯 **Juego:** Concurso de Belleza de Keynes (2/3 del promedio)")

if "app_url" not in st.session_state:
    st.session_state["app_url"] = DEFAULT_APP_URL

st.sidebar.divider()
st.sidebar.markdown("### 📲 Código QR para ingresar")
st.sidebar.image(generar_qr(st.session_state["app_url"]), caption="Escanea con tu celular", use_container_width=True)
st.sidebar.caption(f"[{st.session_state['app_url']}]({st.session_state['app_url']})")

# ==============================================================================
# VISTA DEL ESTUDIANTE
# ==============================================================================
if rol == "👨‍🎓 Estudiante":
    render_encabezado_institucional(
        "🎯 Concurso de Belleza de Keynes",
        f"Experimento interactivo de Teoría de Juegos (2/3 del promedio) — {MAX_RONDAS} rondas sincronizadas"
    )

    tab_jugar, tab_guia = st.tabs([
        "📝 Sala de Juego",
        "📖 Explicación y Reglas del Juego"
    ])

    with tab_guia:
        st.header("🎯 Concurso de Belleza de Keynes (p-Beauty Contest)")
        st.markdown("""
        ### 📌 ¿En qué consiste el juego?
        Cada participante debe elegir un número real entre **0 y 100**.
        Una vez que todos los participantes envían su número, el sistema calcula el **promedio de toda la clase** y determina la **meta**:

        $$\\text{Meta} = \\frac{2}{3} \\times \\text{Promedio General}$$

        🏆 **¿Quién gana?** El jugador cuyo número esté más cerca de la **meta** (menor distancia absoluta).

        ---
        ### 🔄 Dinámica de la sesión (6 etapas):
        1. **Inscripción:** Registra tus datos y universidad.
        2. **Sala de espera:** Aguarda mientras se completa el cupo de participantes.
        3. **Elección de número:** Escoge estratégicamente tu valor entre `0.0` y `100.0`.
        4. **Espera de jugadas:** Aguarda hasta que todos los participantes hayan enviado su decisión.
        5. **Resultados de la ronda:** Analiza el promedio, la meta ganadora ($2/3$) y tu desempeño.
        6. **Siguiente ronda:** Se activa la nueva ronda hasta completar las 5 rondas.

        ---
        ### 📜 Origen histórico: John Maynard Keynes (1936)
        En su obra *Teoría General del Empleo, el Interés y el Dinero*, Keynes comparó los mercados financieros con un concurso de belleza de los periódicos británicos, donde el premio no era para quien eligiera el rostro más bello según su gusto personal, sino para **quien anticipara mejor la preferencia promedio de todos los demás participantes**.
        """)

    with tab_jugar:
        if "est_registrado" not in st.session_state:
            st.session_state["est_registrado"] = False
            st.session_state["est_nombre"] = ""
            st.session_state["est_cedula"] = ""
            st.session_state["est_universidad"] = "Escuela Politécnica Nacional"

        estado_actual = sincronizar_estado_juego(juego)

        # Si el profesor reinició la partida, limpiar sesión local automáticamente
        if st.session_state["est_registrado"]:
            with get_conn() as conn:
                sigue_inscrito = conn.execute(
                    "SELECT estudiante, universidad FROM participantes WHERE juego = ? AND cedula = ?",
                    (juego, st.session_state["est_cedula"])
                ).fetchone()
            if not sigue_inscrito:
                st.session_state["est_registrado"] = False
                st.session_state["globos_final_mostrados"] = False

        # ------------------ ETAPA 1: INSCRIPCIÓN ------------------
        if not st.session_state["est_registrado"]:
            render_stepper(1)
            st.subheader("1️⃣ Inscripción de Participante")
            st.write(
                f"Registra tus datos para ingresar a la sala del experimento "
                f"(Inscritos actuales: **{estado_actual['num_inscritos']} / {estado_actual['cupo']}**)."
            )

            with st.form("form_registro_estudiante"):
                nombre_in = st.text_input("1. Nombre y Apellido:", placeholder="Ej: Juan Pérez").strip()
                cedula_in = st.text_input("2. Cédula (10 dígitos):", max_chars=10, placeholder="Ej: 1712345678").strip()
                universidad_in = st.selectbox(
                    "3. Universidad:",
                    [
                        "Escuela Politécnica Nacional",
                        "Universidad de las Fuerzas Armadas",
                        "Universidad San Francisco de Quito",
                        "Universidad Central del Ecuador"
                    ]
                )
                btn_registro = st.form_submit_button("✅ Inscribirme y Pasar a Sala de Espera", type="primary", use_container_width=True)

                if btn_registro:
                    if not nombre_in:
                        st.error("⚠️ Por favor ingresa tu Nombre y Apellido.")
                    elif not (len(cedula_in) == 10 and cedula_in.isdigit()):
                        st.error("⚠️ La cédula debe contener exactamente 10 dígitos numéricos.")
                    else:
                        with get_conn() as conn:
                            conn.execute(
                                """INSERT INTO participantes (juego, cedula, estudiante, universidad)
                                   VALUES (?, ?, ?, ?)
                                   ON CONFLICT(juego, cedula) DO UPDATE SET
                                       estudiante = excluded.estudiante,
                                       universidad = excluded.universidad""",
                                (juego, cedula_in, nombre_in, universidad_in)
                            )
                        st.session_state["est_nombre"] = nombre_in
                        st.session_state["est_cedula"] = cedula_in
                        st.session_state["est_universidad"] = universidad_in
                        st.session_state["est_registrado"] = True
                        sincronizar_estado_juego(juego)
                        st.rerun()

        else:
            estudiante = st.session_state["est_nombre"]
            cedula = st.session_state["est_cedula"]
            universidad = st.session_state["est_universidad"]

            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.info(f"👤 **{estudiante}** | 🪪 Cédula: **{cedula}** | 🏛️ **{universidad}**")
            with col_btn:
                if st.button("🔄 Cambiar usuario", use_container_width=True):
                    st.session_state["est_registrado"] = False
                    st.rerun()

            estado_actual = sincronizar_estado_juego(juego)
            fase = estado_actual["fase"]
            ronda_activa = estado_actual["ronda_activa"]

            # ------------------ ETAPA 2: SALA DE ESPERA DE INSCRIPCIÓN ------------------
            if fase == "inscripcion":
                render_stepper(2)
                render_sala_espera_inscripcion(juego, estudiante)

            # ------------------ ETAPAS 3 Y 4: RONDA ABIERTA ------------------
            elif fase == "jugando":
                with get_conn() as conn:
                    jugada_actual = conn.execute(
                        "SELECT decision FROM respuestas WHERE juego = ? AND ronda = ? AND cedula = ?",
                        (juego, ronda_activa, cedula)
                    ).fetchone()

                # ETAPA 4: Ya eligió su número -> Espera hasta que todos jueguen
                if jugada_actual is not None:
                    render_stepper(4)
                    render_sala_espera_jugadas(juego, ronda_activa, float(jugada_actual[0]))

                # ETAPA 3: Escoger su número para la ronda activa
                else:
                    render_stepper(3)
                    st.markdown(f"### 3️⃣ Ronda **{ronda_activa}** de **{MAX_RONDAS}** — Escoge tu número")
                    render_monitor_fase_durante_seleccion(juego, ronda_activa)

                    if ronda_activa > 1:
                        r_ant = ronda_activa - 1
                        with get_conn() as conn:
                            df_prev = pd.read_sql_query(
                                "SELECT cedula, decision FROM respuestas WHERE juego = ? AND ronda = ?",
                                conn, params=(juego, r_ant)
                            )
                        if not df_prev.empty:
                            prom_prev = df_prev["decision"].mean()
                            meta_prev = (2.0 / 3.0) * prom_prev
                            mia_prev = df_prev[df_prev["cedula"] == cedula]
                            txt_mia = f" | Tu jugada: **{mia_prev['decision'].iloc[0]:.1f}**" if not mia_prev.empty else ""
                            st.caption(
                                f"💡 Referencia Ronda {r_ant}: Promedio = **{prom_prev:.2f}** | "
                                f"Meta (2/3) = **{meta_prev:.2f}**{txt_mia}"
                            )

                    key_def = f"def_val_{ronda_activa}"
                    if key_def not in st.session_state:
                        st.session_state[key_def] = round(random.uniform(10.0, 90.0), 1)

                    with st.form(f"form_jugada_{ronda_activa}"):
                        st.markdown("#### Selecciona tu número estratégico (0.0 – 100.0)")
                        st.write("Ganará quien quede más cerca de **2/3 del promedio** de todos los participantes en esta ronda.")
                        decision = st.number_input(
                            f"Tu número para la Ronda {ronda_activa}:",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(st.session_state[key_def]),
                            step=0.1,
                            help="Ingresa un número entre 0 y 100."
                        )
                        st.divider()
                        texto_boton = (
                            f"🚀 Enviar mi número de Ronda {ronda_activa}"
                            if ronda_activa < MAX_RONDAS
                            else "🏁 Enviar mi número de Ronda 5 (Final)"
                        )
                        enviado = st.form_submit_button(texto_boton, type="primary", use_container_width=True)

                        if enviado:
                            verif = sincronizar_estado_juego(juego)
                            if verif["fase"] != "jugando" or verif["ronda_activa"] != ronda_activa:
                                st.rerun()
                            with get_conn() as conn:
                                conn.execute(
                                    """INSERT INTO respuestas (juego, ronda, estudiante, cedula, universidad, decision)
                                       VALUES (?, ?, ?, ?, ?, ?)
                                       ON CONFLICT(juego, ronda, cedula) DO NOTHING""",
                                    (juego, ronda_activa, estudiante, cedula, universidad, float(decision))
                                )
                            sincronizar_estado_juego(juego)
                            st.rerun()

            # ------------------ ETAPAS 5 Y 6: RESULTADOS Y PASO A SIGUIENTE RONDA ------------------
            elif fase == "resultados":
                render_stepper(5)
                render_resultados_ronda_estudiante(juego, ronda_activa, cedula, estudiante)

            # ------------------ JUEGO COMPLETADO ------------------
            else:
                render_stepper(6)
                mostrar_resumen_final_estudiante(juego, cedula, estudiante)

# ==============================================================================
# VISTA DEL PROFESOR (PROYECTOR Y CONTROL DE SESIÓN)
# ==============================================================================
else:
    estado_global = sincronizar_estado_juego(juego)

    render_encabezado_institucional(
        "📊 Panel de Control del Profesor",
        f"Gestión en vivo del experimento — Cupo configurado: {estado_global['cupo']} estudiantes"
    )

    docente_password = st.secrets.get("DOCENTE_PASSWORD", "epn2026")
    clave = st.sidebar.text_input("Contraseña docente:", type="password")

    if clave == docente_password:
        # --- BARRA DE CONFIGURACIÓN DEL PROFESOR (FUERA DEL FRAGMENTO DE 2s PARA EDICIÓN FLUIDA) ---
        with st.container(border=True):
            st.markdown("#### ⚙️ Configuración de la Sesión")
            cfg_c1, cfg_c2, cfg_c3 = st.columns([1.3, 1.5, 1])

            with cfg_c1:
                nuevo_cupo = st.number_input(
                    "👥 Número total de estudiantes participantes:",
                    min_value=1,
                    max_value=500,
                    value=int(estado_global["cupo"]),
                    step=1,
                    help="Por defecto 20 estudiantes. Define cuántos alumnos deben inscribirse y jugar cada ronda para avanzar automáticamente."
                )
                if int(nuevo_cupo) != int(estado_global["cupo"]):
                    actualizar_sesion(juego, cupo=int(nuevo_cupo))
                    sincronizar_estado_juego(juego)
                    st.rerun()

            with cfg_c2:
                solo_prof_nuevo = st.toggle(
                    "🎛️ Activar siguiente ronda manualmente (Profesor)",
                    value=estado_global["solo_profesor_avanza"],
                    help="Activado (recomendado para clase con proyector): tras mostrar resultados en el Paso 5, el profesor decide cuándo activar la siguiente ronda. Desactivado: pasa automáticamente cuando todos pulsan 'Listo'."
                )
                if bool(solo_prof_nuevo) != bool(estado_global["solo_profesor_avanza"]):
                    actualizar_sesion(juego, solo_profesor_avanza=solo_prof_nuevo)
                    sincronizar_estado_juego(juego)
                    st.rerun()

            with cfg_c3:
                st.write("")
                with st.popover("🗑️ Reiniciar Partida", use_container_width=True):
                    st.markdown("##### Reiniciar experimento")
                    st.caption("Vuelve a la Etapa 1 (Inscripción) manteniendo el cupo configurado.")
                    if st.button("🧹 Reiniciar partida actual", type="primary", use_container_width=True, key="main_reset_juego"):
                        reiniciar_juego_db(juego, borrar_todo=False, mantener_cupo=int(nuevo_cupo))
                        st.session_state.pop("ronda_proyectada", None)
                        st.session_state["seguir_ronda_activa"] = True
                        st.rerun()
                    st.divider()
                    if st.button("⚠️ Restablecer todo de fábrica (Cupo = 20)", use_container_width=True, key="main_reset_todo"):
                        reiniciar_juego_db(juego, borrar_todo=True, mantener_cupo=DEFAULT_CUPO)
                        st.session_state.pop("ronda_proyectada", None)
                        st.session_state["seguir_ronda_activa"] = True
                        st.rerun()

        # --- PANEL EN VIVO DEL PROYECTOR (ACTUALIZACIÓN AUTOMÁTICA CADA 2 SEGUNDOS) ---
        @st.fragment(run_every=2)
        def render_panel_profesor_en_vivo(juego):
            s = sincronizar_estado_juego(juego)
            ronda_activa = s["ronda_activa"]
            fase = s["fase"]
            cupo = s["cupo"]
            num_inscritos = s["num_inscritos"]
            num_respuestas = s["num_respuestas"]
            num_listos = s["num_listos"]

            if st.session_state.get("seguir_ronda_activa", True) or "ronda_proyectada" not in st.session_state:
                st.session_state["ronda_proyectada"] = ronda_activa
            ronda_proy = st.session_state["ronda_proyectada"]

            # Indicador visual de etapa actual
            mapa_paso = {"inscripcion": 2 if num_inscritos > 0 else 1, "jugando": 4 if num_respuestas > 0 else 3, "resultados": 5, "finalizado": 6}
            render_stepper(mapa_paso.get(fase, 1))

            with get_conn() as conn:
                df_inscritos = pd.read_sql_query(
                    "SELECT estudiante, cedula, universidad FROM participantes WHERE juego = ? ORDER BY id ASC",
                    conn, params=(juego,)
                )
                df_proy = pd.read_sql_query(
                    "SELECT estudiante, cedula, universidad, decision FROM respuestas WHERE juego = ? AND ronda = ?",
                    conn, params=(juego, ronda_proy)
                )
                df_activa = pd.read_sql_query(
                    "SELECT estudiante, cedula, universidad, decision FROM respuestas WHERE juego = ? AND ronda = ?",
                    conn, params=(juego, ronda_activa)
                )
                df_hist = pd.read_sql_query(
                    "SELECT ronda, AVG(decision) as promedio, COUNT(DISTINCT coalesce(cedula, estudiante)) as participantes "
                    "FROM respuestas WHERE juego = ? GROUP BY ronda ORDER BY ronda",
                    conn, params=(juego,)
                )

            # --- CONTROL CENTRAL SINCRONIZADO DE LAS 6 ETAPAS ---
            with st.container(border=True):
                etiquetas_fase = {
                    "inscripcion": "1º-2º INSCRIPCIÓN Y SALA DE ESPERA",
                    "jugando": f"3º-4º RONDA {ronda_activa} EN JUEGO",
                    "resultados": f"5º RESULTADOS RONDA {ronda_activa}",
                    "finalizado": "🏁 JUEGO FINALIZADO (5 RONDAS)"
                }
                m1, m2, m3, m4 = st.columns([1.4, 1, 1, 1])
                m1.metric("📡 Etapa actual", etiquetas_fase.get(fase, fase))
                m2.metric("👥 Inscritos en sala", f"{num_inscritos} / {cupo}")
                m3.metric(f"🗳️ Jugadas Ronda {ronda_activa}", f"{num_respuestas} / {cupo}")
                m4.metric("📍 Ronda proyectada", f"Ronda {ronda_proy} de {MAX_RONDAS}")

                st.divider()

                # Controles contextuales según la etapa
                if fase == "inscripcion":
                    prog_ins = min(1.0, num_inscritos / cupo) if cupo > 0 else 0.0
                    st.progress(prog_ins)
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(
                            f"⏳ **Sala de espera activa:** Esperando a completar **{cupo}** estudiantes inscritos "
                            f"(actualmente **{num_inscritos}**). Al llegar a {cupo}, la Ronda 1 comenzará automáticamente."
                        )
                    with col_b:
                        txt_ini = (
                            f"▶️ Iniciar Ronda 1 ahora (con {num_inscritos} inscritos)"
                            if num_inscritos > 0
                            else "▶️ Iniciar Ronda 1 manualmente"
                        )
                        if st.button(txt_ini, type="primary", use_container_width=True):
                            nuevo_c = num_inscritos if num_inscritos > 0 else cupo
                            actualizar_sesion(juego, ronda_activa=1, fase="jugando", cupo=nuevo_c)
                            st.session_state["seguir_ronda_activa"] = True
                            st.session_state["ronda_proyectada"] = 1
                            st.rerun()

                    with st.expander(f"📋 Ver lista de estudiantes inscritos en sala de espera ({num_inscritos})", expanded=num_inscritos > 0):
                        if df_inscritos.empty:
                            st.caption("Aún ningún estudiante ha completado el formulario de inscripción.")
                        else:
                            st.dataframe(
                                df_inscritos.rename(columns={"estudiante": "Nombre y Apellido", "cedula": "Cédula", "universidad": "Universidad"}),
                                use_container_width=True,
                                hide_index=True
                            )

                elif fase == "jugando":
                    prog_jug = min(1.0, num_respuestas / cupo) if cupo > 0 else 0.0
                    st.progress(prog_jug)
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(
                            f"🎯 **Ronda {ronda_activa} abierta:** Los estudiantes están eligiendo su número (**{num_respuestas} de {cupo}** recibidos). "
                            f"Al completarse las {cupo} jugadas, los resultados se mostrarán automáticamente."
                        )
                    with col_b:
                        if st.button(f"🔓 Cerrar y Mostrar Resultados Ronda {ronda_activa}", type="primary", use_container_width=True):
                            actualizar_sesion(juego, fase="resultados")
                            st.session_state["seguir_ronda_activa"] = True
                            st.session_state["ronda_proyectada"] = ronda_activa
                            st.rerun()

                    if not df_inscritos.empty:
                        cedulas_jugaron = set(df_activa["cedula"].dropna().tolist())
                        pendientes = df_inscritos[~df_inscritos["cedula"].isin(cedulas_jugaron)]
                        with st.expander(f"👀 Estado de entrega por estudiante — Pendientes: {len(pendientes)}"):
                            df_est_entrega = df_inscritos.copy()
                            df_est_entrega["Estado"] = df_est_entrega["cedula"].apply(
                                lambda c: "✅ Jugada enviada" if c in cedulas_jugaron else "⏳ Eligiendo número..."
                            )
                            st.dataframe(
                                df_est_entrega[["estudiante", "universidad", "Estado"]].rename(
                                    columns={"estudiante": "Estudiante", "universidad": "Universidad"}
                                ),
                                use_container_width=True,
                                hide_index=True
                            )

                elif fase == "resultados":
                    col_a, col_b, col_c = st.columns([2, 1.2, 0.8])
                    with col_a:
                        if ronda_activa < MAX_RONDAS:
                            st.write(
                                f"✅ **Resultados de Ronda {ronda_activa} visibles en celulares y proyector.** "
                                f"Estudiantes marcados como listos: **{num_listos} / {cupo}**."
                            )
                        else:
                            st.success(f"🏁 **Ronda {MAX_RONDAS} completada.** Resultados finales en pantalla.")
                    with col_b:
                        if ronda_activa < MAX_RONDAS:
                            if st.button(f"➡️ 6º Activar Ronda {ronda_activa + 1}", type="primary", use_container_width=True):
                                actualizar_sesion(juego, ronda_activa=ronda_activa + 1, fase="jugando")
                                st.session_state["seguir_ronda_activa"] = True
                                st.session_state["ronda_proyectada"] = ronda_activa + 1
                                st.rerun()
                        else:
                            if st.button("🏁 Marcar experimento como Finalizado", type="primary", use_container_width=True):
                                actualizar_sesion(juego, fase="finalizado")
                                st.rerun()
                    with col_c:
                        if st.button(f"🔓 Reabrir Ronda {ronda_activa}", type="secondary", use_container_width=True):
                            actualizar_sesion(juego, fase="jugando")
                            st.rerun()

                else:
                    st.success(f"🎉 **Experimento finalizado ({MAX_RONDAS} rondas completadas).** Puedes explorar cada ronda abajo o reiniciar la partida arriba.")

            # --- RECUADROS INTERACTIVOS COMO BOTONES PARA ELEGIR LA RONDA A PROYECTAR ---
            st.markdown("##### 📌 Selecciona la ronda que deseas proyectar en pantalla:")
            r_cols = st.columns(MAX_RONDAS)
            for r_num in range(1, MAX_RONDAS + 1):
                count_r = df_hist[df_hist["ronda"] == r_num]["participantes"].values
                val = int(count_r[0]) if len(count_r) > 0 else 0
                es_sel = (r_num == ronda_proy)
                texto_alumnos = f"{val} alumno" if val == 1 else f"{val} alumnos"

                with r_cols[r_num - 1]:
                    with st.container(border=True):
                        st.metric(f"Ronda {r_num}", texto_alumnos)
                        texto_btn = "👁️ Proyectando" if es_sel else f"Ver Ronda {r_num}"
                        if st.button(
                            texto_btn,
                            key=f"btn_ronda_sel_{r_num}",
                            use_container_width=True,
                            type="primary" if es_sel else "secondary"
                        ):
                            st.session_state["ronda_proyectada"] = r_num
                            st.session_state["seguir_ronda_activa"] = (r_num == ronda_activa)
                            st.rerun()

            # --- RESULTADOS Y GRÁFICOS DE LA RONDA PROYECTADA ---
            # Se muestran automáticamente en Etapa 5 ('resultados'/'finalizado') o al consultar rondas anteriores ya cerradas
            ronda_proy_cerrada = (
                (ronda_proy < ronda_activa)
                or (ronda_proy == ronda_activa and fase in ("resultados", "finalizado"))
            )

            if ronda_proy_cerrada:
                if df_proy.empty:
                    st.warning(f"No hay respuestas registradas en la Ronda {ronda_proy}.")
                else:
                    st.divider()
                    st.subheader(f"📊 Análisis y Resultados — Ronda {ronda_proy}")
                    promedio = df_proy["decision"].mean()
                    meta = (2.0 / 3.0) * promedio
                    df_proy["distancia"] = (df_proy["decision"] - meta).abs()
                    min_dist = df_proy["distancia"].min()
                    ganadores = df_proy[df_proy["distancia"] == min_dist]

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Promedio de la clase", f"{promedio:.2f}")
                    c2.metric("🎯 Meta (2/3 del promedio)", f"{meta:.2f}")
                    nombres_ganadores = ", ".join([
                        f"{row['estudiante']} ({row['universidad']}) — {row['decision']:.1f}"
                        if pd.notna(row.get("universidad")) and row.get("universidad")
                        else f"{row['estudiante']} ({row['decision']:.1f})"
                        for _, row in ganadores.iterrows()
                    ])
                    c3.metric("🏆 Ganador(es)", nombres_ganadores)

                    fig = px.histogram(
                        df_proy, x="decision", nbins=25,
                        title=f"Distribución de Elecciones de la Clase — Ronda {ronda_proy}",
                        labels={"decision": "Número Elegido", "count": "Frecuencia"},
                        color_discrete_sequence=["#18243E"]
                    )
                    fig.add_vline(x=promedio, line_dash="dash", line_width=2.5, line_color="#3D1A4A", annotation_text=f"Promedio ({promedio:.1f})")
                    fig.add_vline(x=meta, line_dash="solid", line_width=3, line_color="#E96132", annotation_text=f"Meta 2/3 ({meta:.1f})")
                    fig.update_layout(
                        xaxis=dict(range=[0, 100]),
                        plot_bgcolor="#F7F8FC",
                        paper_bgcolor="#FFFFFF",
                        font=dict(family="Varela Round, Segoe UI, sans-serif", color="#18243E"),
                        title_font=dict(color="#3D1A4A", size=18)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("🧠 Guía de razonamiento estratégico (Niveles k) — Para debate docente", expanded=True):
                        st.markdown(f"""
                        **Resultados de la Ronda {ronda_proy}:** Promedio de la clase = **{promedio:.2f}** | Meta (2/3 del promedio) = **{meta:.2f}**

                        ---
                        ### 🧠 Guía de razonamiento estratégico (Niveles $k$):
                        * **Nivel 0 (Ingenuo / Aleatorio):** Las personas eligen números al azar entre 0 y 100. El promedio esperado sería alrededor de **50**.
                        * **Nivel 1 (Primer orden de deducción):** Si crees que los demás jugarán al azar (promedio 50), deberías jugar: $\\frac{2}{3} \\times 50 \\approx \\mathbf{{33.3}}$
                        * **Nivel 2 (Segundo orden):** Si piensas que los demás son listos y jugarán 33.3, deberías anticiparte jugando: $\\frac{2}{3} \\times 33.3 \\approx \\mathbf{{22.2}}$
                        * **Nivel 3:** Si todos hacen lo anterior: $\\frac{2}{3} \\times 22.2 \\approx \\mathbf{{14.8}}$
                        * **Equilibrio de Nash (Racionalidad común infinita):** Si este proceso se repite infinitas veces, el único número donde nadie tiene incentivos a desviarse es el **0**.

                        > ⚠️ **¡Pero cuidado!** En el mundo real no todos son perfectamente racionales. Si tú juegas 0 pero el resto juega 50, ¡perderás! Tu reto es predecir la profundidad de pensamiento de tus compañeros hoy.
                        """)

                    if len(df_hist) > 1:
                        st.subheader("📈 Evolución a lo largo de las rondas (Convergencia hacia Nash)")
                        fig_evol = px.line(
                            df_hist, x="ronda", y="promedio", markers=True,
                            title="Convergencia del Promedio hacia el Equilibrio de Nash (0)",
                            labels={"ronda": "Ronda", "promedio": "Promedio de la decisión"},
                            color_discrete_sequence=["#E96132"]
                        )
                        fig_evol.update_traces(
                            line=dict(color="#E96132", width=3.2),
                            marker=dict(size=10, color="#18243E", line=dict(width=2, color="#FFFFFF"))
                        )
                        fig_evol.update_layout(
                            xaxis=dict(dtick=1),
                            plot_bgcolor="#F7F8FC",
                            paper_bgcolor="#FFFFFF",
                            font=dict(family="Varela Round, Segoe UI, sans-serif", color="#18243E"),
                            title_font=dict(color="#3D1A4A", size=18)
                        )
                        st.plotly_chart(fig_evol, use_container_width=True)

                    with st.expander(f"📋 Ver tabla completa de registros de la Ronda {ronda_proy}"):
                        df_mostrar = df_proy.rename(columns={
                            "estudiante": "Nombre y Apellido",
                            "cedula": "Cédula",
                            "universidad": "Universidad",
                            "decision": "Número Elegido",
                            "distancia": "Distancia a la Meta"
                        })
                        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            else:
                st.info(
                    f"🔒 **Resultados ocultos en el proyector mientras la sesión está en '{etiquetas_fase.get(fase, fase)}'** "
                    "para no sesgar las decisiones de los estudiantes. Se mostrarán automáticamente apenas todos terminen de jugar."
                )

        render_panel_profesor_en_vivo(juego)

        # --- CÓDIGO QR PERMANENTEMENTE VISIBLE PARA EL PROYECTOR ---
        st.divider()
        with st.container(border=True):
            col_qr1, col_qr2 = st.columns([1, 2])
            with col_qr1:
                st.image(generar_qr(st.session_state["app_url"]), caption="Escanea para unirte a la partida", width=220)
            with col_qr2:
                st.markdown("### 📱 ¡Únete al juego desde tu celular!")
                st.markdown("""
                1. Apunta con la **cámara de tu teléfono** al código QR para ingresar.
                2. **Inscríbete** y espera en la **Sala de Espera** hasta completar el grupo.
                3. Elige tu número en cada ronda y compite por acercarte a **2/3 del promedio**.
                """)
                url_editada = st.text_input(
                    "🔗 Enlace web del juego (editable si cambia el dominio):",
                    value=st.session_state["app_url"],
                    key="input_url_qr"
                )
                if url_editada != st.session_state["app_url"]:
                    st.session_state["app_url"] = url_editada
                    st.rerun()
                st.markdown(f"👉 **Enlace directo:** [{st.session_state['app_url']}]({st.session_state['app_url']})")

    else:
        if clave:
            st.error("❌ Contraseña incorrecta. Por favor verifica tus credenciales.")
        else:
            st.info("🔒 Ingresa la contraseña docente en la barra lateral izquierda para configurar el número de estudiantes y controlar la sesión.")
