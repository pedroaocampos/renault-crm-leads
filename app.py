import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(
    page_title="Renault B2B - CRM & Dialer",
    page_icon="🚗",
    layout="wide"
)

# Cargar la base de 1.449 clientes
@st.cache_data
def cargar_datos():
    df = pd.read_csv("clientes_renault_consolidado.csv")
    if "Estado" not in df.columns:
        df["Estado"] = "Pendiente"
    if "Telefono" not in df.columns:
        # Placeholder para teléfonos a completar o enriquecer
        df["Telefono"] = "+595981000000"
    if "Email" not in df.columns:
        df["Email"] = "contacto@cliente.com"
    return df

if "df_crm" not in st.session_state:
    st.session_state.df_crm = cargar_datos()

# Encabezado y Métricas
st.title("🚗 Renault Prospección B2B — Panel Interactivo")
st.markdown("Sistema de reactivación comercial de cartera histórica: 1.449 cuentas procesadas.")

c1, c2, c3, c4 = st.columns(4)
total = len(st.session_state.df_crm)
pendientes = len(st.session_state.df_crm[st.session_state.df_crm["Estado"] == "Pendiente"])
insistir = len(st.session_state.df_crm[st.session_state.df_crm["Estado"] == "Insistir"])
listos = len(st.session_state.df_crm[st.session_state.df_crm["Estado"] == "Listo"])

c1.metric("Cartera Total", total)
c2.metric("⏳ Pendientes", pendientes)
c3.metric("⚠️ Insistir / Recontactar", insistir)
c4.metric("✅ Listos / Gestionados", listos)

st.divider()

# Filtros laterales
st.sidebar.header("Filtros de Prospección")
filtro_modelo = st.sidebar.multiselect(
    "Modelo Renault Sugerido:",
    options=list(st.session_state.df_crm["Vehiculo_Renault_Sugerido"].unique()),
    default=list(st.session_state.df_crm["Vehiculo_Renault_Sugerido"].unique())
)

filtro_estado = st.sidebar.multiselect(
    "Estado de Gestión:",
    options=["Pendiente", "Insistir", "Listo"],
    default=["Pendiente", "Insistir", "Listo"]
)

df_vista = st.session_state.df_crm[
    (st.session_state.df_crm["Vehiculo_Renault_Sugerido"].isin(filtro_modelo)) &
    (st.session_state.df_crm["Estado"].isin(filtro_estado))
]

st.subheader(f"Contactos Filtrados: {len(df_vista)}")

# Listado interactivo paginado de a 20 clientes
limite = st.sidebar.slider("Mostrar registros por página", 5, 50, 15)

for idx, row in df_vista.head(limite).iterrows():
    with st.expander(f"🏢 {row['Cliente']} | Sugerido: {row['Vehiculo_Renault_Sugerido']}", expanded=False):
        col_info, col_pitch, col_accion = st.columns([4, 4, 3])
        
        with col_info:
            st.markdown(f"**Origen:** `{row['Archivo_Origen']}`")
            st.markdown(f"**Historial:** {row['Vehiculo_Comprado']}")
            st.markdown(f"**Teléfono:** `{row['Telefono']}`")
            
        with col_pitch:
            st.success(f"🎯 **Oferta:** {row['Vehiculo_Renault_Sugerido']}")
            st.info(f"💡 {row['Pitch_Comercial']}")
            
        with col_accion:
            nuevo_est = st.selectbox(
                "Estado:",
                options=["Pendiente", "Insistir", "Listo"],
                index=["Pendiente", "Insistir", "Listo"].index(row["Estado"]),
                key=f"est_{idx}"
            )
            if nuevo_est != row["Estado"]:
                st.session_state.df_crm.at[idx, "Estado"] = nuevo_est
                st.rerun()
                
            # Links rápidos de contacto
            msg = f"Hola {row['Cliente']}, le contactamos de Renault. Vemos que cuenta con flota previa y queremos presentarle las condiciones corporativas para el nuevo {row['Vehiculo_Renault_Sugerido']}."
            msg_url = urllib.parse.quote(msg)
            
            w_col, t_col = st.columns(2)
            w_col.link_button("💬 WhatsApp", f"https://api.whatsapp.com/send?phone={row['Telefono']}&text={msg_url}")
            t_col.link_button("📞 Llamar", f"tel:{row['Telefono']}")
