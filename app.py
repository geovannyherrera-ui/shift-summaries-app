import datetime
import os
import pandas as pd
import streamlit as st

# CSV file acting as our database
DB_FILE = "shift_data_v2.csv"

SUPERVISORS = [
    "Select Supervisor",
    "John Doe",
    "Jane Smith",
    "Carlos Pérez",
    "Maria Gonzalez",
    "Alex Chen",
    "Other (Type below)",
]

HUBS_KYC = [
    "Guatemala",
    "New York",
    "Israel",
    "Philippines",
    "China",
    "Romania",
    "India",
]
HUBS_CC = ["Guatemala", "New York", "Israel", "Philippines", "China", "Poland"]


def load_data():
  if os.path.exists(DB_FILE):
    return pd.read_csv(DB_FILE)
  else:
    return pd.DataFrame(
        columns=[
            "Timestamp",
            "Supervisor",
            "LOB",
            "Hub",
            "Checklist_Items",
            "Tech_Issues",
            "Scheduled_Reps",
            "Actual_Reps",
            "Absentees_Number",
            "Absentees_Names",
            "Offline_Hours",
            "Offline_Reason",
            "Handover",
            "DateOnly",
        ]
    )


def save_data(new_record):
  df = load_data()
  df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
  df.to_csv(DB_FILE, index=False)


st.set_page_config(
    page_title="Shift Summaries & Handovers Hub", page_icon="📋", layout="wide"
)

st.title("📋 Shift Summaries & Daily Handovers Hub")

tab1, tab2, tab3 = st.tabs(
    ["➕ Submit Shift Summary", "📊 Historical Records", "🚨 Today's Handovers"]
)

# --- TAB 1: SUBMIT FORM ---
with tab1:
  st.header("Shift Summary Submission Form")

  with st.form("shift_summary_form", clear_on_submit=True):
    # Supervisor Identification
    st.subheader("Supervisor Details")
    sup_choice = st.selectbox("Supervisor Name", SUPERVISORS)
    supervisor_name = sup_choice
    if sup_choice == "Other (Type below)":
      supervisor_name = st.text_input("Enter your full name")

    st.divider()

    # 1. LOB Selection
    st.subheader("Line of Business (LOB)")
    lob = st.radio(
        "Select which summary are you filling out", ["KYC", "Customer Care"]
    )

    st.divider()

    # 2. Hub Selection
    st.subheader("Hub Location")
    if lob == "KYC":
      hub = st.selectbox("Hub", HUBS_KYC)
    else:
      hub = st.selectbox("Hub", HUBS_CC)

    st.divider()

    # 3. Daily Checklist
    st.subheader("Daily Checklist")
    checklist_selected = []

    if lob == "KYC":
      c1 = st.checkbox("Attendance")
      c2 = st.checkbox("KYC Briefing")
      c3 = st.checkbox("Unassign over 8 hour tickets")
      c4 = st.checkbox("Marked all absentees on Shift Organizer")
      c5 = st.checkbox("Handled KYC - Supervisor tickets")
      for name, val in [
          ("Attendance", c1),
          ("KYC Briefing", c2),
          ("Unassign tickets", c3),
          ("Marked absentees on Organizer", c4),
          ("Handled KYC - Supervisor tickets", c5),
      ]:
        if val:
          checklist_selected.append(name)
    else:
      c1 = st.checkbox("Attendance")
      c2 = st.checkbox("Test the lines")
      c3 = st.checkbox("CC Briefing")
      c4 = st.checkbox("Sending IPH and SLA reports")
      c5 = st.checkbox("Marked all absentees on Shift Organizer")
      c6 = st.checkbox("G3 Checklist")
      c7 = st.checkbox("Review of agent skills")
      for name, val in [
          ("Attendance", c1),
          ("Test the lines", c2),
          ("CC Briefing", c3),
          ("Sending IPH and SLA reports", c4),
          ("Marked absentees on Organizer", c5),
          ("G3 Checklist", c6),
          ("Review of agent skills", c7)
      ]:
        if val:
          checklist_selected.append(name)

    st.divider()

    # Operational metrics and details (Points to note removed/unifed)
    st.subheader("Shift Metrics & Details")

    tech_issues = st.text_area(
        "Tech Issues", placeholder="Describe any technical issues encountered..."
    )

    col_a, col_b = st.columns(2)
    with col_a:
      scheduled_reps = st.number_input(
          "Scheduled Reps", min_value=0, value=0, step=1
      )
    with col_b:
      actual_reps = st.number_input("Actual Reps", min_value=0, value=0, step=1)

    # Simplified Absentees Section
    st.markdown("**Absentees Management**")
    absentees_names = st.text_input(
        "Names of the absentees (Type names separated by commas)",
        placeholder="e.g., John Smith, Anna Davis",
    )

    col_d, col_e = st.columns(2)
    with col_d:
      offline_hours = st.number_input(
          "Offline Time (Number in hours)",
          min_value=0.0,
          value=0.0,
          step=0.5,
      )
    with col_e:
      offline_reason = st.text_input(
          "Reason for the offline time", placeholder="Brief description..."
      )

    st.divider()

    # Unified Handover & Points to Note field
    st.subheader("Handover & Points to Note")
    handover_text = st.text_area(
        "Shift Handover / Key Highlights / Important Notes",
        placeholder=(
            "Write the handover details, key highlights, and things for the"
            " incoming shift to note here..."
        ),
        height=180,
    )

    submitted = st.form_submit_button("Submit Shift Summary")

    if submitted:
      if supervisor_name == "Select Supervisor" or supervisor_name.strip() == "":
        st.error("Please select or enter a valid Supervisor name.")
      elif handover_text.strip() == "":
        st.error("The Handover / Points to Note field is mandatory.")
      else:
        if absentees_names.strip() == "":
          absentees_num = 0
          absentees_list_clean = "None"
        else:
          names_list = [n.strip() for n in absentees_names.split(",") if n.strip()]
          absentees_num = len(names_list)
          absentees_list_clean = ", ".join(names_list)

        record_date = str(datetime.date.today())
        new_record = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Supervisor": supervisor_name,
            "LOB": lob,
            "Hub": hub,
            "Checklist_Items": ", ".join(checklist_selected),
            "Tech_Issues": tech_issues,
            "Scheduled_Reps": scheduled_reps,
            "Actual_Reps": actual_reps,
            "Absentees_Number": absentees_num,
            "Absentees_Names": absentees_list_clean,
            "Offline_Hours": offline_hours,
            "Offline_Reason": offline_reason,
            "Handover": handover_text,
            "DateOnly": record_date,
        }
        save_data(new_record)
        st.success(
            f"✅ Shift Summary successfully submitted! ({absentees_num}"
            " absentee(s) registered automatically)."
        )

# --- TAB 2: HISTORICAL RECORDS ---
with tab2:
  st.header("Historical Records Database")
  df_historial = load_data()

  if df_historial.empty:
    st.info("No records available yet.")
  else:
    search_query = st.text_input(
        "🔍 Search across all records (Supervisor, Hub, LOB, Text...)"
    )
    if search_query:
      mask = df_historial.astype(str).apply(
          lambda x: x.str.contains(search_query, case=False, na=False)
      ).any(axis=1)
      df_historial = df_historial[mask]

    st.dataframe(df_historial, use_container_width=True)

    csv_data = df_historial.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Database as CSV",
        data=csv_data,
        file_name="shift_summaries_master.csv",
        mime="text/csv",
    )

# --- TAB 3: TODAY'S HANDOVERS ---
with tab3:
  st.header("🚨 Today's Shift Handovers")
  df_today = load_data()

  if df_today.empty:
    st.info("No records available.")
  else:
    today_str = str(datetime.date.today())

    if "DateOnly" in df_today.columns:
      handovers_hoy = df_today[df_today["DateOnly"] == today_str]
    else:
      df_today["Timestamp_Date"] = pd.to_datetime(
          df_today["Timestamp"]
      ).dt.strftime("%Y-%m-%d")
      handovers_hoy = df_today[df_today["Timestamp_Date"] == today_str]

    if handovers_hoy.empty:
      st.warning(
          f"No handovers have been registered for today yet ({today_str})."
      )
    else:
      st.success(
          f"Showing all handovers submitted today ({today_str}):"
          f" {len(handovers_hoy)} report(s) found."
      )

      for index, row in handovers_hoy.iterrows():
        with st.container(border=True):
          col_h1, col_h2, col_h3, col_h4 = st.columns(4)
          with col_h1:
            st.markdown(f"**LOB:** {row['LOB']}")
          with col_h2:
            st.markdown(f"**Hub:** {row['Hub']}")
          with col_h3:
            st.markdown(f"**Supervisor:** {row['Supervisor']}")
          with col_h4:
            st.markdown(f"**Time:** {row['Timestamp']}")

          st.markdown(f"**Handover & Notes:**")
          st.info(row["Handover"])

          with st.expander("View full shift details and checklist"):
            st.write(f"**Checklist Completed:** {row['Checklist_Items']}")
            st.write(f"**Tech Issues:** {row['Tech_Issues']}")
            st.write(
                f"**Reps (Sched / Act):** {row['Scheduled_Reps']} /"
                f" {row['Actual_Reps']}"
            )
            st.write(
                f"**Absentees Total:** {row['Absentees_Number']} (Names:"
                f" {row['Absentees_Names']})"
            )
            st.write(
                f"**Offline Time:** {row['Offline_Hours']} hrs (Reason:"
                f" {row['Offline_Reason']})"
            )
