# -*- coding: utf-8 -*-
"""Form builder utilities for better UI/UX"""
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards


def create_form_section(title: str, description: str = None):
    """Create a styled form section"""
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown("## 📋")
    with col2:
        st.markdown(f"### {title}")
        if description:
            st.markdown(f"*{description}*")
    st.divider()


def create_metric_card(label: str, value: str, icon: str = "📊", color: str = "blue"):
    """Create a styled metric card"""
    color_map = {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "red": "#d62728",
        "orange": "#ff7f0e",
        "purple": "#9467bd",
    }
    
    bg_color = color_map.get(color, color)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {bg_color} 0%, {bg_color}88 100%); 
                padding: 20px; border-radius: 10px; color: white;'>
        <p style='margin: 0; font-size: 14px; opacity: 0.9;'>{icon} {label}</p>
        <p style='margin: 10px 0 0 0; font-size: 28px; font-weight: bold;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)
