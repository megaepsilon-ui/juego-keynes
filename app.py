import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import io
import urllib.parse
import random
import os
import base64

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
# - Dorado DeC: #F0B840 | Rojo DeC: #E01818 | Texto cuerpo: #4A5568 / #868585
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
        padding: 22px 28px;
        margin-bottom: 20px;
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
        font-size: 0.75rem;
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
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 4px 0 !important;
        line-height: 1.2;
    }
    .dec-hero-sub {
        color: rgba(255, 255, 255, 0.85) !important;
        font-size: 0.95rem;
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
        height: 68px;
        width: auto;
        display: block;
    }
    @media (max-width: 640px) {
        .dec-hero-banner {
            padding: 16px 18px;
            flex-direction: row;
        }
        .dec-hero-title {
            font-size: 1.35rem;
        }
        .dec-hero-logo-box img {
            height: 50px;
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

MAX_RONDAS = 5
DEFAULT_APP_URL = st.secrets.get("APP_URL", "https://juego-keynes-epn.streamlit.app/")

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

# --- CONEXIÓN Y BASE DE DATOS LOCAL ---
def get_conn():
    return sqlite3.connect("juegos_clase.db", check_same_thread=False)

def init_db():
    with get_conn() as conn:
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
            CREATE TABLE IF NOT EXISTS estado_sesion (
                juego TEXT PRIMARY KEY,
                ronda_activa INTEGER DEFAULT 1,
                estado TEXT DEFAULT 'abierta'
            )
        """)
        # Migración automática si la tabla fue creada previamente sin estas columnas
        cursor = conn.execute("PRAGMA table_info(respuestas)")
        cols = [c[1] for c in cursor.fetchall()]
        if "cedula" not in cols:
            conn.execute("ALTER TABLE respuestas ADD COLUMN cedula TEXT")
        if "universidad" not in cols:
            conn.execute("ALTER TABLE respuestas ADD COLUMN universidad TEXT")
init_db()

def get_estado_sesion(juego):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT ronda_activa, estado FROM estado_sesion WHERE juego = ?",
            (juego,)
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO estado_sesion (juego, ronda_activa, estado) VALUES (?, 1, 'abierta')",
                (juego,)
            )
            return 1, "abierta"
        return int(row[0]), str(row[1])

def set_estado_sesion(juego, ronda, estado):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO estado_sesion (juego, ronda_activa, estado)
            VALUES (?, ?, ?)
            ON CONFLICT(juego) DO UPDATE SET ronda_activa=excluded.ronda_activa, estado=excluded.estado
        """, (juego, ronda, estado))

@st.fragment(run_every=2)
def render_resumen_en_vivo_estudiante(juego, r_res, mi_decision, estudiante, dict_jugadas, rondas_jugadas):
    st.markdown(f"### 📊 Resultados de tu Ronda {r_res} de {MAX_RONDAS}")
    st.progress(r_res / MAX_RONDAS)
    
    with get_conn() as conn:
        df_ronda_clase = pd.read_sql_query(
            "SELECT decision FROM respuestas WHERE juego = ? AND ronda = ?",
            conn, params=(juego, r_res)
        )
    
    promedio_clase = df_ronda_clase["decision"].mean() if not df_ronda_clase.empty else mi_decision
    meta_clase = (2 / 3) * promedio_clase
    distancia_mi = abs(mi_decision - meta_clase)
    total_jugadores = len(df_ronda_clase)
    
    with st.container(border=True):
        st.markdown("#### 🎯 Resultados de la Ronda (actualizándose en vivo):")
        c1, c2, c3 = st.columns(3)
        c1.metric("Tu número", f"{mi_decision:.1f}")
        c2.metric("Promedio clase", f"{promedio_clase:.2f}")
        c3.metric("Meta (2/3)", f"{meta_clase:.2f}")
        
        st.divider()
        st.write(f"📏 **Tu distancia a la meta ganadora:** **{distancia_mi:.2f}** unidades")
        st.caption(f"👥 Respuestas registradas en la clase: **{total_jugadores}** 🟢 *(actualizando en vivo cada 2 segundos)*")
        
        if distancia_mi <= 3.0:
            st.success("🌟 ¡Excelente intuición! Tu número estuvo sumamente cerca de la meta ganadora.")
        elif mi_decision > meta_clase:
            st.info(f"💡 **Retroalimentación:** Tu número ({mi_decision:.1f}) estuvo **por encima** de la meta ({meta_clase:.2f}). Recuerda que la meta es 2/3 del promedio. ¡Para la siguiente ronda la clase tenderá a jugar números más bajos!")
        else:
            st.info(f"💡 **Retroalimentación:** Tu número ({mi_decision:.1f}) estuvo **por debajo** de la meta ({meta_clase:.2f}). ¡Interesante estrategia! Observa la meta calculada para calibrar tu siguiente jugada.")
    
    if r_res < MAX_RONDAS:
        st.divider()
        st.markdown(f"##### ¿Listo para la Ronda {r_res + 1}?")
        st.caption(f"Toma en cuenta la meta actual (**{meta_clase:.2f}**) para estimar tu siguiente número estratégico.")
        if st.button(f"➡️ Continuar a la Ronda {r_res + 1}", type="primary", use_container_width=True):
            st.session_state[f"continuar_despues_de_{r_res}"] = True
            st.rerun()
    else:
        st.divider()
        if not st.session_state.get(f"globos_mostrados_{r_res}", False):
            st.balloons()
            st.session_state[f"globos_mostrados_{r_res}"] = True
        st.success(f"🎉 **¡Felicitaciones, {estudiante}! Has completado las {MAX_RONDAS} rondas del juego.**")
        
        df_resumen = pd.DataFrame([
            {"Ronda": r, "Tu Decisión": dict_jugadas[r]} for r in rondas_jugadas
        ])
        st.subheader("📋 Resumen histórico de tus decisiones:")
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)
        st.info("👀 Observa el proyector para ver el análisis de la clase y la convergencia hacia el Equilibrio de Nash.")

# --- BARRA LATERAL: CONFIGURACIÓN ---
col_sb1, col_sb2 = st.sidebar.columns([1, 1])
with col_sb1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8c/Escudo_de_la_Escuela_Polit%C3%A9cnica_Nacional.png", width=75)
with col_sb2:
    if os.path.exists("logo_dec.png"):
        st.image("logo_dec.png", width=78)
st.sidebar.title("Laboratorio Keynes")
rol = st.sidebar.radio("Modo de vista:", ["👨‍🎓 Estudiante", "👨‍🏫 Profesor (Proyector)"])

# Juego fijado: Concurso de Belleza de Keynes
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
        f"Experimento interactivo de Teoría de Juegos (2/3 del promedio) — Máximo {MAX_RONDAS} rondas"
    )
    
    # --- PESTAÑAS: JUEGO / GUÍA Y EXPLICACIÓN ---
    tab_jugar, tab_guia = st.tabs([
        "📝 Realizar mi Jugada",
        "📖 Explicación y Reglas del Juego"
    ])
    
    # ------------------ PESTAÑA 2: GUÍA Y EXPLICACIÓN ------------------
    with tab_guia:
        st.header("🎯 Concurso de Belleza de Keynes (p-Beauty Contest)")
        st.markdown("""
        ### 📌 ¿En qué consiste el juego?
        Cada participante debe elegir un número real entre **0 y 100**. 
        Una vez que todos envían su número, el sistema calcula el **promedio de toda la clase** y luego calcula la **meta**:
        
        $$\\text{Meta} = \\frac{2}{3} \\times \\text{Promedio General}$$
        
        🏆 **¿Quién gana?** El jugador cuyo número esté más cerca de la **meta** (menor distancia absoluta).
        
        ---
        ### 📜 Origen histórico: John Maynard Keynes (1936)
        En su famosa obra *Teoría General del Empleo, el Interés y el Dinero*, Keynes comparó los mercados financieros con un concurso de belleza de los periódicos británicos de su época, donde el premio no era para quien eligiera a la cara más bella según su gusto, sino para **quien adivinara la preferencia media de todos los lectores**.
        
        > *"No se trata de elegir según el gusto personal, ni siquiera según la auténtica belleza, sino de anticipar lo que la opinión promedio cree que será la opinión promedio."*
        
        ---
        ### 🎯 Desafío para el jugador:
        * No se trata de elegir tu número favorito ni de buscar una respuesta matemática aislada.
        * Tu reto es **anticipar la mentalidad y comportamiento de tus compañeros**: adivinar qué número jugarán en promedio y posicionarte estratégicamente a **2/3 de ese promedio**.
        * ¿Qué número crees que elegirá la mayoría en esta ronda?
        """)
    
    # ------------------ PESTAÑA 1: FORMULARIO DE JUGADA ------------------
    with tab_jugar:
        if "est_registrado" not in st.session_state:
            st.session_state["est_registrado"] = False
            st.session_state["est_nombre"] = ""
            st.session_state["est_cedula"] = ""
            st.session_state["est_universidad"] = "Escuela Politécnica Nacional"

        if not st.session_state["est_registrado"]:
            st.subheader("📋 Registro de Participante")
            st.write("Completa tus datos para habilitar tus decisiones en el laboratorio:")
            
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
                btn_registro = st.form_submit_button("✅ Guardar y Comenzar a Jugar", type="primary", use_container_width=True)
                
                if btn_registro:
                    if not nombre_in:
                        st.error("⚠️ Por favor ingresa tu Nombre y Apellido.")
                    elif not (len(cedula_in) == 10 and cedula_in.isdigit()):
                        st.error("⚠️ La cédula debe contener exactamente 10 dígitos numéricos.")
                    else:
                        st.session_state["est_nombre"] = nombre_in
                        st.session_state["est_cedula"] = cedula_in
                        st.session_state["est_universidad"] = universidad_in
                        st.session_state["est_registrado"] = True
                        st.rerun()
        else:
            estudiante = st.session_state["est_nombre"]
            cedula = st.session_state["est_cedula"]
            universidad = st.session_state["est_universidad"]

            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.info(f"👤 **{estudiante}** | 🪪 Cédula: **{cedula}** | 🏛️ **{universidad}**")
            with col_btn:
                if st.button("🔄 Cambiar datos / Jugador"):
                    st.session_state["est_registrado"] = False
                    st.session_state["est_nombre"] = ""
                    st.session_state["est_cedula"] = ""
                    st.rerun()

            with get_conn() as conn:
                res = conn.execute(
                    "SELECT ronda, decision FROM respuestas WHERE juego = ? AND cedula = ? ORDER BY ronda ASC",
                    (juego, cedula)
                ).fetchall()
            
            dict_jugadas = {r[0]: r[1] for r in res}
            rondas_jugadas = sorted(list(dict_jugadas.keys()))
            ultima_ronda = max(rondas_jugadas) if rondas_jugadas else 0

            # Alternativa B: Al enviar una ronda, mostrar pantalla de resumen antes de permitir pasar a la siguiente
            debe_ver_resumen = (ultima_ronda > 0) and not st.session_state.get(f"continuar_despues_de_{ultima_ronda}", False)

            # Caso 1: Mostrar resumen de la ronda recién enviada antes de avanzar (se actualiza en vivo cada 2s)
            if debe_ver_resumen:
                r_res = ultima_ronda
                mi_decision = dict_jugadas[r_res]
                render_resumen_en_vivo_estudiante(juego, r_res, mi_decision, estudiante, dict_jugadas, rondas_jugadas)

            # Caso 2: Ya completó las 5 rondas y ya revisó el resumen
            elif len(rondas_jugadas) >= MAX_RONDAS:
                st.success(f"🎉 **¡Excelente, {estudiante}! Has completado las {MAX_RONDAS} rondas del juego.**")
                st.progress(1.0)
                
                df_resumen = pd.DataFrame([
                    {"Ronda": r, "Tu Decisión": dict_jugadas[r]} for r in rondas_jugadas
                ])
                st.subheader("📋 Resumen de tus decisiones en las 5 rondas:")
                st.dataframe(df_resumen, use_container_width=True, hide_index=True)
                st.info("Observa el proyector para ver el análisis general de la clase.")

            # Caso 3: Formulario para responder la ronda correspondiente
            else:
                ronda_a_jugar = len(rondas_jugadas) + 1
                
                st.markdown(f"### 📍 Ronda **{ronda_a_jugar}** de **{MAX_RONDAS}**")
                st.progress((ronda_a_jugar - 1) / MAX_RONDAS)
                
                if ronda_a_jugar > 1:
                    r_ant = ronda_a_jugar - 1
                    with get_conn() as conn:
                        df_prev = pd.read_sql_query(
                            "SELECT decision FROM respuestas WHERE juego = ? AND ronda = ?",
                            conn, params=(juego, r_ant)
                        )
                    if not df_prev.empty:
                        meta_prev = (2 / 3) * df_prev["decision"].mean()
                        st.caption(f"💡 Recordatorio: En la Ronda {r_ant}, la meta fue **{meta_prev:.2f}** (tu jugada fue **{dict_jugadas.get(r_ant, 0):.1f}**).")

                key_def = f"def_val_{ronda_a_jugar}"
                if key_def not in st.session_state:
                    st.session_state[key_def] = round(random.uniform(10.0, 90.0), 1)
                
                with st.form(f"form_jugada_{ronda_a_jugar}"):
                    st.markdown("#### Selecciona tu número estratégico (0.0 - 100.0)")
                    st.write("Debes escoger un valor entre **0 y 100**. Ganará quien esté más cerca de **2/3 del promedio** de toda la clase.")
                    decision = st.number_input(
                        f"Tu número para la Ronda {ronda_a_jugar}:",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(st.session_state[key_def]),
                        step=0.1,
                        help="Ingresa el valor que crees que igualará 2/3 del promedio de todos."
                    )
                    
                    st.divider()
                    texto_boton = f"🚀 Confirmar y Enviar Ronda {ronda_a_jugar}" if ronda_a_jugar < MAX_RONDAS else "🏁 Confirmar y Finalizar Ronda 5"
                    enviado = st.form_submit_button(texto_boton, type="primary", use_container_width=True)
                    
                    if enviado:
                        try:
                            with get_conn() as conn:
                                conn.execute(
                                    "INSERT INTO respuestas (juego, ronda, estudiante, cedula, universidad, decision) VALUES (?, ?, ?, ?, ?, ?)",
                                    (juego, ronda_a_jugar, estudiante, cedula, universidad, float(decision))
                                )
                            st.session_state[f"continuar_despues_de_{ronda_a_jugar}"] = False
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.warning(f"Ya se había registrado una respuesta para la Ronda {ronda_a_jugar} con tu cédula.")

# ==============================================================================
# VISTA DEL PROFESOR (PROYECTOR)
# ==============================================================================
else:
    ronda_activa_global, estado_sesion_global = get_estado_sesion(juego)
    if "ronda_proyectada" not in st.session_state:
        st.session_state["ronda_proyectada"] = min(ronda_activa_global, MAX_RONDAS)
    
    ronda = st.session_state["ronda_proyectada"]
    
    render_encabezado_institucional(
        "📊 Panel de Control del Profesor",
        f"Visualización central para proyector — Mostrando Ronda {ronda} de {MAX_RONDAS}"
    )
    
    # Obtener contraseña desde secrets si existe, o usar predeterminada
    docente_password = st.secrets.get("DOCENTE_PASSWORD", "epn2026")
    clave = st.sidebar.text_input("Contraseña docente:", type="password")
    
    if clave == docente_password:
        ronda_activa, estado_sesion = get_estado_sesion(juego)

        with get_conn() as conn:
            df = pd.read_sql_query(
                "SELECT estudiante, cedula, universidad, decision FROM respuestas WHERE juego = ? AND ronda = ?",
                conn, params=(juego, ronda)
            )
            df_hist = pd.read_sql_query(
                "SELECT ronda, AVG(decision) as promedio, COUNT(DISTINCT coalesce(cedula, estudiante)) as participantes FROM respuestas WHERE juego = ? GROUP BY ronda ORDER BY ronda",
                conn, params=(juego,)
            )

        # CONTROL CENTRALIZADO DE RONDAS (SINCRONIZACIÓN DE CLASE)
        st.subheader("🎛️ Control Central de Rondas (Sincronizado con la clase)")
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns([1, 1, 2])
            col_c1.metric("📍 Ronda activa en clase", f"Ronda {ronda_activa} de {MAX_RONDAS}")
            estado_texto = "🟢 ABIERTA (Recibiendo jugadas)" if estado_sesion == "abierta" else "🔴 CERRADA (En discusión)"
            col_c2.metric("📡 Estado para alumnos", estado_texto)
            
            with col_c3:
                st.write("**Acciones para sincronizar la clase:**")
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if estado_sesion == "abierta":
                        if st.button(f"🔒 Cerrar Ronda {ronda_activa} y Revelar", type="primary", use_container_width=True):
                            set_estado_sesion(juego, ronda_activa, "cerrada")
                            st.session_state["revelar_resultados"] = True
                            st.rerun()
                    else:
                        if st.button(f"🔓 Reabrir Ronda {ronda_activa}", use_container_width=True):
                            set_estado_sesion(juego, ronda_activa, "abierta")
                            st.rerun()
                with b_col2:
                    if ronda_activa < MAX_RONDAS:
                        if st.button(f"➡️ Abrir Ronda {ronda_activa + 1}", type="secondary", use_container_width=True):
                            set_estado_sesion(juego, ronda_activa + 1, "abierta")
                            st.session_state["ronda_proyectada"] = ronda_activa + 1
                            st.session_state["revelar_resultados"] = False
                            st.rerun()
                    else:
                        st.info("🏁 5 rondas completadas")
        
        # Métricas de participación y controles rápidos
        c_status1, c_status2, c_status3, c_status4 = st.columns([1, 1, 1, 1])
        c_status1.metric("👥 Respuestas en ronda proyectada", len(df))
        c_status2.metric("🔄 Ronda proyectada", f"Ronda {ronda} de {MAX_RONDAS}")
        with c_status3:
            st.write("")
            if st.button("🔄 Actualizar", use_container_width=True, help="Refrescar respuestas recibidas"):
                st.rerun()
        with c_status4:
            st.write("")
            with st.popover("🗑️ Reiniciar Juego", use_container_width=True):
                st.markdown("##### Opciones de reinicio")
                st.write(f"Permite a los estudiantes comenzar nuevamente desde la **Ronda 1**.")
                if st.button("🧹 Reiniciar juego activo", use_container_width=True, key="main_reset_juego"):
                    with get_conn() as conn:
                        conn.execute("DELETE FROM respuestas WHERE juego = ?", (juego,))
                    set_estado_sesion(juego, 1, "abierta")
                    st.session_state["revelar_resultados"] = False
                    st.success(f"Respuestas de '{juego}' eliminadas. Ronda 1 abierta.")
                    st.rerun()
                st.divider()
                if st.button("⚠️ Borrar toda la base", use_container_width=True, key="main_reset_todo"):
                    with get_conn() as conn:
                        conn.execute("DELETE FROM respuestas")
                        conn.execute("DELETE FROM estado_sesion")
                    set_estado_sesion(juego, 1, "abierta")
                    st.session_state["revelar_resultados"] = False
                    st.success("Toda la base de datos ha sido borrada.")
                    st.rerun()

        # Recuadros interactivos como botones para elegir la ronda a proyectar
        st.markdown("##### 📌 Selecciona la ronda que deseas proyectar en pantalla:")
        r_cols = st.columns(MAX_RONDAS)
        for r_num in range(1, MAX_RONDAS + 1):
            count_r = df_hist[df_hist["ronda"] == r_num]["participantes"].values
            val = int(count_r[0]) if len(count_r) > 0 else 0
            es_sel = (r_num == ronda)
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
                        st.session_state["revelar_resultados"] = True
                        st.rerun()

        # Código QR permanentemente visible para el proyector
        st.divider()
        with st.container(border=True):
            col_qr1, col_qr2 = st.columns([1, 2])
            with col_qr1:
                st.image(generar_qr(st.session_state["app_url"]), caption="Escanea para unirte a la partida", width=220)
            with col_qr2:
                st.markdown("### 📱 ¡Únete al juego desde tu celular!")
                st.markdown("""
                * Apunta con la **cámara de tu teléfono** al código QR para ingresar directamente a la sala.
                * No necesitas instalar ninguna aplicación.
                """)
                url_editada = st.text_input(
                    "🔗 Enlace web del juego (editable si cambia el dominio o IP):",
                    value=st.session_state["app_url"],
                    key="input_url_qr"
                )
                if url_editada != st.session_state["app_url"]:
                    st.session_state["app_url"] = url_editada
                    st.rerun()
                st.markdown(f"👉 **Enlace directo:** [{st.session_state['app_url']}]({st.session_state['app_url']})")
        st.divider()
                
        revelar_defecto = st.session_state.get("revelar_resultados", estado_sesion == "cerrada")
        revelar = st.toggle("🔓 Revelar resultados y gráficos en pantalla (Proyector)", value=revelar_defecto)
        
        if revelar:
            if df.empty:
                st.warning("Aún no hay respuestas registradas para esta ronda.")
            else:
                st.divider()
                promedio = df["decision"].mean()
                meta = (2 / 3) * promedio
                df["distancia"] = (df["decision"] - meta).abs()
                min_dist = df["distancia"].min()
                ganadores = df[df["distancia"] == min_dist]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Promedio de la clase", f"{promedio:.2f}")
                c2.metric("Meta (2/3 del promedio)", f"{meta:.2f}")
                nombres_ganadores = ", ".join([
                    f"{row['estudiante']} ({row['universidad']}) — {row['decision']:.1f}" 
                    if pd.notna(row.get('universidad')) and row.get('universidad') 
                    else f"{row['estudiante']} ({row['decision']:.1f})" 
                    for _, row in ganadores.iterrows()
                ])
                c3.metric("🏆 Ganador(es)", nombres_ganadores)
                
                fig = px.histogram(
                    df, x="decision", nbins=25,
                    title="Distribución de Elecciones de la Clase",
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
                
                # Explicación pedagógica para la clase
                with st.expander("🧠 Guía de razonamiento estratégico (Niveles k) — Para debate docente", expanded=True):
                    st.markdown(f"""
                    **Resultados de la ronda:** Promedio de la clase = **{promedio:.2f}** | Meta (2/3 del promedio) = **{meta:.2f}**
                    
                    ---
                    ### 🧠 Guía de razonamiento estratégico (Niveles $k$):
                    * **Nivel 0 (Ingenuo / Aleatorio):** Las personas eligen números al azar entre 0 y 100. El promedio esperado sería alrededor de **50**.
                    * **Nivel 1 (Primer orden de deducción):** Si crees que los demás jugarán al azar (promedio 50), deberías jugar: $\\frac{2}{3} \\times 50 \\approx \\mathbf{33.3}$
                    * **Nivel 2 (Segundo orden):** Si piensas que los demás son listos y jugarán 33.3, deberías anticiparte jugando: $\\frac{2}{3} \\times 33.3 \\approx \\mathbf{22.2}$
                    * **Nivel 3:** Si todos hacen lo anterior: $\\frac{2}{3} \\times 22.2 \\approx \\mathbf{14.8}$
                    * **Equilibrio de Nash (Racionalidad común infinita):** Si este proceso se repite infinitas veces, el único número donde nadie tiene incentivos a desviarse es el **0**.

                    > ⚠️ **¡Pero cuidado!** En el mundo real no todos son perfectamente racionales. Si tú juegas 0 pero el resto juega 50, ¡perderás! Tu reto es predecir la profundidad de pensamiento de tus compañeros hoy.
                    """)

                if len(df_hist) > 1:
                    st.subheader("📈 Evolución a lo largo de las rondas (Convergencia hacia Nash)")
                    fig_evol = px.line(
                        df_hist, x="ronda", y="promedio", markers=True,
                        title="Convergencia del Promedio hacia el Equilibrio de Nash",
                        labels={"ronda": "Ronda", "promedio": "Promedio de la decisión"},
                        color_discrete_sequence=["#E96132"]
                    )
                    fig_evol.update_traces(
                        line=dict(color="#E96132", width=3),
                        marker=dict(size=10, color="#18243E", line=dict(width=2, color="#FFFFFF"))
                    )
                    fig_evol.update_layout(
                        plot_bgcolor="#F8FAFC",
                        paper_bgcolor="#FFFFFF",
                        font=dict(family="Segoe UI, sans-serif", color="#18243E")
                    )
                    st.plotly_chart(fig_evol, use_container_width=True)
                    
                with st.expander("📋 Ver tabla completa de registros de la ronda"):
                    df_mostrar = df.copy()
                    col_map = {
                        "estudiante": "Nombre y Apellido",
                        "cedula": "Cédula",
                        "universidad": "Universidad",
                        "decision": "Número Elegido",
                        "distancia": "Distancia a la Meta"
                    }
                    df_mostrar = df_mostrar.rename(columns={k: v for k, v in col_map.items() if k in df_mostrar.columns})
                    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
                    
        st.sidebar.divider()
        st.sidebar.subheader("⚙️ Control de Partida")
        with st.sidebar.popover("🗑️ Reiniciar Partida", use_container_width=True):
            st.caption("Esta acción permitirá a los estudiantes jugar de nuevo desde la Ronda 1.")
            if st.button("🧹 Reiniciar juego activo", use_container_width=True, key="sb_reset_current"):
                with get_conn() as conn:
                    conn.execute("DELETE FROM respuestas WHERE juego = ?", (juego,))
                set_estado_sesion(juego, 1, "abierta")
                st.session_state["revelar_resultados"] = False
                st.success(f"'{juego}' reiniciado con éxito. Ronda 1 abierta.")
                st.rerun()
            if st.button("⚠️ Borrar toda la base de datos", use_container_width=True, key="sb_reset_all"):
                with get_conn() as conn:
                    conn.execute("DELETE FROM respuestas")
                    conn.execute("DELETE FROM estado_sesion")
                set_estado_sesion(juego, 1, "abierta")
                st.session_state["revelar_resultados"] = False
                st.success("Laboratorio reiniciado por completo.")
                st.rerun()
    else:
        if clave:
            st.error("❌ Contraseña incorrecta. Por favor verifica tus credenciales.")
        else:
            st.info("🔒 Ingresa la contraseña docente en la barra lateral izquierda para acceder al panel de control y proyector.")
