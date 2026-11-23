import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(
    page_title="Laboratorio de Teoría de Juegos | EPN",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
                decision REAL,
                UNIQUE(juego, ronda, estudiante)
            )
        """)
init_db()

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/8c/Escudo_de_la_Escuela_Polit%C3%A9cnica_Nacional.png", width=90)
st.sidebar.title("Configuración de Sesión")
rol = st.sidebar.radio("Modo de vista:", ["👨‍🎓 Estudiante", "👨‍🏫 Profesor (Proyector)"])

juego = st.sidebar.selectbox("Juego activo:", [
    "p-Beauty Contest (2/3 del promedio)",
    "Juego de Bienes Públicos"
])
ronda = st.sidebar.number_input("Ronda actual:", min_value=1, max_value=10, value=1, step=1)

# ==============================================================================
# VISTA DEL ESTUDIANTE
# ==============================================================================
if rol == "👨‍🎓 Estudiante":
    st.title(f"🎮 {juego}")
    st.caption(f"Sesión activa — **Ronda {ronda}**")
    
    # --- PESTAÑAS: JUEGO / GUÍA Y EXPLICACIÓN / CALCULADORA DE ESTRATEGIA ---
    tab_jugar, tab_guia, tab_simulador = st.tabs([
        "📝 Realizar mi Jugada",
        "📖 Explicación y Reglas del Juego",
        "💡 Simulador de Estrategia"
    ])
    
    # ------------------ PESTAÑA 2: GUÍA Y EXPLICACIÓN ------------------
    with tab_guia:
        if "Beauty" in juego:
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
            ### 🧠 Guía de razonamiento estratégico (Niveles $k$):
            * **Nivel 0 (Ingenuo / Aleatorio):** Las personas eligen números al azar entre 0 y 100. El promedio esperado sería alrededor de **50**.
            * **Nivel 1 (Primer orden de deducción):** Si crees que los demás jugarán al azar (promedio 50), deberías jugar:
              $$\\frac{2}{3} \\times 50 \\approx \\mathbf{33.3}$$
            * **Nivel 2 (Segundo orden):** Si piensas que los demás son listos y jugarán 33.3, deberías anticiparte jugando:
              $$\\frac{2}{3} \\times 33.3 \\approx \\mathbf{22.2}$$
            * **Nivel 3:** Si todos hacen lo anterior:
              $$\\frac{2}{3} \\times 22.2 \\approx \\mathbf{14.8}$$
            * **Equilibrio de Nash (Racionalidad común infinita):** Si este proceso se repite infinitas veces, el único número donde nadie tiene incentivos a desviarse es el **0**. 
            
            ⚠️ **¡Pero cuidado!** En el mundo real no todos son perfectamente racionales. Si tú juegas 0 pero el resto juega 50, ¡perderás! Tu reto es **predecir la profundidad de pensamiento de tus compañeros hoy**.
            """)
        else:
            st.header("🤝 Dilema de los Bienes Públicos (Dilema del Polizón)")
            st.markdown("""
            ### 📌 ¿En qué consiste el juego?
            Representa una economía con provisión de un bien común (alumbrado público, investigación, trabajo en equipo, parques).
            
            * Cada estudiante recibe una dotación inicial de **\\$20**.
            * Tú decides voluntariamente cuánto dinero aportar ($c_i$) al **fondo común** (entre \\$0 y \\$20).
            * Lo que no aportes ($20 - c_i$), te lo quedas en tu bolsillo privado.
            
            ### 📈 Multiplicador y distribución:
            1. Todas las aportaciones de la clase se suman en un pozo común.
            2. El pozo se multiplica por un factor social de beneficio: **1.6x** (+60% de rendimiento por cooperación).
            3. El pozo multiplicado se reparte **en partes estrictamente iguales** entre todos los participantes de la clase, **hayan aportado o no**.
            
            $$\\text{Tu Pago Final} = (20 - c_i) + \\frac{1.6 \\times \\sum c_j}{N}$$
            
            ---
            ### ⚖️ El dilema estratégico: ¿Cooperar o ser un "Free Rider" (Polizón)?
            * **El Óptimo Social (Cooperación total):** Si **todos** aportan sus \\$20, cada uno terminará con **\\$32** (ganancia neta de +\\$12 para todos).
            * **La Tentación Individual (El Polizón):** Por cada \\$1 que tú aportas al fondo, recibes de vuelta solo $\\frac{1.6}{N}$ dólares (si hay más de 2 jugadores, esto es menor a \\$1). En cambio, si tú guardas tus \\$20 y los demás aportan, tú te beneficias del fondo de los demás ¡sin haber gastado nada!
            * **Equilibrio de Nash:** Si cada individuo piensa estrictamente de forma egoísta para maximizar su pago seguro en una ronda, la estrategia dominante individual es aportar **\\$0**. Pero si todos aportan \\$0, todos terminan con solo **\\$20** (el peor resultado colectivo posible).
            """)
    
    # ------------------ PESTAÑA 3: SIMULADOR DE ESTRATEGIA ------------------
    with tab_simulador:
        if "Beauty" in juego:
            st.subheader("💡 Simulador para el Concurso de Belleza")
            st.write("Prueba qué número deberías jugar según lo que proyectas que hará el grupo:")
            
            est_promedio = st.slider("¿Cuál crees que será el promedio de la clase?", min_value=0.0, max_value=100.0, value=45.0, step=1.0)
            meta_calculada = (2 / 3) * est_promedio
            
            st.info(f"👉 Si el promedio resulta ser **{est_promedio:.1f}**, la meta exacta ganadora será: **{meta_calculada:.2f}**")
            st.caption("Pista: Recuerda ajustar tu número según cuántos niveles de deducción creas que aplicarán tus compañeros en esta ronda.")
        else:
            st.subheader("💡 Simulador de Pagos (Bienes Públicos)")
            st.write("Calcula tu ganancia esperada bajo diferentes escenarios hipotéticos:")
            
            col_sim1, col_sim2, col_sim3 = st.columns(3)
            with col_sim1:
                tam_clase = st.number_input("Número estimado de jugadores (N):", min_value=2, max_value=100, value=20, step=1)
            with col_sim2:
                mi_aporte_sim = st.slider("Tu aporte hipotético ($):", 0.0, 20.0, 10.0, 1.0)
            with col_sim3:
                aporte_medio_demas = st.slider("Aporte promedio de los demás ($):", 0.0, 20.0, 10.0, 1.0)
            
            pozo_total_sim = mi_aporte_sim + (aporte_medio_demas * (tam_clase - 1))
            retorno_individual_sim = (pozo_total_sim * 1.6) / tam_clase
            pago_total_estudiante = (20 - mi_aporte_sim) + retorno_individual_sim
            
            c_res1, c_res2, c_res3 = st.columns(3)
            c_res1.metric("Pozo social multiplicado", f"${pozo_total_sim * 1.6:.2f}")
            c_res2.metric("Retorno del fondo público", f"${retorno_individual_sim:.2f}")
            c_res3.metric("Tu ganancia total estimada", f"${pago_total_estudiante:.2f}")
    
    # ------------------ PESTAÑA 1: FORMULARIO DE JUGADA ------------------
    with tab_jugar:
        st.subheader("Paso a paso para enviar tu decisión:")
        
        with st.form("form_jugada"):
            col_id1, col_id2 = st.columns([2, 1])
            with col_id1:
                nombre = st.text_input("1. Tu nombre completo o código de estudiante:", placeholder="Ej: Juan Pérez / 20261001")
            with col_id2:
                st.info(f"Ronda: **{ronda}**")
            
            st.divider()
            
            if "Beauty" in juego:
                st.markdown("#### 2. Selecciona tu número estratégico")
                st.write("Debes escoger un valor entre **0 y 100**. Ganará quien esté más cerca de **2/3 del promedio** de toda la clase.")
                decision = st.number_input(
                    "Tu número seleccionado (0.0 a 100.0):",
                    min_value=0.0,
                    max_value=100.0,
                    value=33.3,
                    step=0.1,
                    help="Ingresa el valor que crees que igualará 2/3 del promedio de todos."
                )
            else:
                st.markdown("#### 2. Decide tu contribución al Bien Público")
                st.write("Tienes una dotación inicial de **$20**. ¿Cuánto deseas aportar al fondo común?")
                decision = st.slider(
                    "Tu aporte ($):",
                    min_value=0.0,
                    max_value=20.0,
                    value=10.0,
                    step=1.0,
                    help="Lo que no aportes queda en tu cuenta privada ($20 - tu aporte)."
                )
                st.caption(f"Te quedas con **${20 - decision:.2f}** seguros y aportas **${decision:.2f}** al beneficio común.")
                
            st.divider()
            enviado = st.form_submit_button("🚀 Confirmar y Enviar Decisión", use_container_width=True)
            
            if enviado:
                if not nombre.strip():
                    st.error("⚠️ Por favor ingresa tu nombre o código antes de enviar.")
                else:
                    try:
                        with get_conn() as conn:
                            conn.execute(
                                "INSERT INTO respuestas (juego, ronda, estudiante, decision) VALUES (?, ?, ?, ?)",
                                (juego, ronda, nombre.strip(), float(decision))
                            )
                        st.success(f"✅ ¡Jugada registrada con éxito para **{nombre.strip()}** en la Ronda {ronda}!")
                        st.balloons()
                    except sqlite3.IntegrityError:
                        st.warning(f"⚠️ Ya existe una jugada registrada con el nombre '{nombre.strip()}' para la Ronda {ronda}. Espera a la siguiente ronda o usa tu código único correcto.")

# ==============================================================================
# VISTA DEL PROFESOR (PROYECTOR)
# ==============================================================================
else:
    st.title(f"📊 Panel de Control del Profesor: {juego}")
    st.caption(f"Visualización central para proyector — **Ronda {ronda}**")
    
    # Obtener contraseña desde secrets si existe, o usar predeterminada
    docente_password = st.secrets.get("DOCENTE_PASSWORD", "epn2026")
    clave = st.sidebar.text_input("Contraseña docente:", type="password")
    
    if clave == docente_password:
        with get_conn() as conn:
            df = pd.read_sql_query(
                "SELECT estudiante, decision FROM respuestas WHERE juego = ? AND ronda = ?",
                conn, params=(juego, ronda)
            )
            df_hist = pd.read_sql_query(
                "SELECT ronda, AVG(decision) as promedio, COUNT(estudiante) as participantes FROM respuestas WHERE juego = ? GROUP BY ronda ORDER BY ronda",
                conn, params=(juego,)
            )
        
        # Métricas de participación
        c_status1, c_status2, c_status3 = st.columns([1, 1, 1])
        c_status1.metric("👥 Respuestas recibidas (Ronda actual)", len(df))
        c_status2.metric("🔄 Ronda activa", f"Ronda {ronda}")
        with c_status3:
            if st.button("🔄 Actualizar datos de estudiantes", use_container_width=True):
                st.rerun()
                
        revelar = st.toggle("🔓 Revelar resultados y gráficos en pantalla (Proyector)", value=False)
        
        if revelar:
            if df.empty:
                st.warning("Aún no hay respuestas registradas para esta ronda.")
            else:
                st.divider()
                if "Beauty" in juego:
                    promedio = df["decision"].mean()
                    meta = (2 / 3) * promedio
                    df["distancia"] = (df["decision"] - meta).abs()
                    min_dist = df["distancia"].min()
                    ganadores = df[df["distancia"] == min_dist]
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Promedio de la clase", f"{promedio:.2f}")
                    c2.metric("Meta (2/3 del promedio)", f"{meta:.2f}")
                    nombres_ganadores = ", ".join([f"{row['estudiante']} ({row['decision']:.1f})" for _, row in ganadores.iterrows()])
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
                    with st.expander("🎓 Análisis pedagógico para la clase: Niveles de Razonamiento"):
                        st.markdown(f"""
                        * **Media observada:** {promedio:.2f} | **Meta ganadora:** {meta:.2f}
                        * **Picos típicos en la literatura (Nagel, 1995):**
                          - Alrededor de **50**: Jugadores de nivel 0 (elección intuitiva/aleatoria).
                          - Alrededor de **33.3**: Jugadores de nivel 1 (anticiparon un promedio de 50).
                          - Alrededor de **22.2**: Jugadores de nivel 2 (anticiparon que los demás jugarían 33.3).
                          - Cerca de **0**: Jugadores con razonamiento deductivo infinito (Equilibrio de Nash estricto).
                        * A medida que se juegan más rondas, se suele observar el fenómeno de **aprendizaje y convergencia hacia cero**.
                        """)
                    
                else:
                    n = len(df)
                    fondo_total = df["decision"].sum() * 1.6
                    retorno_individual = fondo_total / n
                    df["pago_final"] = (20 - df["decision"]) + retorno_individual
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Aporte promedio", f"${df['decision'].mean():.2f} / $20")
                    c2.metric("Fondo común multiplicado (1.6x)", f"${fondo_total:.2f}")
                    c3.metric("Pago promedio final por estudiante", f"${df['pago_final'].mean():.2f}")
                    
                    fig = px.bar(
                        df.sort_values("pago_final", ascending=False),
                        x="estudiante", y=["decision", "pago_final"],
                        barmode="group",
                        title="Comparación: Aporte individual vs. Pago Final obtenido",
                        labels={"value": "Dólares ($)", "variable": "Concepto", "estudiante": "Estudiante"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("🎓 Análisis pedagógico: El Dilema del Polizón (Free-Rider)"):
                        st.markdown("""
                        * Aquellos estudiantes con **menor aporte** y **mayor pago final** explotaron con éxito la estrategia de *Free-Rider* (polizón).
                        * El grupo en su conjunto maximiza ganancias cuando la cooperación es del 100% (todos aportan $20 y obtienen $32).
                        * En experimentos repetidos sin castigo, la cooperación tiende a decaer ronda tras ronda porque los cooperadores se sienten explotados por los polizones.
                        """)
                    
                if len(df_hist) > 1:
                    st.subheader("📈 Evolución a lo largo de las rondas")
                    fig_evol = px.line(
                        df_hist, x="ronda", y="promedio", markers=True,
                        title="Evolución del Promedio por Ronda (Dinámica de Aprendizaje)",
                        labels={"ronda": "Ronda", "promedio": "Promedio de la decisión"}
                    )
                    st.plotly_chart(fig_evol, use_container_width=True)
                    
                with st.expander("📋 Ver tabla completa de registros de la ronda"):
                    st.dataframe(df, use_container_width=True)
                    
        st.sidebar.divider()
        if st.sidebar.button("🗑️ Borrar todos los datos de la base"):
            with get_conn() as conn:
                conn.execute("DELETE FROM respuestas")
            st.sidebar.success("Base de datos reiniciada con éxito.")
            st.rerun()
    else:
        if clave:
            st.error("❌ Contraseña incorrecta. Por favor verifica tus credenciales.")
        else:
            st.info("🔒 Ingresa la contraseña docente en la barra lateral izquierda para acceder al panel de control y proyector.")
