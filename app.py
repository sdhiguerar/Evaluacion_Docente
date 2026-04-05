import streamlit as st
import pandas as pd
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
 
# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
 
st.set_page_config(page_title="Sistema de Evaluación de Talleres", page_icon="📘", layout="centered")
 
DOCENTE_USER = "sebastian"
DOCENTE_PASS = "curso2026"
CSV_FILE     = "historial_evaluaciones.csv"
 
RUBRICAS = {
    "Organización y Presentación (20%)": {
        "peso": 20,
        "comentarios": {
            5: "Trabajo completamente ordenado, limpio y fácil de seguir. Los ejercicios están bien identificados.",
            4: "Buen orden general, con pequeños detalles de presentación.",
            3: "Presenta cierto desorden o falta de claridad en algunas partes.",
            2: "Desorganizado y difícil de seguir.",
            1: "Muy desordenado, ilegible o incompleto.",
        },
    },
    "Desarrollo y Procedimiento (30%)": {
        "peso": 30,
        "comentarios": {
            5: "Muestra todos los pasos correctamente y de forma clara.",
            4: "Presenta la mayoría de los pasos con pequeños errores u omisiones.",
            3: "Faltan varios pasos importantes o hay poca explicación.",
            2: "Procedimiento incompleto o con errores graves.",
            1: "No muestra procedimiento o es totalmente incorrecto.",
        },
    },
    "Exactitud de Resultados (30%)": {
        "peso": 30,
        "comentarios": {
            5: "Todos los resultados son correctos.",
            4: "Uno o dos errores menores de cálculo.",
            3: "Varios errores, pero se evidencia intento correcto.",
            2: "Muchos errores de cálculo o concepto.",
            1: "Resultados mayormente incorrectos o no responde.",
        },
    },
    "Comprensión del Tema (20%)": {
        "peso": 20,
        "comentarios": {
            5: "Demuestra dominio claro de los conceptos.",
            4: "Buena comprensión general con pequeñas confusiones.",
            3: "Comprensión básica, con errores conceptuales leves.",
            2: "Dificultad notable para aplicar los conceptos.",
            1: "No demuestra comprensión del tema.",
        },
    },
}
 
NIVELES = {5: "Excelente", 4: "Bueno", 3: "Aceptable", 2: "Insuficiente", 1: "Deficiente"}
 
# ══════════════════════════════════════════════════════════════
#  ESTILOS
# ══════════════════════════════════════════════════════════════
 
st.markdown("""
<style>
    .stApp { background-color: #F0EAF8; }
    section.main > div { background-color: #F0EAF8; }
    h1, h2, h3, h4, h5, h6 { color: #2D1B69 !important; font-weight: 700; }
    p, label, div, span { color: #3B2A6E; }
    input[type="text"], input[type="password"], input[type="number"], textarea, select {
        background-color: #FFFFFF !important;
        color: #2D1B69 !important;
        border: 1.5px solid #C3A9E8 !important;
        border-radius: 10px !important;
    }
    input::placeholder, textarea::placeholder { color: #A08BBF !important; }
    .stButton > button[kind="primary"] {
        background-color: #7C4DCC !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
    }
    .stButton > button[kind="primary"]:hover { background-color: #6A3DB8 !important; }
    .stButton > button:disabled { background-color: #C9B8E8 !important; color: #FFFFFF !important; }
    .card {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        border: 1px solid #D8C6F0;
    }
    .login-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 2rem 2rem 1.5rem;
        border: 1px solid #D8C6F0;
        max-width: 400px;
        margin: 3rem auto 0;
    }
    .resultado-card {
        background: #EDE4FA;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        border: 1px solid #C3A9E8;
        margin-top: 1rem;
    }
    .nota-grande { font-size: 48px; font-weight: 700; color: #2D1B69; text-align: center; }
    .nota-label  { font-size: 14px; color: #6B5A90; text-align: center; margin-top: -10px; }
    [data-testid="stAlert"] {
        background-color: #EDE4FA !important;
        border: 1px solid #C3A9E8 !important;
        border-radius: 12px !important;
        color: #2D1B69 !important;
    }
    [data-testid="stMetric"] { background-color: #EDE4FA; border-radius: 12px; padding: 10px; }
    [data-testid="stMetricValue"] { color: #2D1B69 !important; }
    .danger-btn > button {
        background-color: #F5E4E4 !important;
        color: #A32D2D !important;
        border: 1px solid #F0A0A0 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    hr { border-color: #D8C6F0; }
    .stCaption { color: #6B5A90 !important; }
</style>
""", unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
 
def calcular_nota(valores: dict) -> float:
    suma = sum((v / 5) * RUBRICAS[r]["peso"] for r, v in valores.items())
    return round((suma / 100) * 5, 2)
 
def guardar_registros(filas: list):
    df_nuevo = pd.DataFrame(filas)
    if os.path.exists(CSV_FILE):
        df_nuevo.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df_nuevo.to_csv(CSV_FILE, index=False)
 
def cargar_registros() -> pd.DataFrame:
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, dtype={"Documento": str})
    return pd.DataFrame()
 
def generar_pdf(asignatura, trabajo, fecha, estudiantes_data, valores, nota_final) -> str:
    filename = f"Evaluacion_{trabajo.replace(' ', '_')}_{fecha.replace('/', '-')}.pdf"
    estilos  = getSampleStyleSheet()
    normal   = estilos["Normal"]
    doc      = SimpleDocTemplate(filename, pagesize=pagesizes.letter)
    elems    = []
 
    elems.append(Paragraph("<b>Evaluación de Taller</b>", estilos["Title"]))
    elems.append(Spacer(1, 12))
    elems.append(Paragraph(f"<b>Asignatura:</b> {asignatura}", normal))
    elems.append(Paragraph(f"<b>Trabajo / Taller:</b> {trabajo}", normal))
    elems.append(Paragraph(f"<b>Fecha:</b> {fecha}", normal))
    elems.append(Spacer(1, 12))
 
    elems.append(Paragraph("<b>Estudiantes evaluados:</b>", normal))
    for est in estudiantes_data:
        elems.append(Paragraph(f"- {est['nombre']} (Doc: {est['documento']})", normal))
    elems.append(Spacer(1, 12))
 
    elems.append(Paragraph("<b>Rúbricas aplicadas:</b>", normal))
    elems.append(Spacer(1, 6))
    for rubrica, valor in valores.items():
        comentario = RUBRICAS[rubrica]["comentarios"][valor]
        elems.append(Paragraph(f"<b>{rubrica}</b>", normal))
        elems.append(Paragraph(f"Nivel: {valor} – {NIVELES[valor]}", normal))
        elems.append(Paragraph(f"Comentario: {comentario}", normal))
        elems.append(Spacer(1, 8))
 
    elems.append(Paragraph(f"<b>Nota Final: {nota_final}</b>", estilos["Heading2"]))
    doc.build(elems)
    return filename
 
# ══════════════════════════════════════════════════════════════
#  ESTADO DE SESIÓN
# ══════════════════════════════════════════════════════════════
 
for k, v in [("docente_auth", False), ("vista", "evaluar"), ("confirmar_eliminar", False)]:
    if k not in st.session_state:
        st.session_state[k] = v
 
# ══════════════════════════════════════════════════════════════
#  BARRA LATERAL
# ══════════════════════════════════════════════════════════════
 
with st.sidebar:
    st.markdown("### Navegación")
    if st.button("📝  Registrar evaluación", use_container_width=True):
        st.session_state.vista = "evaluar"
        st.rerun()
    if st.button("🔍  Consultar mi calificación", use_container_width=True):
        st.session_state.vista = "consulta"
        st.rerun()
    if st.button("🔒  Panel docente", use_container_width=True):
        st.session_state.vista = "login" if not st.session_state.docente_auth else "panel"
        st.rerun()
    if st.session_state.docente_auth:
        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.docente_auth = False
            st.session_state.vista = "evaluar"
            st.rerun()
 
# ══════════════════════════════════════════════════════════════
#  VISTA: REGISTRAR EVALUACIÓN
# ══════════════════════════════════════════════════════════════
 
if st.session_state.vista == "evaluar":
    st.title("📘 Evaluación de Talleres")
    st.caption("Completa la información del taller y califica cada rúbrica.")
    st.divider()
 
    asignatura = st.text_input("Asignatura", placeholder="Ej: Matemáticas")
    trabajo    = st.text_input("Trabajo / Taller", placeholder="Ej: Taller 1 – Álgebra")
 
    st.divider()
    st.markdown("#### Estudiantes")
    cantidad = st.number_input("Número de estudiantes", min_value=1, max_value=20, value=1)
 
    estudiantes_data = []
    for i in range(int(cantidad)):
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input(f"Nombre estudiante {i+1}", key=f"nombre_{i}", placeholder="Nombre completo")
        with col2:
            documento = st.text_input(f"Número de documento {i+1}", key=f"doc_{i}", placeholder="Ej: 1234567890")
        st.markdown('</div>', unsafe_allow_html=True)
        if nombre and documento:
            estudiantes_data.append({"nombre": nombre.strip(), "documento": documento.strip()})
 
    st.divider()
    st.markdown("#### Rúbricas de evaluación")
    st.caption("Las mismas rúbricas aplican para todos los estudiantes del grupo.")
 
    valores = {}
    for rubrica, info in RUBRICAS.items():
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f"**{rubrica}**")
        val = st.selectbox(
            rubrica,
            options=[5, 4, 3, 2, 1],
            format_func=lambda x: f"{x} – {NIVELES[x]}",
            key=f"rubrica_{rubrica}",
            label_visibility="collapsed",
        )
        st.caption(info["comentarios"][val])
        valores[rubrica] = val
        st.markdown('</div>', unsafe_allow_html=True)
 
    st.divider()
 
    nota_preview = calcular_nota(valores)
    st.metric("Nota calculada (vista previa)", f"{nota_preview:.2f} / 5.00")
 
    st.write("")
    listo = asignatura and trabajo and len(estudiantes_data) == int(cantidad)
 
    if st.button("Guardar evaluación", type="primary", disabled=not listo, use_container_width=True):
        fecha   = datetime.now().strftime("%d/%m/%Y")
        nota    = calcular_nota(valores)
        filas   = []
 
        for est in estudiantes_data:
            fila = {
                "Fecha":      fecha,
                "Asignatura": asignatura.strip(),
                "Taller":     trabajo.strip(),
                "Nombre":     est["nombre"],
                "Documento":  est["documento"],
            }
            for rubrica, val in valores.items():
                fila[rubrica] = f"{val} – {NIVELES[val]}"
            fila["Nota Final"] = nota
            filas.append(fila)
 
        guardar_registros(filas)
 
        # Generar PDF
        pdf_file = generar_pdf(asignatura, trabajo, fecha, estudiantes_data, valores, nota)
 
        st.success(f"¡Evaluación guardada! Nota Final: **{nota:.2f}**")
        st.balloons()
 
        with open(pdf_file, "rb") as f:
            st.download_button(
                "⬇️  Descargar PDF de la evaluación",
                f, file_name=pdf_file,
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
 
# ══════════════════════════════════════════════════════════════
#  VISTA: CONSULTA ESTUDIANTE
# ══════════════════════════════════════════════════════════════
 
elif st.session_state.vista == "consulta":
    st.title("🔍 Consulta de calificación")
    st.caption("Ingresa tu número de documento para ver tu calificación.")
    st.divider()
 
    documento = st.text_input("Número de documento", placeholder="Ej: 1234567890")
 
    if st.button("Buscar", type="primary", use_container_width=True):
        df = cargar_registros()
        if df.empty:
            st.warning("Aún no hay calificaciones registradas.")
        else:
            resultados = df[df["Documento"].astype(str) == documento.strip()]
            if resultados.empty:
                st.error("No se encontró ninguna calificación con ese número de documento.")
            else:
                st.success(f"Se encontraron {len(resultados)} registro(s) para tu documento.")
                for _, fila in resultados.iterrows():
                    st.markdown('<div class="resultado-card">', unsafe_allow_html=True)
                    st.markdown(f"**Estudiante:** {fila['Nombre']}")
                    st.markdown(f"**Asignatura:** {fila['Asignatura']}  |  **Taller:** {fila['Taller']}  |  **Fecha:** {fila['Fecha']}")
                    st.divider()
                    for rubrica in RUBRICAS:
                        if rubrica in fila:
                            st.markdown(f"- {rubrica}: **{fila[rubrica]}**")
                    st.markdown(f'<p class="nota-grande">{fila["Nota Final"]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="nota-label">Nota Final / 5.00</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.write("")
 
# ══════════════════════════════════════════════════════════════
#  VISTA: LOGIN DOCENTE
# ══════════════════════════════════════════════════════════════
 
elif st.session_state.vista == "login":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("### 🔒 Acceso docente")
    st.caption("Ingresa tus credenciales para ver el historial de evaluaciones.")
    st.write("")
    usuario    = st.text_input("Usuario", placeholder="Usuario")
    contrasena = st.text_input("Contraseña", type="password", placeholder="Contraseña")
    st.write("")
    if st.button("Ingresar", type="primary", use_container_width=True):
        if usuario == DOCENTE_USER and contrasena == DOCENTE_PASS:
            st.session_state.docente_auth = True
            st.session_state.vista = "panel"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
    st.markdown('</div>', unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════
#  VISTA: PANEL DOCENTE
# ══════════════════════════════════════════════════════════════
 
elif st.session_state.vista == "panel" and st.session_state.docente_auth:
    st.title("📊 Panel docente")
    st.caption("Consulta, descarga y administra el historial de evaluaciones.")
    st.divider()
 
    df = cargar_registros()
 
    if df.empty:
        st.info("Aún no hay evaluaciones registradas.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de registros", len(df))
        with col2:
            st.metric("Promedio del grupo", f"{df['Nota Final'].mean():.2f}")
        with col3:
            st.metric("Nota más alta", f"{df['Nota Final'].max():.2f}")
 
        st.write("")
        st.markdown("#### Historial de evaluaciones")
        st.dataframe(df, use_container_width=True, hide_index=True)
 
        st.write("")
        st.markdown("#### Descargar registros")
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Descargar como Excel (.csv)",
            data=csv_bytes,
            file_name=f"historial_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )
 
        st.write("")
        st.markdown("#### Eliminar registros")
        st.warning("⚠️ Esta acción eliminará **todos** los registros de forma permanente. Asegúrate de haber descargado el archivo antes de continuar.")
 
        if not st.session_state.confirmar_eliminar:
            st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
            if st.button("🗑️  Eliminar todos los registros", use_container_width=True):
                st.session_state.confirmar_eliminar = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("¿Estás seguro? Esta acción no se puede deshacer.")
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("Sí, eliminar", type="primary", use_container_width=True):
                    if os.path.exists(CSV_FILE):
                        os.remove(CSV_FILE)
                    st.session_state.confirmar_eliminar = False
                    st.success("Registros eliminados correctamente.")
                    st.rerun()
            with col_no:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.confirmar_eliminar = False
                    st.rerun()
