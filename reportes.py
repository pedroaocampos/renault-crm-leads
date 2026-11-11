import streamlit as st
import pandas as pd
import re

# Configuracion del panel ejecutivo
st.set_page_config(
    page_title="Renault Paraguay — Executive BI Analytics",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def cargar_analitica():
    df = pd.read_csv("clientes_renault_consolidado.csv")
    
    if "Estado" not in df.columns:
        df["Estado"] = "Pendiente"
    if "Telefono" not in df.columns:
        df["Telefono"] = ""
    df["Telefono"] = df["Telefono"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

    # Clasificacion B2B vs B2C
    patrones_b2b = r"\b(S\.?A\.?|S\.?R\.?L\.?|EMPRESA|AGRO|AGROPECUARIA|GANADERA|COMERCIAL|IMPORT|EXPORT|LOGISTICA|CONSTRUCTORA|GRUPO|SOCIEDAD|ASOCIACION|COOPERATIVA|DESARROLLOS)\b"
    df["Tipo_Cliente"] = df["Cliente"].apply(
        lambda x: "Corporativo (B2B)" if re.search(patrones_b2b, str(x).upper()) else "Persona Física (B2C)"
    )

    # Clasificacion de Canal y Geografia
    def clasificar_contacto(tel):
        nums = re.sub(r"\D", "", str(tel))
        if not nums or nums in ["0", "None", "nan"]:
            return "Sin Registro", "Desconocido"
        tel_loc = nums[3:] if nums.startswith("595") else nums
        
        if tel_loc.startswith("9") or tel_loc.startswith("09"):
            return "Celular (WhatsApp)", "Móvil Nacional"
        elif tel_loc.startswith("21") or tel_loc.startswith("021"):
            return "Línea Fija", "Gran Asunción / Central"
        elif tel_loc.startswith("61") or tel_loc.startswith("061"):
            return "Línea Fija", "Alto Paraná / CDE"
        elif tel_loc.startswith("71") or tel_loc.startswith("071"):
            return "Línea Fija", "Itapúa / Encarnación"
        else:
            return "Línea Fija / Otra", "Interior / Regional"

    res = df["Telefono"].apply(clasificar_contacto)
    df["Canal_Contacto"] = [r[0] for r in res]
    df["Region_Estimada"] = [r[1] for r in res]
    return df

df = cargar_analitica()

# --- ENCABEZADO ---
st.title("📊 Renault Paraguay — Tablero Ejecutivo BI & Auditoría de Leads")
st.caption("Inteligencia de datos sobre cartera histórica reactivada (1.449 cuentas procesadas).")

# --- MÉTRICAS GENERALES ---
total_leads = len(df)
total_b2b = (df["Tipo_Cliente"] == "Corporativo (B2B)").sum()
total_b2c = (df["Tipo_Cliente"] == "Persona Física (B2C)").sum()
total_wa = (df["Canal_Contacto"] == "Celular (WhatsApp)").sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Cartera Consolidada", f"{total_leads:,}")
k2.metric("🏢 Cuentas B2B (Empresas)", f"{total_b2b} ({total_b2b/total_leads*100:.1f}%)")
k3.metric("👤 Clientes Particulares (B2C)", f"{total_b2c} ({total_b2c/total_leads*100:.1f}%)")
k4.metric("💬 Conectividad WhatsApp", f"{total_wa} ({total_wa/total_leads*100:.1f}%)")

st.markdown("---")

# --- GRÁFICOS ANALÍTICOS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("🚗 Potencial de Renovación por Modelo Renault")
    conteo_modelos = df["Vehiculo_Renault_Sugerido"].value_counts()
    st.bar_chart(conteo_modelos)
    st.caption("Distribución del volumen proyectado para plan de importación y stock.")

with c2:
    st.subheader("📞 Perfil de Canales y Cobertura de Contacto")
    conteo_canales = df["Canal_Contacto"].value_counts()
    st.bar_chart(conteo_canales)
    st.caption("Porcentaje abordable de forma inmediata por mensajería vs. centralita corporativa.")

st.markdown("---")

# --- TABLA B2B Y DESCARGA ---
col_t1, col_t2 = st.columns([1.5, 1])

with col_t1:
    st.subheader("🏢 Muestra de Cuentas Corporativas B2B")
    filtro_b2b = df[df["Tipo_Cliente"] == "Corporativo (B2B)"][["Cliente", "Vehiculo_Renault_Sugerido", "Canal_Contacto", "Telefono"]]
    st.dataframe(filtro_b2b.head(15), use_container_width=True)

with col_t2:
    st.subheader("📥 Exportación Ejecutiva")
    st.write("Descarga la base enriquecida con todas las dimensiones analíticas agregadas (B2B/B2C, Canales, Prefijos y Segmentación) para presentar a dirección:")
    
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Descargar Dataset Enriquecido (CSV)",
        data=csv_bytes,
        file_name="informe_ejecutivo_renault_b2b.csv",
        mime="text/csv"
    )
