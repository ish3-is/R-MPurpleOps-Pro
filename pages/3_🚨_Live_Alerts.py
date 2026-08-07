import streamlit as st
import pandas as pd
from utils import CUSTOM_CSS, get_recent_alerts

st.set_page_config(page_title="Live Alerts", page_icon="🚨", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("🚨 Live Alerts")
st.markdown("Real-time security alerts from Wazuh SIEM.")

minutes = st.slider("Time Range (minutes)", 5, 60, 30, 5)
recent_alerts = get_recent_alerts(minutes=minutes)

if recent_alerts:
    st.success(f"✅ Found {len(recent_alerts)} alerts in the last {minutes} minutes")
    
    for hit in recent_alerts[:20]:
        source = hit['_source']
        rule = source.get('rule', {})
        agent = source.get('agent', {})
        level = rule.get('level', 0)
        
        if level >= 10: severity, color = "CRITICAL", "#ef4444"
        elif level >= 7: severity, color = "HIGH", "#f97316"
        elif level >= 4: severity, color = "MEDIUM", "#eab308"
        else: severity, color = "LOW", "#22c55e"
        
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.5); padding: 12px; margin: 5px 0; border-radius: 6px; border-left: 4px solid {color};'>
            <strong style='color: #f1f5f9;'>{source.get('timestamp', 'N/A')[:19]}</strong> | 
            Rule <strong>{rule.get('id', 'N/A')}</strong> | 
            Level <strong>{level}</strong> | 
            <span style='color: {color}; font-weight: 600;'>{severity}</span> |
            {rule.get('description', 'N/A')[:80]}...
            <br><small style='color: #64748b;'>Agent: {agent.get('name', 'N/A')}</small>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(f"No alerts in the last {minutes} minutes")