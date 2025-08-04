import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            .stButton>button {
                background-color: #007bff;
                color: white;
                padding: 0.5em 1em;
                border-radius: 8px;
                border: none;
            }
            .stTextInput>div>input {
                padding: 0.5em;
                border-radius: 6px;
            }
            .stFileUploader>div>input {
                padding: 0.5em;
                border-radius: 6px;
            }
        </style>
    """, unsafe_allow_html=True)
