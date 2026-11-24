import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import io
import urllib.parse

st.set_page_config(
    page_title="Laboratorio de Teoría de Juegos | EPN",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

MAX_RONDAS = 5
DEFAULT_APP_URL = st.secrets.get("APP_URL", "https://juego-keynes.streamlit.app")

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

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/8c/Escudo_de_la_Escuela_Polit%C3%A9cnica_Nacional.png", width=90)
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
    st.title("🎯 Concurso de Belleza de Keynes")
    st.caption(f"Experimento de Teoría de Juegos (2/3 del promedio) — **Máximo {MAX_RONDAS} rondas**")
    
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
                        "Universidad San Francisco de Quito"
                    ]
                )
                btn_registro = st.form_submit_button("✅ Guardar y Comenzar a Jugar", use_container_width=True)
                
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

            ronda_activa, estado_sesion = get_estado_sesion(juego)

            with get_conn() as conn:
                res = conn.execute(
                    "SELECT ronda, decision FROM respuestas WHERE juego = ? AND cedula = ? ORDER BY ronda ASC",
                    (juego, cedula)
                ).fetchall()
                jugada_actual = conn.execute(
                    "SELECT decision FROM respuestas WHERE juego = ? AND ronda = ? AND cedula = ?",
                    (juego, ronda_activa, cedula)
                ).fetchone()
            
            rondas_jugadas = [r[0] for r in res]
            
            # Caso 1: Ha completado todas las rondas o el profesor finalizó el juego
            if len(rondas_jugadas) >= MAX_RONDAS or ronda_activa > MAX_RONDAS:
                st.success(f"🎉 **¡Excelente, {estudiante}! Has completado las {MAX_RONDAS} rondas del juego.**")
                st.progress(1.0)
                st.info("Has alcanzado el límite de 5 rondas. Presta atención al proyector para ver el análisis de resultados.")
                
                df_resumen = pd.DataFrame(res, columns=["Ronda", "Tu Decisión"])
                st.subheader("📋 Resumen de tus decisiones:")
                st.dataframe(df_resumen, use_container_width=True, hide_index=True)
            
            # Caso 2: Ya envió la respuesta para la ronda activa
            elif jugada_actual is not None:
                st.markdown(f"### 📍 Ronda **{ronda_activa}** de **{MAX_RONDAS}**")
                st.progress(ronda_activa / MAX_RONDAS)
                st.success(f"✅ ¡Tu jugada para la **Ronda {ronda_activa}** ya fue registrada! (Tu decisión: **{jugada_actual[0]:.1f}**)")
                st.info("👀 **Presta atención al proyector de la clase:** El profesor proyectará los resultados, el promedio y la meta ganadora de esta ronda.")
                st.caption("Cuando el profesor abra la siguiente ronda, tu pantalla se habilitará automáticamente.")
                if st.button("🔄 Comprobar si ya inició la siguiente ronda", use_container_width=True):
                    st.rerun()

            # Caso 3: La ronda activa está cerrada por el profesor
            elif estado_sesion == "cerrada":
                st.markdown(f"### 📍 Ronda **{ronda_activa}** de **{MAX_RONDAS}**")
                st.warning(f"🔒 La **Ronda {ronda_activa}** está cerrada temporalmente para nuevas respuestas.")
                st.info("👀 Observa el proyector de la clase para ver el debate y los resultados. Espera a que el docente habilite la siguiente ronda.")
                if st.button("🔄 Comprobar si ya abrió la siguiente ronda", use_container_width=True):
                    st.rerun()

            # Caso 4: Ronda activa abierta y el alumno aún no ha jugado
            else:
                st.markdown(f"### 📍 Ronda **{ronda_activa}** de **{MAX_RONDAS}**")
                st.progress((ronda_activa - 1) / MAX_RONDAS)
                
                with st.form(f"form_jugada_{ronda_activa}"):
                    st.markdown("#### Selecciona tu número estratégico (0.0 - 100.0)")
                    st.write("Debes escoger un valor entre **0 y 100**. Ganará quien esté más cerca de **2/3 del promedio** de toda la clase.")
                    decision = st.number_input(
                        f"Tu número para la Ronda {ronda_activa}:",
                        min_value=0.0,
                        max_value=100.0,
                        value=33.3,
                        step=0.1,
                        help="Ingresa el valor que crees que igualará 2/3 del promedio de todos."
                    )
                    
                    st.divider()
                    texto_boton = f"🚀 Confirmar y Enviar Ronda {ronda_activa}" if ronda_activa < MAX_RONDAS else "🏁 Confirmar y Finalizar Ronda 5"
                    enviado = st.form_submit_button(texto_boton, use_container_width=True)
                    
                    if enviado:
                        try:
                            with get_conn() as conn:
                                conn.execute(
                                    "INSERT INTO respuestas (juego, ronda, estudiante, cedula, universidad, decision) VALUES (?, ?, ?, ?, ?, ?)",
                                    (juego, ronda_activa, estudiante, cedula, universidad, float(decision))
                                )
                            st.success(f"✅ ¡Jugada de la Ronda {ronda_activa} enviada!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.warning(f"Ya se había registrado una respuesta para la Ronda {ronda_activa} con tu cédula.")

# ==============================================================================
# VISTA DEL PROFESOR (PROYECTOR)
# ==============================================================================
else:
    ronda_activa_global, estado_sesion_global = get_estado_sesion(juego)
    ronda = st.sidebar.number_input(
        "Ronda a proyectar:",
        min_value=1,
        max_value=MAX_RONDAS,
        value=min(ronda_activa_global, MAX_RONDAS),
        step=1,
        help="Selecciona qué ronda deseas proyectar en pantalla."
    )
    
    st.title(f"📊 Panel de Control del Profesor: {juego}")
    st.caption(f"Visualización central para proyector — **Ronda {ronda} de {MAX_RONDAS}**")
    
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

        # Resumen de participación en las 5 rondas
        r_cols = st.columns(MAX_RONDAS)
        for r_num in range(1, MAX_RONDAS + 1):
            count_r = df_hist[df_hist["ronda"] == r_num]["participantes"].values
            val = int(count_r[0]) if len(count_r) > 0 else 0
            r_cols[r_num - 1].metric(f"Ronda {r_num}", f"{val} alumnos")

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
                    color_discrete_sequence=["#1f77b4"]
                )
                fig.add_vline(x=promedio, line_dash="dash", line_color="blue", annotation_text=f"Promedio ({promedio:.1f})")
                fig.add_vline(x=meta, line_dash="solid", line_color="red", annotation_text=f"Meta 2/3 ({meta:.1f})")
                fig.update_layout(xaxis=dict(range=[0, 100]))
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
                        labels={"ronda": "Ronda", "promedio": "Promedio de la decisión"}
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
