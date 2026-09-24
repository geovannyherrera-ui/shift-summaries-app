import datetime
import os
import pandas as pd
import streamlit as st
from supabase import create_client

# Conectar cliente con Secrets de Streamlit
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lista de supervisores
SUPERVISORS = [
    "Elena Zbar",
    "David Mazzantini",
    "Huiyan Sun",
    "Ari Chen",
    "Garcia liu",
    "Lynne Huang",
    "Olha Dehtiar",
    "Jonathan MENES",
    "John Rafael BELLO",
    "John Carl De Gracia",
    "Nhel Flores",
    "Martin Evans BANGIS",
    "Robert III Flores",
    "Hazel Ann Aguilar",
    "Mark Anthony Desabayla",
    "Darren Josh Suniga",
    "Guardian Jasen",
    "Geovanny Sebastian Herrera Claudio",
    "Lizbeth Jazmin Chinchilla Colon",
    "Elsy Nikol Garcia Martinez",
    "Pavan A",
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

OFFLINE_REASONS = [
    "None",
    "Coaching",
    "Team meetings",
    "Training",
    "1-on-1 Session",
    "System / Tech Issues",
    "All-Hands / Town Hall",
    "Special Project / Administrative",
    "Other (Specify in Handover)",
]


def load_data():
    """Consulta todas las filas de la tabla 'shift_data' en Supabase."""
    try:
        response = supabase.table("shift_data").select("*").execute()
        data = response.data
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(
                columns=[
                    "Timestamp",
                    "Supervisor",
                    "LOB",
                    "Hub",
                    "Checklist_Items",
                    "Tech_Issues",
                    "Bluebook",
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
    except Exception as e:
        st.error(f"Error cargando datos de Supabase: {e}")
        return pd.DataFrame()


def save_data(new_record):
    """Inserta un nuevo registro en la tabla 'shift_data' de Supabase."""
    try:
        supabase.table("shift_data").insert(new_record).execute()
    except Exception as e:
        st.error(f"Error guardando registro en Supabase: {e}")


st.set_page_config(
    page_title="Shift Summaries & Handovers Hub", page_icon="📋", layout="wide"
)

# Initialize Session State for Important Notes
if "important_notes" not in st.session_state:
    st.session_state["important_notes"] = []

st.title("📋 Shift Summaries & Daily Handovers Hub")

tab1, tab2, tab3 = st.tabs(
    ["➕ Submit Shift Summary", "📊 Historical Records", "🚨 Today's Handovers"]
)

# --- TAB 1: SUBMIT FORM ---
with tab1:
    st.header("Shift Summary Submission Form")

    # Multi-select Supervisor Dropdown
    sup_choices = st.multiselect(
        "Supervisor Name(s)",
        SUPERVISORS,
        placeholder="Select one or more supervisors...",
    )

    other_sup = ""
    if "Other (Type below)" in sup_choices:
        other_sup = st.text_input("Enter additional supervisor full name(s)")

    st.divider()

    st.subheader("Line of Business (LOB)")
    lob = st.radio(
        "Select which summary are you filling out",
        ["KYC", "Customer Care"],
        key="lob_selector",
    )

    st.divider()

    with st.form("shift_summary_form", clear_on_submit=True):
        st.subheader("Hub Location")
        if lob == "KYC":
            hub = st.selectbox("Hub", HUBS_KYC, key="hub_kyc")
        else:
            hub = st.selectbox("Hub", HUBS_CC, key="hub_cc")

        st.divider()

        st.subheader("Daily Checklist")
        checklist_selected = []

        if lob == "KYC":
            c1 = st.checkbox("Attendance", key="c_kyc_1")
            c2 = st.checkbox("KYC Briefing", key="c_kyc_2")
            c3 = st.checkbox("Unassign over 8 hour tickets", key="c_kyc_3")
            c4 = st.checkbox(
                "Marked all absentees on Shift Organizer", key="c_kyc_4"
            )
            c5 = st.checkbox("Handled KYC - Supervisor tickets", key="c_kyc_5")

            for name, val in [
                ("Attendance", c1),
                ("KYC Briefing", c2),
                ("Unassign over 8 hour tickets", c3),
                ("Marked all absentees on Shift Organizer", c4),
                ("Handled KYC - Supervisor tickets", c5),
            ]:
                if val:
                    checklist_selected.append(name)
        else:
            c1 = st.checkbox("Attendance", key="c_cc_1")
            c2 = st.checkbox("Test the lines", key="c_cc_2")
            c3 = st.checkbox("CC Briefing", key="c_cc_3")
            c4 = st.checkbox("Sending IPH and SLA reports", key="c_cc_4")
            c5 = st.checkbox(
                "Marked all absentees on Shift Organizer", key="c_cc_5"
            )
            c6 = st.checkbox("G3 Checklist", key="c_cc_6")
            c7 = st.checkbox("Review of agent skills", key="c_cc_7")

            for name, val in [
                ("Attendance", c1),
                ("Test the lines", c2),
                ("CC Briefing", c3),
                ("Sending IPH and SLA reports", c4),
                ("Marked absentees on Shift Organizer", c5),
                ("G3 Checklist", c6),
                ("Review of agent skills", c7),
            ]:
                if val:
                    checklist_selected.append(name)

        st.divider()

        st.subheader("Shift Metrics & Details")

        tech_issues = st.text_area(
            "Tech Issues",
            placeholder="Describe any technical issues encountered...",
        )

        is_bluebook = st.checkbox(
            "🚨 Was a Bluebook / PagerDuty incident created?"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            scheduled_reps = st.number_input(
                "Scheduled Reps", min_value=0, value=0, step=1
            )
        with col_b:
            actual_reps = st.number_input(
                "Actual Reps", min_value=0, value=0, step=1
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
            offline_reason = st.selectbox(
                "Reason for the offline time",
                options=OFFLINE_REASONS,
                index=0,
            )

        st.divider()

        st.subheader("Handover & Points to Note")
        handover_text = st.text_area(
            "Shift Handover / Key Highlights / Important Notes",
            placeholder=(
                "Write the handover details, key highlights, and things for"
                " the incoming shift to note here..."
            ),
            height=180,
        )

        submitted = st.form_submit_button("Submit Shift Summary")

        if submitted:
            # Consolidate supervisor selections
            selected_sups = [
                s for s in sup_choices if s != "Other (Type below)"
            ]
            if other_sup.strip():
                selected_sups.append(other_sup.strip())

            supervisor_string = ", ".join(selected_sups)

            if not selected_sups:
                st.error("Please select or enter at least one Supervisor name.")
            elif handover_text.strip() == "":
                st.error("The Handover / Points to Note field is mandatory.")
            else:
                # Resta matemática para ausencias reales
                calculated_absentees = max(0, int(scheduled_reps) - int(actual_reps))

                record_date = str(datetime.date.today())
                new_record = {
                    "Timestamp": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Supervisor": supervisor_string,
                    "LOB": lob,
                    "Hub": hub,
                    "Checklist_Items": ", ".join(checklist_selected),
                    "Tech_Issues": tech_issues,
                    "Bluebook": "Yes" if is_bluebook else "No",
                    "Scheduled_Reps": scheduled_reps,
                    "Actual_Reps": actual_reps,
                    "Absentees_Number": calculated_absentees,
                    "Absentees_Names": "None",
                    "Offline_Hours": offline_hours,
                    "Offline_Reason": offline_reason,
                    "Handover": handover_text,
                    "DateOnly": record_date,
                }
                save_data(new_record)
                st.success(
                    f"✅ Shift Summary successfully submitted! ({calculated_absentees}"
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
            mask = (
                df_historial.astype(str)
                .apply(
                    lambda x: x.str.contains(
                        search_query, case=False, na=False
                    )
                )
                .any(axis=1)
            )
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
    # Header & Button Row
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.header("🚨 Today's Shift Handovers")
    with col_btn:
        st.write("")  # Alignment spacing
        with st.popover("➕ Add an important note", use_container_width=True):
            st.subheader("Add Important Note")
            new_note = st.text_area(
                "Write note for everyone to see:",
                placeholder=(
                    "Type urgent announcements or critical notices here..."
                ),
            )
            if st.button("Save Note", use_container_width=True):
                if new_note.strip():
                    st.session_state["important_notes"].append(new_note.strip())
                    st.rerun()
                else:
                    st.warning("Note cannot be empty.")

    # --- SECTION: Important Things to Notice ---
    if st.session_state["important_notes"]:
        st.markdown("### 🔔 Important Things to Notice")
        for idx, note in enumerate(st.session_state["important_notes"]):
            with st.container():
                st.warning(f"**NOTICE:** {note}")
                if st.button(
                    f"❌ Dismiss Note #{idx + 1}", key=f"del_note_{idx}"
                ):
                    st.session_state["important_notes"].pop(idx)
                    st.rerun()
        st.divider()

    # --- TODAY'S HANDOVERS LIST ---
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
                    # Fila 1: Datos Generales
                    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
                    with col_h1:
                        st.markdown(f"**LOB:** {row.get('LOB', 'N/A')}")
                    with col_h2:
                        st.markdown(f"**Hub:** {row.get('Hub', 'N/A')}")
                    with col_h3:
                        st.markdown(
                            f"**Supervisor(s):** {row.get('Supervisor', 'N/A')}"
                        )
                    with col_h4:
                        st.markdown(
                            f"**Time:** {row.get('Timestamp', 'N/A')}"
                        )

                    st.divider()

                    # Fila 2: Indicadores Rápidos
                    col_m1, col_m2 = st.columns(2)

                    with col_m1:
                        try:
                            sched = int(row.get("Scheduled_Reps", 0))
                            actual = int(row.get("Actual_Reps", 0))
                        except (ValueError, TypeError):
                            sched, actual = 0, 0

                        if sched > 0:
                            attendance_pct = (actual / sched) * 100
                            st.markdown(
                                f"👥 **Attendance:** {actual}/{sched} reps"
                                f" ({attendance_pct:.1f}%)"
                            )
                        else:
                            st.markdown(
                                f"👥 **Attendance:** {actual}/{sched} reps"
                                " (N/A)"
                            )

                    with col_m2:
                        tech_text = str(row.get("Tech_Issues", "")).strip()
                        bluebook_status = str(row.get("Bluebook", "No")).strip()

                        if tech_text and tech_text.lower() != "nan":
                            if bluebook_status == "Yes":
                                st.markdown(
                                    "🚨 **Tech Issues:** Yes (Bluebook /"
                                    " PagerDuty)"
                                )
                            else:
                                st.markdown("⚠️ **Tech Issues:** Yes")
                        else:
                            if bluebook_status == "Yes":
                                st.markdown(
                                    "🚨 **Bluebook / PagerDuty:** Yes"
                                )
                            else:
                                st.markdown("✅ **Tech Issues:** None")

                    # Handover Notes
                    st.markdown("**Handover & Notes:**")
                    handover_val = str(row.get("Handover", "")).strip()
                    st.info(
                        handover_val
                        if handover_val != "" and handover_val.lower() != "nan"
                        else "No additional notes provided."
                    )

                    with st.expander("View full shift details and checklist"):
                        st.write(
                            "**Checklist Completed:**"
                            f" {row.get('Checklist_Items', 'N/A')}"
                        )
                        st.write(
                            "**Tech Issues Details:**"
                            f" {row.get('Tech_Issues', 'None')}"
                        )
                        st.write(
                            "**Bluebook Incident:**"
                            f" {row.get('Bluebook', 'No')}"
                        )
                        st.write(
                            "**Reps (Sched / Act):**"
                            f" {row.get('Scheduled_Reps', 0)} /"
                            f" {row.get('Actual_Reps', 0)}"
                        )
                        st.write(
                            "**Absentees Total:**"
                            f" {row.get('Absentees_Number', 0)}"
                        )
                        st.write(
                            "**Offline Time:**"
                            f" {row.get('Offline_Hours', 0)} hrs (Reason:"
                            f" {row.get('Offline_Reason', 'N/A')})"
                        )
