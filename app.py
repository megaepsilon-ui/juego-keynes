import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Laboratorio de Teoría de Juegos", layout="wide")

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
st.sidebar.title("Configuración de Sesión")
rol = st.sidebar.radio("Modo de vista:", ["Estudiante", "Profesor (Proyector)"])
juego = st.sidebar.selectbox("Juego activo:", [
    "p-Beauty Contest (2/3 del promedio)",
    "Juego de Bienes Públicos"
])
ronda = st.sidebar.number_input("Ronda actual:", min_value=1, max_value=10, value=1)

# --- VISTA DEL ESTUDIANTE ---
if rol == "Estudiante":
    st.title(f"🎮 {juego} — Ronda {ronda}")
    
    with st.form("form_jugada"):
        nombre = st.text_input("Tu nombre o código único:")
        
        if "Beauty" in juego:
            st.markdown("Elige un número entre **0 y 100**. Gana quien se acerque más a **2/3 del promedio** de toda la clase.")
            decision = st.number_input("Tu número (0 - 100):", min_value=0.0, max_value=100.0, value=50.0, step=0.5)
        else:
            st.markdown("Tienes una dotación de **$20**. Decide cuánto aportar al fondo común (se multiplica por **1.6** y se reparte en partes iguales entre todos).")
            decision = st.slider("Tu aporte al bien público ($):", min_value=0.0, max_value=20.0, value=10.0, step=1.0)
            
        enviado = st.form_submit_button("Enviar decisión")
        
        if enviado:
            if not nombre.strip():
                st.error("Por favor ingresa tu nombre o código.")
            else:
                try:
                    with get_conn() as conn:
                        conn.execute(
                            "INSERT INTO respuestas (juego, ronda, estudiante, decision) VALUES (?, ?, ?, ?)",
                            (juego, ronda, nombre.strip(), decision)
                        )
                    st.success(f"¡Jugada registrada para {nombre} en la Ronda {ronda}!")
                except sqlite3.IntegrityError:
                    st.warning("Ya enviaste una respuesta en esta ronda con ese nombre.")

# --- VISTA DEL PROFESOR ---
else:
    st.title(f"📊 Panel del Profesor: {juego} (Ronda {ronda})")
    clave = st.sidebar.text_input("Contraseña docente:", type="password")
    
    if clave == "epn2026":  # Cambia tu contraseña aquí
        with get_conn() as conn:
            df = pd.read_sql_query(
                "SELECT estudiante, decision FROM respuestas WHERE juego = ? AND ronda = ?",
                conn, params=(juego, ronda)
            )
            df_hist = pd.read_sql_query(
                "SELECT ronda, AVG(decision) as promedio FROM respuestas WHERE juego = ? GROUP BY ronda",
                conn, params=(juego,)
            )
        
        col1, col2 = st.columns([1, 2])
        col1.metric("Respuestas recibidas", len(df))
        if col1.button("🔄 Actualizar conteo"):
            st.rerun()
            
        revelar = st.checkbox("🔓 Revelar resultados y gráficos en pantalla")
        
        if revelar and not df.empty:
            if "Beauty" in juego:
                promedio = df["decision"].mean()
                meta = (2 / 3) * promedio
                df["distancia"] = (df["decision"] - meta).abs()
                ganador = df.loc[df["distancia"].idxmin()]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Promedio de la clase", f"{promedio:.2f}")
                c2.metric("Meta (2/3 del promedio)", f"{meta:.2f}")
                c3.metric("Ganador(a)", f"{ganador['estudiante']} ({ganador['decision']:.1f})")
                
                fig = px.histogram(df, x="decision", nbins=20, title="Distribución de decisiones")
                fig.add_vline(x=promedio, line_dash="dash", line_color="blue", annotation_text="Promedio")
                fig.add_vline(x=meta, line_dash="solid", line_color="red", annotation_text="2/3 Promedio (Meta)")
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                n = len(df)
                fondo_total = df["decision"].sum() * 1.6
                retorno_individual = fondo_total / n
                df["pago_final"] = (20 - df["decision"]) + retorno_individual
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Aporte promedio", f"${df['decision'].mean():.2f} / $20")
                c2.metric("Fondo común multiplicado", f"${fondo_total:.2f}")
                c3.metric("Pago promedio final", f"${df['pago_final'].mean():.2f}")
                
                fig = px.bar(df.sort_values("pago_final", ascending=False), 
                             x="estudiante", y=["decision", "pago_final"], 
                             barmode="group", title="Aportes vs. Pago Final (Incentivo al Free-Rider)")
                st.plotly_chart(fig, use_container_width=True)
                
            if len(df_hist) > 1:
                fig_evol = px.line(df_hist, x="ronda", y="promedio", markers=True, 
                                   title="Convergencia hacia el Equilibrio de Nash por Ronda")
                st.plotly_chart(fig_evol, use_container_width=True)
                
            st.dataframe(df, use_container_width=True)
            
        if st.sidebar.button("🗑️ Borrar todos los datos"):
            with get_conn() as conn:
                conn.execute("DELETE FROM respuestas")
            st.sidebar.success("Base de datos reiniciada.")
            st.rerun()
    else:
        st.info("Ingresa la contraseña docente en la barra lateral para controlar el experimento.")