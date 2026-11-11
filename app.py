import streamlit as st
import pandas as pd
import math

# Configuración general de la página
st.set_page_config(
    page_title="Renault Prospección B2B — Panel Interactivo",
    page_icon="🚗",
    layout="wide"
)

# Cargar base de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("clientes_renault_consolidado.csv")
    if "Estado" not in df.columns:
        df["Estado"] = "Pendiente"
    return df

df = cargar_datos()

# Inicializar estados en session_state si no existen
if "estados" not in st.session_state:
    st.session_state.estados = {i: df.loc[i, "Estado"] for i in df.index}

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Prospección")

modelos_disponibles = sorted(list(df["Vehiculo_Renault_Sugerido"].dropna().unique()))
filtro_modelo = st.sidebar.multiselect(
    "Modelo Renault Sugerido:",
    options=modelos_disponibles,
    default=modelos_disponibles
)

estados_posibles = ["Pendiente", "Insistir", "Listo"]
filtro_estado = st.sidebar.multiselect(
    "Estado de Gestión:",
    options=estados_posibles,
    default=estados_posibles
)

st.sidebar.markdown("---")
registros_por_pagina = st.sidebar.slider(
    "Registros por página:",
    min_value=10,
    max_value=50,
    value=25,
    step=5
)

# Filtrar datos
df_filtrado = df[
    (df["Vehiculo_Renault_Sugerido"].isin(filtro_modelo)) &
    (df.index.map(st.session_state.estados).isin(filtro_estado))
]

# --- ENCABEZADO Y MÉTRICAS ---
st.title("🚗 Renault Prospección B2B — Panel Interactivo")
st.caption("Sistema de reactivación comercial de cartera histórica: 1.449 cuentas procesadas.")

total_cartera = len(df)
pendientes = sum(1 for v in st.session_state.estados.values() if v == "Pendiente")
insistir = sum(1 for v in st.session_state.estados.values() if v == "Insistir")
listos = sum(1 for v in st.session_state.estados.values() if v == "Listo")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Cartera Total", total_cartera)
col_m2.metric("⏳ Pendientes", pendientes)
col_m3.metric("⚠️ Insistir / Recontactar", insistir)
col_m4.metric("✅ Listos / Gestionados", listos)

st.markdown("---")
st.subheader(f"Contactos Filtrados: {len(df_filtrado)}")

# --- PAGINACIÓN ---
if len(df_filtrado) > 0:
    total_paginas = math.ceil(len(df_filtrado) / registros_por_pagina)

    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav2:
        pagina_actual = st.number_input(
            f"Página (1 de {total_paginas}):",
            min_value=1,
            max_value=total_paginas,
            value=1,
            step=1
        )

    inicio = (pagina_actual - 1) * registros_por_pagina
    fin = inicio + registros_por_pagina
    df_pagina = df_filtrado.iloc[inicio:fin]

    # --- LISTADO DE CONTACTOS ---
    for idx, row in df_pagina.iterrows():
        nombre_cliente = row.get("Cliente", "Sin Nombre")
        sugerido = row.get("Vehiculo_Renault_Sugerido", "Renault Flota")
        origen = row.get("Archivo_Origen", "Histórico")
        pitch = row.get("Pitch_Comercial", "Propuesta de renovación de flota Renault.")
        tel_raw = str(row.get("Telefono", "")).strip().replace(".0", "")

        # Normalizar teléfono para enlaces
        tel_limpio = "".join([c for c in tel_raw if c.isdigit()])
        if tel_limpio.startswith("09"):
            tel_wa = "595" + tel_limpio[1:]
        elif tel_limpio.startswith("9"):
            tel_wa = "595" + tel_limpio
        else:
            tel_wa = tel_limpio

        msg_wa = f"Hola {nombre_cliente}, nos comunicamos desde Renault Paraguay para presentarte nuestra propuesta para el nuevo {sugerido}."
        url_wa = f"https://wa.me/{tel_wa}?text={msg_wa.replace(' ', '%20')}"
        url_call = f"tel:+{tel_wa}"

        with st.expander(f"🏢 {nombre_cliente} | Sugerido: {sugerido}"):
            col_info, col_pitch, col_accion = st.columns([2, 2, 1.5])

            with col_info:
                st.markdown(f"**Origen:** `{origen}`")
                st.markdown(f"**Historial:** Cartera Histórica")
                st.markdown(f"**Teléfono:** `{tel_raw if tel_raw else 'No disponible'}`")

            with col_pitch:
                st.info(f"🎯 **Oferta:** {sugerido}")
                st.write(f"💡 {pitch}")

            with col_accion:
                estado_actual = st.session_state.estados.get(idx, "Pendiente")
                nuevo_estado = st.selectbox(
                    "Estado:",
                    options=["Pendiente", "Insistir", "Listo"],
                    index=["Pendiente", "Insistir", "Listo"].index(estado_actual),
                    key=f"estado_{idx}"
                )
                if nuevo_estado != estado_actual:
                    st.session_state.estados[idx] = nuevo_estado
                    st.rerun()

                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <a href="{url_wa}" target="_blank" style="text-decoration:none; background:#25D366; color:white; padding:8px 14px; border-radius:5px; font-weight:bold; font-size:14px;">💬 WhatsApp</a>
                    <a href="{url_call}" style="text-decoration:none; background:#007BFF; color:white; padding:8px 14px; border-radius:5px; font-weight:bold; font-size:14px;">📞 Llamar</a>
                </div>
                """, unsafe_allow_html=True)
else:
    st.warning("No hay registros que coincidan con los filtros seleccionados.")
