import streamlit as st
import time
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from utils import CUSTOM_CSS, ATTACKS_DB, execute_ssh, search_alerts, send_scan_summary, send_telegram_message

st.set_page_config(page_title="Attack Simulation", page_icon="🎯", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("🎯 Attack Simulation")
st.markdown("Execute MITRE ATT&CK techniques and validate SOC detection capabilities.")

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    run_full = st.button("🚀 Run Full Scan", use_container_width=True)
with col2:
    selected_attack = st.selectbox("Select Single Attack", options=list(ATTACKS_DB.keys()), format_func=lambda x: f"{x} - {ATTACKS_DB[x]['name']}")
with col3:
    run_single = st.button("▶️ Run", use_container_width=True)

progress_bar = st.progress(0)
status_text = st.empty()

if run_full:
    results = []
    total = len(ATTACKS_DB)
    for idx, (attack_id, attack) in enumerate(ATTACKS_DB.items()):
        status_text.markdown(f"<div class='alert-box'>🔄 <strong>Testing:</strong> {attack_id} - {attack['name']}</div>", unsafe_allow_html=True)
        execute_ssh(attack['command'])
        time.sleep(12)
        hits = search_alerts(attack_id, minutes=5, rule_id=attack['expected_rule'])
        detected = len(hits) > 0
        results.append({'id': attack_id, 'name': attack['name'], 'tactic': attack['tactic'], 'risk': attack['risk'], 'detected': detected, 'alerts': len(hits), 'rule': attack['expected_rule'], 'description': attack['description']})
        progress_bar.progress((idx + 1) / total)
    
    status_text.markdown("<div class='alert-box' style='border-color: #22c55e;'>✅ <strong>Full scan completed!</strong></div>", unsafe_allow_html=True)
    detected_count = sum(1 for r in results if r['detected'])
    coverage = (detected_count / len(results) * 100)
    st.session_state['results'] = results
    st.session_state['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_scan_summary(results, coverage, st.session_state['scan_time'])

elif run_single:
    attack = ATTACKS_DB[selected_attack]
    status_text.markdown(f"<div class='alert-box'>🔄 <strong>Testing:</strong> {selected_attack} - {attack['name']}</div>", unsafe_allow_html=True)
    execute_ssh(attack['command'])
    time.sleep(12)
    hits = search_alerts(selected_attack, minutes=5, rule_id=attack['expected_rule'])
    detected = len(hits) > 0
    results = [{'id': selected_attack, 'name': attack['name'], 'tactic': attack['tactic'], 'risk': attack['risk'], 'detected': detected, 'alerts': len(hits), 'rule': attack['expected_rule'], 'description': attack['description']}]
    status_text.markdown("<div class='alert-box' style='border-color: #22c55e;'>✅ <strong>Test completed!</strong></div>", unsafe_allow_html=True)
    st.session_state['results'] = results
    st.session_state['scan_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📊 Assessment Results")
    
    detected_count = sum(1 for r in results if r['detected'])
    total_count = len(results)
    coverage = (detected_count / total_count * 100) if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        color = '#22c55e' if coverage >= 80 else '#eab308' if coverage >= 60 else '#ef4444'
        st.markdown(f"<div class='metric-card' style='text-align: center;'><div style='color: #94a3b8;'>OVERALL COVERAGE</div><div style='font-size: 3rem; font-weight: 800; color: {color};'>{coverage:.1f}%</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card' style='text-align: center;'><div style='color: #94a3b8;'>DETECTED</div><div style='font-size: 3rem; font-weight: 800; color: #22c55e;'>{detected_count}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card' style='text-align: center;'><div style='color: #94a3b8;'>MISSED</div><div style='font-size: 3rem; font-weight: 800; color: #ef4444;'>{total_count - detected_count}</div></div>", unsafe_allow_html=True)
    
    for result in results:
        status_icon = "✅" if result['detected'] else "❌"
        with st.expander(f"{status_icon} **{result['id']}** - {result['name']} | Risk: {result['risk']}", expanded=False):
            st.markdown(f"**MITRE ID:** {result['id']} | **Rule ID:** {result['rule']} | **Tactic:** {result['tactic']}")
            st.markdown(f"**Status:** {'DETECTED' if result['detected'] else 'NOT DETECTED'} | **Alerts:** {result['alerts']}")
            st.markdown(f"**Description:** {result['description']}")