
import streamlit as st
import os
def apply_global_style():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    css_file_path = os.path.join(project_root, 'styles', 'main.css')
    if os.path.exists(css_file_path):
        with open(css_file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
