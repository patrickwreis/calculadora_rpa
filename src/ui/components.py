# -*- coding: utf-8 -*-
"""Reusable UI components"""
import streamlit as st
from typing import Callable, Optional


def input_form(fields: dict, on_submit: Callable):
    """Create an input form with multiple fields"""
    with st.form("input_form"):
        values = {}
        for field_name, field_config in fields.items():
            field_type = field_config.get("type", "text")
            label = field_config.get("label", field_name)
            placeholder = field_config.get("placeholder", "")
            min_value = field_config.get("min", 0)
            max_value = field_config.get("max", 100)
            
            if field_type == "text":
                values[field_name] = st.text_input(label, placeholder=placeholder)
            elif field_type == "number":
                values[field_name] = st.number_input(
                    label, 
                    min_value=min_value, 
                    max_value=max_value,
                    value=0.0
                )
            elif field_type == "slider":
                values[field_name] = st.slider(label, min_value, max_value)
        
        if st.form_submit_button("Calcular"):
            on_submit(values)


def result_table(data: dict, title: str = "Resultados"):
    """Display results in a formatted table"""
    st.subheader(title)
    cols = st.columns(len(data))
    for idx, (key, value) in enumerate(data.items()):
        with cols[idx]:
            st.metric(key, value)


def header(title: str, subtitle: str = ""):
    """Display page header"""
    st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.divider()
