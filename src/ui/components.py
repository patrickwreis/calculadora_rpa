# -*- coding: utf-8 -*-
"""Reusable UI components (using pure Streamlit only)"""
import streamlit as st


def page_header(title: str, subtitle: str = ""):
    """Display page header with title and optional subtitle."""
    st.title(title)
    if subtitle:
        st.markdown(subtitle)
    
