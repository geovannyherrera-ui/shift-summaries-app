import datetime
import os
import pandas as pd
import streamlit as st

# Archivo CSV que actuará como base de datos en la nube/servidor
DB_FILE = "shift_data.csv"


def load_data():
  if os.path.exists(DB_FILE):
    return pd.read_csv(DB_FILE)
  else:
    return pd.DataFrame(
        columns=[
            "Fecha",
            "Turno",
            "Responsable",
            "Métrica Clave",
            "Handover",
            "Timestamp",
        ]
    )


def save_data(new_record):
  df = load_data()
  df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
  df.to_csv(DB_FILE, index=False)


st.set_page_config(
    page_title="Shift Summary Tracker", page_icon="📋", layout="wide"
)

st.title("📋 Control de Turnos y Handovers")

tab1, tab2, tab3 = st.tabs(
    [
        "➕ Nuevo Turno (Form)",
        "📊 Historial General (Database)",
        "🚨 Handovers de Hoy",
    ]
)

# --- PESTAÑA 1: FORMULARIO ---
with tab1:
  st.header("Ingresar Resumen de Turno")

  with st.form("shift_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      fecha_turno = st.date_input("Fecha del Turno", datetime.date.today())
      turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
    with col2:
      responsable = st.text_input("Responsable / Supervisor")
      metrica = st.number_input(
          "Métrica Clave (ej. Unidades producidas / Incidentes)", value=0
      )

    handover_text = st.text_area(
        "Handover (Descripción de lo acontecido en el turno)",
        placeholder="Escribe aquí los detalles importantes para el siguiente turno...",
    )

    submitted = st.form_submit_button("Guardar Shift Summary")

    if submitted:
      if responsable.strip() == "" or handover_text.strip() == "":
        st.error("Por favor completa el Responsable y el Handover.")
      else:
        nuevo_registro = {
            "Fecha": str(fecha_turno),
            "Turno": turno,
            "Responsable": responsable,
            "Métrica Clave": metrica,
            "Handover": handover_text,
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_data(nuevo_registro)
        st.success("¡Shift Summary guardado con éxito!")

# --- PESTAÑA 2: HISTORIAL GENERAL ---
with tab2:
  st.header("Historial de Registros")
  df_historial = load_data()

  if df_historial.empty:
    st.info("Aún no hay registros guardados.")
  else:
    search_term = st.text_input("Buscar en los registros...")
    if search_term:
      mask = df_historial.astype(str).apply(
          lambda x: x.str.contains(search_term, case=False, na=False)
      ).any(axis=1)
      df_historial = df_historial[mask]

    st.dataframe(df_historial, use_container_width=True)

# --- PESTAÑA 3: HANDOVERS DE HOY ---
with tab3:
  st.header("Handovers Ingresados Hoy")
  df_today = load_data()

  if df_today.empty:
    st.info("No hay registros disponibles.")
  else:
    hoy_str = str(datetime.date.today())
    # Limpiamos formato de fecha por seguridad
    df_today["Fecha"] = pd.to_datetime(df_today["Fecha"]).dt.strftime(
        "%Y-%m-%d"
    )
    handovers_hoy = df_today[df_today["Fecha"] == hoy_str]

    if handovers_hoy.empty:
      st.warning(f"No hay handovers registrados para el día de hoy ({hoy_str}).")
    else:
      st.success(f"Mostrando los handovers de hoy ({hoy_str}):")
      for index, row in handovers_hoy.iterrows():
        with st.container(border=True):
          st.markdown(
              f"**Turno:** {row['Turno']} | **Responsable:**"
              f" {row['Responsable']} | **Hora de registro:**"
              f" {row['Timestamp']}"
          )
          st.markdown(f"**Handover:**\n> {row['Handover']}")