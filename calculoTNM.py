import os
import streamlit as st
import pandas as pd

# =====================================================
# CONFIGURACIÓN
# =====================================================
TUMORES_PATH = "tumores"

st.set_page_config(page_title="Clasificación TNM ", page_icon="imagenes/logo_app.png", layout="wide")

main_container = st.empty()

        # -------------------------------------------------
        # BARRA LATERAL
        # -------------------------------------------------

col1, col2, col3 = st.sidebar.columns([1,4,1])

with col2:
    st.image("imagenes/logo_app.png", use_container_width=True)

st.sidebar.title("Menú")

# Botón Inicio
if st.sidebar.button("Inicio", use_container_width=True):
    st.session_state["pantalla"] = "inicio"
    st.session_state["tumor_seleccionado"] = None
    st.session_state["estado_viral"] = None
    st.rerun()

# Nombre del cáncer seleccionado
if st.session_state.get("tumor_seleccionado"):
    st.sidebar.markdown(
        f"""
        <div style="
            background-color: #FFC5D3;
            border-left: 4px solid #99606E;
            border-radius: 6px;
            padding: 10px 12px;
            margin-top: 8px;
            margin-bottom: 4px;
        ">
            <div style="font-size:10px; color:#000000; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
                Tumor seleccionado
            </div>
            <div style="font-size:13px; color:#662C39; font-weight:600; line-height:1.3;">
                {st.session_state["tumor_seleccionado"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
# Mas info

st.sidebar.markdown(
    '🔗 <a href="https://www.cancer.gov/espanol/tipos/cabeza-cuello/pro/adulto" target="_blank">Más info</a>',
    unsafe_allow_html=True
)



# Logo HUBU
st.sidebar.image(
    "imagenes/logo_hubu.png",
    width=240
)

st.sidebar.markdown(
    """
    <div style="text-align:center; font-size:12px; color:#9e9e9e; margin-top:0px;">
     Servicio Otorrinolaringología HUBU <br> Iván Mamolar | Ingeniería de la salud <br>© 2026
    </div>
    """,
    unsafe_allow_html=True
)
# =====================================================
# ESTADO DE PANTALLA
# =====================================================
if "pantalla" not in st.session_state:
    st.session_state["pantalla"] = "inicio"

if "tumor_seleccionado" not in st.session_state:
    st.session_state["tumor_seleccionado"] = None

if "estado_viral" not in st.session_state:
    st.session_state["estado_viral"] = None


# =====================================================
# FUNCIONES
# =====================================================

import re

@st.cache_data
def obtener_tumores_disponibles():
    if not os.path.exists(TUMORES_PATH):
        return {}

    archivos = [
        f for f in os.listdir(TUMORES_PATH)
        if f.endswith(".xlsx")
    ]

    # ordenar por número inicial
    archivos = sorted(
        archivos,
        key=lambda x: int(re.match(r"(\d+)", x).group()) if re.match(r"(\d+)", x) else 999
    )

    tumores = {}

    for archivo in archivos:
        nombre_sin_ext = os.path.splitext(archivo)[0]

        # quitar "1. ", "2. ", etc
        nombre_visible = re.sub(r"^\d+\.\s*", "", nombre_sin_ext)

        tumores[nombre_visible] = archivo

    return tumores


def unique_list(values):
    seen = set()
    out = []
    for v in values:
        v = str(v).strip()
        if v == "" or v.lower() == "nan":
            continue
        if v not in seen:
            out.append(v)
            seen.add(v)
    return out


def parse_subitems(text):
    if text is None:
        return []
    text = str(text).strip()
    if text == "" or text.lower() == "nan":
        return []
    return [x.strip() for x in text.split(",") if x.strip()]


@st.cache_data
def load_excel(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name)

    # Columnas opcionales
    for col in ["Prioridad", "Subitems", "Tipo", "Localizacion", "Biomarcador"]:
        if col not in df.columns:
            df[col] = "" if col != "Prioridad" else 0

    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].fillna("").astype(str).str.strip()

    return df


def cumple_condicion(valor_input, valor_regla):
    if str(valor_regla).upper() == "ANY":
        return True
    lista = [v.strip() for v in str(valor_regla).split(",") if v.strip()]
    return valor_input in lista


def clasificar_estadio(valores_TNM, df_estadios):
    for _, row in df_estadios.iterrows():

        cumple_T = cumple_condicion(valores_TNM.get("T", ""), row.get("T", "ANY"))
        cumple_N = cumple_condicion(valores_TNM.get("N", ""), row.get("N", "ANY"))
        cumple_M = cumple_condicion(valores_TNM.get("M", ""), row.get("M", "ANY"))

        if cumple_T and cumple_N and cumple_M:
            return row.get("Estadio", "No definido")

    return "No clasificado"

# =====================================================
# PANTALLA 1 — SELECCIÓN DE CÁNCER
# =====================================================

col1, col2 = st.columns([3, 1])

if st.session_state["pantalla"] == "inicio":

    with col1:
        st.markdown(
            "<h1 style='margin-top:-30px;'>Clasificación TNM</h1>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='color:#9e9e9e; font-size:16px; margin-top:-15px;'>"
            "Aplicación centrada en cáncer de cabeza y cuello"
            "</p>",
            unsafe_allow_html=True
        )

        st.markdown("<h4 style='color: gray;'>Seleccione tipo de cáncer</h4>", unsafe_allow_html=True)

        tumores_dict = obtener_tumores_disponibles()
        

        cols_btn = st.columns(2)
        for i, nombre in enumerate(tumores_dict.keys()):
            with cols_btn[i % 2]:
                if st.button(nombre, use_container_width=True):
                    with st.spinner("Cargando datos..."):
                        st.session_state["tumor_seleccionado"] = nombre
                        st.session_state["pantalla"] = "tnm"
                        st.session_state["estado_viral"] = None
                        st.rerun()

    with col2:
        st.markdown("<h1 style='color: transparent;'>Titulo</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: transparent;'>Subtitulo</h4>", unsafe_allow_html=True)

        imagen_path = os.path.join("imagenes", "imagen_cuello.jpg")
        if os.path.exists(imagen_path):
            st.image(imagen_path, use_container_width=True)

    st.markdown(
    """
    <div style="text-align:center; font-size:12px; color:#9e9e9e; margin-top:40px;">
    Basado en:<br> AJCC Cancer Staging Manual 8th Edition<br>
    Head and Neck Cancer Staging (AJCC 8th Edition)
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# PANTALLA 2 — TNM 
# =====================================================
if st.session_state["pantalla"] == "tnm":

    # Contenedor centrado
    col_left, col_center, col_right = st.columns([1, 5, 1])

    with col_center:
        tumor_nombre = st.session_state["tumor_seleccionado"]
        st.header(tumor_nombre)

        # -------------------------------------------------
        # ESTADO VIRAL (RADIO)
        # -------------------------------------------------
        estado_viral = None

        # NASOFARINGE → VEB
        if "nasofaringe" in tumor_nombre.lower():

            st.markdown("#### Estado viral")

            estado_viral = st.radio(
                "Seleccione estado:",
                ["VEB+", "VEB-"],
                horizontal=True,
                key="estado_viral_radio"
            )

        # OROFARINGE → VPH (solo si es p16+ o p16-)
        elif "orofaringe" in tumor_nombre.lower():

            if "p16+" in tumor_nombre.lower() or "p16-" in tumor_nombre.lower():

                st.markdown("#### Estado viral")

                estado_viral = st.radio(
                    "Seleccione estado:",
                    ["VPH+", "VPH-"],
                    horizontal=True,
                    key="estado_viral_radio"
                )

        # Guardar en session_state
        if estado_viral:
            st.session_state["estado_viral"] = estado_viral

        if st.button("← Volver"):
            st.session_state["pantalla"] = "inicio"
            st.session_state["tumor_seleccionado"] = None
            st.session_state["estado_viral"] = None
            st.rerun()

        tumores_dict = obtener_tumores_disponibles()

        archivo_excel = tumores_dict[tumor_nombre]

        # -------------------------------------------------
        # CASO ESPECIAL ESCAMOSO
        # -------------------------------------------------

        if archivo_excel == "ESPECIAL":

            EXCEL_PATH = os.path.join(TUMORES_PATH, "Metástasis cervical de origen desconocido.xlsx")

            try:
                with st.spinner("Cargando datos ..."):
                    df_rules = load_excel(EXCEL_PATH, "TNM")
                    df_estadios = load_excel(EXCEL_PATH, "Estadios")
            except Exception as e:
                st.error(f"Error cargando archivo: {e}")
                st.stop()

            st.subheader("Biomarcador")

            biomarcadores = unique_list(df_rules["Biomarcador"].tolist())

            cols = st.columns(3)

            for i, biom in enumerate(biomarcadores):
                with cols[i % 3]:
                    if st.button(biom, use_container_width=True):
                        st.session_state["estado_viral"] = biom

            if st.session_state["estado_viral"]:
                df_rules = df_rules[df_rules["Biomarcador"] == st.session_state["estado_viral"]]

        else:

            EXCEL_PATH = os.path.join(TUMORES_PATH, archivo_excel)

            try:
                with st.spinner("Cargando datos ..."):
                    df_rules = load_excel(EXCEL_PATH, "TNM")
                    df_estadios = load_excel(EXCEL_PATH, "Estadios")
            except Exception as e:
                st.error(f"Error cargando archivo: {e}")
                st.stop()



        categorias_disponibles = ["T", "N", "M"]
        valores_TNM = {}
        explicaciones = {}

        # -------------------------------------------------
        # BIOMARCADORES
        # -------------------------------------------------

        biomarcadores = unique_list(df_rules["Biomarcador"].tolist())

        if biomarcadores:

            st.subheader("Biomarcador")

            biomarcador_seleccionado = st.radio(
                "Seleccione biomarcador:",
                biomarcadores,
                horizontal=True,
                key="biomarcador"
            )

            df_rules = df_rules[
                df_rules["Biomarcador"] == biomarcador_seleccionado
            ]

        # -------------------------------------------------
        # INTERFAZ TNM
        # -------------------------------------------------
        st.markdown(
                    "<p style='color:#9e9e9e; font-size:12px; font-style:italic;'>"
                    "* →  más detalles disponibles"
                    "</p>",
                    unsafe_allow_html=True
                )
        
        for cat in categorias_disponibles:

            
            st.subheader(f"Categoría {cat}")

            df_cat = df_rules[df_rules["Categoria"] == cat].copy()

            if df_cat.empty:
                st.warning(f"No hay reglas para {cat}")
                continue

            # LOCALIZACIÓN SOLO EN T
            if cat == "T":
                localizaciones = unique_list(df_cat["Localizacion"].tolist())
                if localizaciones:
                    localizacion = st.selectbox(
                        "Localización tumoral:",
                        localizaciones,
                        key="localizacion_T"
                    )
                    df_cat = df_cat[df_cat["Localizacion"] == localizacion]

            # TIPO SOLO EN N
            if cat == "N":
                tipos = unique_list(df_cat["Tipo"].tolist())
                if tipos:
                    tipo = st.radio(
                        "Tipo de evaluación:",
                        tipos,
                        horizontal=True
                    )
                    df_cat = df_cat[df_cat["Tipo"] == tipo]

            items = unique_list(df_cat["Item"].tolist())

            item = st.selectbox(
                f"{cat} - Característica:",
                items,
                key=f"item_{cat}"
            )

            df_item = df_cat[df_cat["Item"] == item].copy()
            df_item = df_item.sort_values("Prioridad", ascending=False)
            row = df_item.iloc[0]

            subitems = parse_subitems(row["Subitems"])

            seleccion_sub = []
            if subitems:
                seleccion_sub = st.multiselect(
                    f"{cat} - Detalles:",
                    subitems,
                    key=f"sub_{cat}"
                )

            valores_TNM[cat] = row["Resultado"]

            explicacion = row["Explicacion"]
            if seleccion_sub:
                explicacion += " + ".join(seleccion_sub)

            explicaciones[cat] = explicacion

        # -------------------------------------------------
        # RESULTADOS
        # -------------------------------------------------
        st.divider()
        st.header("Resultados TNM")

        resultado_simple = " ".join(
            [valores_TNM.get(k, "") for k in categorias_disponibles]
        )

        st.success(resultado_simple)

        estado_viral = st.session_state.get("estado_viral", None)

        # -------------------------
        # ENCABEZADO (UNA SOLA VEZ)
        # -------------------------
        if estado_viral:
            st.info(f"{tumor_nombre} ({estado_viral})")
        else:
            st.info(f"{tumor_nombre}")

        # -------------------------
        # DETALLE TNM (SIN REPETIR)
        # -------------------------
        resultado_explicado = " ".join(
            [f"{valores_TNM.get(k,'')} ({explicaciones.get(k,'')})"
            for k in categorias_disponibles]
        )

        st.info(resultado_explicado)

        # -------------------------------------------------
        # ESTADIO FINAL
        # -------------------------------------------------
        if all(k in valores_TNM for k in ["T", "N", "M"]):
            estadio = clasificar_estadio(valores_TNM, df_estadios)

            st.divider()
            st.header("Estadio final")

            tumor_nombre = st.session_state["tumor_seleccionado"]

            biomarcador_archivo = None

            if "p16+" in tumor_nombre:
                biomarcador_archivo = "p16+"

            elif "p16-" in tumor_nombre:
                biomarcador_archivo = "p16-"

            biomarcador_radio = st.session_state.get("biomarcador", None)


            if biomarcador_radio and biomarcador_radio != "Ninguno":
                st.success(f"Estadio ({biomarcador_radio}): {estadio}")

            elif biomarcador_archivo:
                st.success(f"Estadio ({biomarcador_archivo}): {estadio}")

            else:
                st.success(f"Estadio: {estadio}")