import os
import re
import streamlit as st
import pandas as pd

# =====================================================
# CONFIGURACIÓN
# =====================================================
TUMORES_PATH = "tumores"

st.set_page_config(page_title="TNM — cabeza y cuello", page_icon="imagenes/logo_app.png", layout="wide")


# =====================================================
# FUNCIÓNES PRINCIPALES
# =====================================================
def reset_tnm():
    st.session_state["tnm_paso"] = "T"
    st.session_state["tnm_selecciones"] = {}
    st.session_state["tnm_explicaciones"] = {}
    st.session_state["tnm_items"] = {}
    prefijos_borrar = ("chk_", "estado_tnm_", "subitems_sel_", "subitems_guardados_")
    claves_borrar = ("localizacion_T", "tipo_N", "estado_viral_radio")
    for key in list(st.session_state.keys()):
        if key.startswith(prefijos_borrar) or key in claves_borrar:
            del st.session_state[key]

@st.cache_data
def obtener_tumores_disponibles():
    if not os.path.exists(TUMORES_PATH):
        return {}
    archivos = sorted(
        [f for f in os.listdir(TUMORES_PATH) if f.endswith(".xlsx")],
        key=lambda x: int(re.match(r"(\d+)", x).group()) if re.match(r"(\d+)", x) else 999
    )
    return {re.sub(r"^\d+\.\s*", "", os.path.splitext(f)[0]): f for f in archivos}

def unique_list(values):
    seen, out = set(), []
    for v in values:
        v = str(v).strip()
        if v and v.lower() != "nan" and v not in seen:
            out.append(v)
            seen.add(v)
    return out

def parse_subitems(text):
    text = str(text).strip()
    if not text or text.lower() == "nan":
        return []
    return [x.strip() for x in text.split(",") if x.strip()]

@st.cache_data
def load_excel(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name)
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
    return valor_input in [v.strip() for v in str(valor_regla).split(",") if v.strip()]

def clasificar_estadio(valores_TNM, df_estadios):
    for _, row in df_estadios.iterrows():
        if (cumple_condicion(valores_TNM.get("T", ""), row.get("T", "ANY")) and
                cumple_condicion(valores_TNM.get("N", ""), row.get("N", "ANY")) and
                cumple_condicion(valores_TNM.get("M", ""), row.get("M", "ANY"))):
            return row.get("Estadio", "No definido")
    return "No clasificado"



# =====================================================
# BARRA LATERAL
# =====================================================
col_1, col_logo, col_2 = st.sidebar.columns([1, 3, 1])
with col_logo:
    st.image("imagenes/logo_app.png", use_container_width=True)

st.sidebar.title("Menú")

if st.sidebar.button("Inicio", use_container_width=True):
    reset_tnm()
    st.session_state["pantalla"] = "inicio"
    st.session_state["tumor_seleccionado"] = None
    st.session_state["estado_viral"] = None
    st.session_state["biomarcador_usuario"] = None
    st.rerun()

if st.session_state.get("tumor_seleccionado"):
    st.sidebar.markdown(
        f"""<div style="background-color:#FFC5D3; border-left:4px solid #99606E;
                        border-radius:6px; padding:10px 12px; margin-top:8px;">
            <div style="font-size:10px; color:#000; text-transform:uppercase;
                        letter-spacing:1px; margin-bottom:4px;">Tumor seleccionado</div>
            <div style="font-size:13px; color:#662C39; font-weight:600;">
                {st.session_state["tumor_seleccionado"]}</div>
        </div>""",
        unsafe_allow_html=True
    )

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown(
    '🔗 <a href="https://www.cancer.gov/espanol/tipos/cabeza-cuello/pro/adulto" target="_blank">Más info</a>',
    unsafe_allow_html=True
)
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.image("imagenes/logo_hubu.png", width=220)
st.sidebar.markdown(
    """<div style="text-align:center; font-size:11px; color:#9e9e9e;">
     Servicio Otorrinolaringología HUBU <br> Iván Mamolar | Ingeniería de la salud <br>© 2026
    </div>""",
    unsafe_allow_html=True
)

# =====================================================
# ESTADO INICIAL
# =====================================================
for clave, valor in [
    ("pantalla", "inicio"),
    ("tumor_seleccionado", None),
    ("estado_viral", None),
    ("tnm_paso", "T"),
    ("tnm_selecciones", {}),
    ("tnm_explicaciones", {}),
    ("tnm_items", {}),
]:
    if clave not in st.session_state:
        st.session_state[clave] = valor


# =====================================================
# PANTALLA 1 — SELECCIÓN DE CÁNCER
# =====================================================
col1, col2 = st.columns([3, 1])

if st.session_state["pantalla"] == "inicio":
    with col1:
        st.markdown("<h1 style='margin-top:-30px;'>Clasificación TNM</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#9e9e9e; font-size:16px; margin-top:-15px;'>"
            "Aplicación centrada en cáncer de cabeza y cuello</p>",
            unsafe_allow_html=True)
        
        st.markdown("<h4 style='color:gray;'>Seleccione tipo de cáncer</h4>", unsafe_allow_html=True)

        tumores_dict = obtener_tumores_disponibles()
        cols_btn = st.columns(2)
        for i, nombre in enumerate(tumores_dict.keys()):
            with cols_btn[i % 2]:
                if st.button(nombre, use_container_width=True):
                    reset_tnm()
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

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(
        """<div style="text-align:center; font-size:11px; color:#9e9e9e; margin-top:40px;">
        Basado en:<br> American Joint Committee on Cancer (AJCC). AJCC Cancer Staging Manual. 8th edition. <br>
        New York: Springer; 2017. NCCN Guidelines Version 1.2026. Head and Neck Cancers</div>""",
        unsafe_allow_html=True)

# =====================================================
# PANTALLA 2 — TNM
# =====================================================
if st.session_state["pantalla"] == "tnm":

    col_left, col_center, col_right = st.columns([1, 5, 1])

    with col_center:
        tumor_nombre = st.session_state["tumor_seleccionado"]
        st.header(tumor_nombre)

        if st.button("← Volver"):
            reset_tnm()
            st.session_state["pantalla"] = "inicio"
            st.session_state["tumor_seleccionado"] = None
            st.session_state["estado_viral"] = None
            st.session_state["biomarcador_usuario"] = None
            st.rerun()

        # -------------------------------------------------
        # ESTADO VIRAL
        # -------------------------------------------------
        estado_viral = None
        if "nasofaringe" in tumor_nombre.lower():
            st.markdown("#### Estado viral")
            estado_viral = st.radio("Seleccione estado:", ["VEB+", "VEB-"], horizontal=True, key="estado_viral_radio")
        elif "orofaringe" in tumor_nombre.lower() and ("p16+" in tumor_nombre.lower()):
            st.markdown("#### Biomarcador")
            estado_viral = st.radio("Seleccione estado:", ["VPH+", "VPH-"], horizontal=True, key="estado_viral_radio")
        elif "orofaringe" in tumor_nombre.lower() and ("p16-" in tumor_nombre.lower()):
            st.markdown("#### Biomarcador")
            estado_viral = st.radio("Seleccione estado:", ["VPH-", "VPH+"], horizontal=True, key="estado_viral_radio")
        if estado_viral:
            st.session_state["estado_viral"] = estado_viral

        # -------------------------------------------------
        # CARGA DE DATOS
        # -------------------------------------------------
        tumores_dict = obtener_tumores_disponibles()
        archivo_excel = tumores_dict[tumor_nombre]
        excel_path = os.path.join(
            TUMORES_PATH,
            "Metástasis cervical de origen desconocido.xlsx" if archivo_excel == "ESPECIAL" else archivo_excel)
        
        try:
            df_rules = load_excel(excel_path, "TNM")
            df_estadios = load_excel(excel_path, "Estadios")
        except Exception as e:
            st.error(f"Error cargando archivo: {e}")
            st.stop()

        categorias_disponibles = ["T", "N", "M"]
        pasos_orden = ["T", "N", "M"]

        # ------------------------------------------------------
        # Casos VPH+/- en orofaringe
        #-------------------------------------------------------
        tumores_dict = obtener_tumores_disponibles()

        tumor_base = tumor_nombre

        if "orofaringe" in tumor_nombre.lower():
            estado = st.session_state.get("estado_viral")

            if "p16+" in tumor_nombre.lower() and estado == "VPH-":
                tumor_base = "4. Orofaringe (p16-)"
            elif "p16-" in tumor_nombre.lower() and estado == "VPH+":
                tumor_base = "3. Orofaringe (p16+)"

        # 🔴 IMPORTANTE: comprobar que existe
        if tumor_base not in tumores_dict:
            st.error(f"No se encontró el archivo para: {tumor_base}")
            st.stop()

        archivo_excel = tumores_dict[tumor_base]

        excel_path = os.path.join(
            TUMORES_PATH,
            "Metástasis cervical de origen desconocido.xlsx" if archivo_excel == "ESPECIAL" else archivo_excel
        )

        # 🔴 AHORA sí cargamos
        df_rules = load_excel(excel_path, "TNM")
        df_estadios = load_excel(excel_path, "Estadios")
        # -------------------------------------------------
        # BIOMARCADORES
        # -------------------------------------------------
        biomarcadores = unique_list(df_rules["Biomarcador"].tolist())
        if biomarcadores:
            st.markdown("#### Biomarcador")
            estado_biom = {b: st.session_state.get(f"chk_{b}", False) for b in biomarcadores}
            tiene_vph = any("VPH" in b for b, v in estado_biom.items() if v)
            tiene_p16 = any("p16" in b for b, v in estado_biom.items() if v)
            total_marcados = sum(estado_biom.values())

            seleccion = []
            cols = st.columns(len(biomarcadores))
            for i, biom in enumerate(biomarcadores):
                with cols[i]:
                    deshabilitado = (
                        ("VPH" in biom and tiene_vph and not estado_biom[biom]) or
                        ("p16" in biom and tiene_p16 and not estado_biom[biom]) or
                        (total_marcados >= 2 and not estado_biom[biom]))
                    
                    if st.checkbox(biom, key=f"chk_{biom}", disabled=deshabilitado):
                        seleccion.append(biom)

            clasificacion_final = None
            if "VPH+" in seleccion:   
                clasificacion_final = "p16+"
            elif "VPH-" in seleccion: 
                clasificacion_final = "p16-"
            elif "p16+" in seleccion: 
                clasificacion_final = "p16+"
            elif "p16-" in seleccion: 
                clasificacion_final = "p16-"
            elif seleccion:           
                clasificacion_final = seleccion[0]

            if not clasificacion_final:
                st.info("Seleccione al menos un biomarcador para continuar.")
                st.stop()

            st.session_state["biomarcador_usuario"] = " / ".join(seleccion)
            df_rules = df_rules[df_rules["Biomarcador"] == clasificacion_final]

        # -------------------------------------------------
        # BARRA DE PROGRESO
        # -------------------------------------------------
        paso_actual = st.session_state.get("tnm_paso", "T")
        paso_idx = pasos_orden.index(paso_actual) if paso_actual in pasos_orden else 0

        st.markdown("<br>", unsafe_allow_html=True)
        estilos_paso = {
            "activo":     "background-color:#d0166a; color:white; padding:8px 12px; border-radius:8px; text-align:center; font-weight:bold; font-size:14px;",
            "completado": "background-color:#28a745; color:white; padding:8px 12px; border-radius:8px; text-align:center; font-size:14px;",
            "pendiente":  "background-color:#e0e0e0; color:#888; padding:8px 12px; border-radius:8px; text-align:center; font-size:14px;"
        }
        etiquetas_pasos = {"T": "Tumor (T)", "N": "Ganglios (N)", "M": "Metástasis (M)"}

        cols_pasos = st.columns(3)
        for i, cat in enumerate(pasos_orden):
            with cols_pasos[i]:
                if cat == paso_actual:
                    estilo, label = estilos_paso["activo"], etiquetas_pasos[cat]
                elif cat in st.session_state["tnm_selecciones"]:
                    estilo = estilos_paso["completado"]
                    label = f" ✓ {cat}: {st.session_state['tnm_selecciones'][cat]}"
                else:
                    estilo, label = estilos_paso["pendiente"], etiquetas_pasos[cat]
                st.markdown(f"<div style='{estilo}'>{label}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)



        # -------------------------------------------------
        # FLUJO TNM PASO A PASO
        # -------------------------------------------------
        todas_completadas = all(c in st.session_state["tnm_selecciones"] for c in categorias_disponibles)

        if not todas_completadas:
            cat = paso_actual
            
            st.markdown(f"#### Resumen de la selección")
            # Resumen de categorías ya completadas
            for c_prev in [c for c in pasos_orden if c in st.session_state["tnm_selecciones"]]:
                val = st.session_state["tnm_selecciones"][c_prev]
                etiqueta = st.session_state["tnm_items"].get(c_prev, val)
                texto = f"{etiqueta}"
                st.markdown(f"— {texto}")

            df_cat = df_rules[df_rules["Categoria"] == cat].copy()

            if df_cat.empty:
                st.warning(f"No hay reglas para {cat}")
            else:
                # Localización (solo T)
                if cat == "T":
                    localizaciones = unique_list(df_cat["Localizacion"].tolist())
                    if localizaciones:
                        loc = st.selectbox("Localización tumoral:", localizaciones, key="localizacion_T")
                        df_cat = df_cat[df_cat["Localizacion"] == loc]

                # Tipo (solo N)
                if cat == "N":
                    tipos = unique_list(df_cat["Tipo"].tolist())
                    if tipos:
                        tipo = st.radio("Tipo de evaluación:", tipos, horizontal=True, key="tipo_N")
                        df_cat = df_cat[df_cat["Tipo"] == tipo]

                df_cat = df_cat.reset_index(drop=True)

                # Estado de selección por índice de fila
                estado_key = f"estado_tnm_{cat}"
                if estado_key not in st.session_state:
                    st.session_state[estado_key] = {}
                estado = st.session_state[estado_key]
                for idx in df_cat.index:
                    if idx not in estado:
                        estado[idx] = False

                # Resultado bloqueante (del primer marcado)
                resultado_bloqueante = next(
                    (str(df_cat.loc[idx, "Resultado"]).strip() for idx in df_cat.index if estado.get(idx)),
                    None
                )

                st.markdown(f"#### Categoría {cat}")
                st.markdown(
                    "<p style='color:#9e9e9e; font-size:12px; font-style:italic;'>"
                    "* → más detalles disponibles </p>",
                    unsafe_allow_html=True
                )
                
                cambio = False
                for idx, row_data in df_cat.iterrows():
                    resultado_fila = str(row_data["Resultado"]).strip()
                    item_texto = str(row_data["Item"]).strip()
                    es_compatible = (resultado_bloqueante is None or resultado_fila == resultado_bloqueante)
                    valor_actual = estado.get(idx, False) and es_compatible

                    nuevo_valor = st.checkbox(f"{item_texto}", value=valor_actual, disabled=not es_compatible)
                    if nuevo_valor != valor_actual:
                        estado[idx] = nuevo_valor
                        cambio = True

                if cambio:
                    st.session_state[estado_key] = estado
                    st.rerun()

                indices_marcados = {idx for idx in df_cat.index if estado.get(idx)}

                # Subitems opcionales
                subitems_totales = list(dict.fromkeys(
                    sub for idx_sel in indices_marcados
                    for sub in parse_subitems(df_cat.loc[idx_sel, "Subitems"])
                ))
                if subitems_totales:
                    st.markdown(f"**Detalles adicionales para {cat}** (opcional):")
                    subs = st.multiselect("", subitems_totales, key=f"subitems_sel_{cat}")
                    st.session_state[f"subitems_guardados_{cat}"] = subs
                else:
                    st.session_state[f"subitems_guardados_{cat}"] = []

                st.markdown("<br>", unsafe_allow_html=True)

                if indices_marcados:
                    siguiente_cat = pasos_orden[paso_idx + 1] if paso_idx < len(pasos_orden) - 1 else None
                    btn_label = f"Siguiente: Categoría {siguiente_cat} →" if siguiente_cat else "Ver Resultados →"

                    if st.button(btn_label, type="primary", use_container_width=True):
                        resultados, explicaciones_list, items_list = [], [], []
                        for idx_sel in sorted(indices_marcados):
                            for lista, col in [(resultados, "Resultado"), (explicaciones_list, "Explicacion"), (items_list, "Item")]:
                                val = df_cat.loc[idx_sel, col]
                                if val and str(val).lower() not in ("", "nan") and val not in lista:
                                    lista.append(val)

                        resultado_cat = resultados[0] if len(set(resultados)) == 1 else " / ".join(resultados)
                        explicacion_cat = " + ".join(explicaciones_list)
                        items_label_cat = " + ".join(items_list)

                        subs_sel = st.session_state.get(f"subitems_guardados_{cat}", [])
                        if subs_sel:
                            explicacion_cat += " | " + " + ".join(subs_sel)
                            items_label_cat += " | " + " + ".join(subs_sel)

                        st.session_state["tnm_selecciones"][cat] = resultado_cat
                        st.session_state["tnm_explicaciones"][cat] = explicacion_cat
                        st.session_state["tnm_items"][cat] = items_label_cat
                        st.session_state["tnm_paso"] = siguiente_cat if siguiente_cat else "RESULTADOS"
                        st.rerun()
                else:
                    st.info(f"Seleccione al menos una opción de la categoría {cat} para continuar.")

                # Volver al paso anterior
                if paso_idx > 0:
                    cat_anterior = pasos_orden[paso_idx - 1]
                    if st.button(f"← Volver a categoría {cat_anterior}"):
                        st.session_state["tnm_selecciones"].pop(cat_anterior, None)
                        st.session_state["tnm_paso"] = cat_anterior
                        for key in list(st.session_state.keys()):
                            if key in (f"estado_tnm_{cat}", f"subitems_sel_{cat}", f"subitems_guardados_{cat}"):
                                del st.session_state[key]
                        st.rerun()

        # -------------------------------------------------
        # RESULTADOS FINALES
        # -------------------------------------------------
        else:
            if st.button("Nueva clasificación TNM"):
                reset_tnm()
                st.rerun()

            valores_TNM = st.session_state["tnm_selecciones"]
            explicaciones = st.session_state["tnm_explicaciones"]
            items_guardados = st.session_state["tnm_items"]

            st.markdown(f"#### Resumen de la selección")

            for c in categorias_disponibles:
                if c in valores_TNM:
                    val = valores_TNM[c]
                    etiqueta = items_guardados.get(c, val)
                    texto = f"{etiqueta}"
                    st.markdown(f"— {texto}")

            st.divider()
            st.header("Resultados TNM")



            estado_viral = st.session_state.get("estado_viral")
            biomarcador_usuario = st.session_state.get("biomarcador_usuario")

            if estado_viral:
                prefijo = f"{tumor_nombre} ({estado_viral})"
            elif biomarcador_usuario:
                prefijo = f"{tumor_nombre} ({biomarcador_usuario})"
            else:
                prefijo = tumor_nombre

            resultado_simple = " ".join(
            [valores_TNM.get(k, "") for k in categorias_disponibles])

            st.success(resultado_simple)

            detalle_tnm = " ".join(
                f"{valores_TNM.get(k, '')} ({explicaciones.get(k, '')})"
                for k in categorias_disponibles
            )
            st.info(f"{prefijo}: {detalle_tnm}" if detalle_tnm.strip() else prefijo)

            # Estadio final
            if all(k in valores_TNM for k in ["T", "N", "M"]):
                estadio = clasificar_estadio(valores_TNM, df_estadios)
                st.divider()
                st.header("Estadio final")
                biomarcador_archivo = "p16+" if "p16+" in tumor_nombre else ("p16-" if "p16-" in tumor_nombre else None)
                if biomarcador_archivo:
                    st.success(f"Estadio ({biomarcador_archivo}): {estadio}")
                else:
                    st.success(f"Estadio: {estadio}")