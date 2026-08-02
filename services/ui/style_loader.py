import os 
import streamlit as st
import base64 # to convert binary text to normal data

def load_css(file_path):
    if os.path.exists(file_path): # CSS
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True) # apply CSS



def inject_local_font(font_path,font_name): # 
    if not os.path.exists(font_path):
        return

    with open(font_path,"rb") as f: # rb=> read binary
        encoded = base64.b64encode(f.read()).decode() # convert to python string

    ext = os.path.splitext(font_path)[1].lstrip(".") # extracts extension of file and remove . from extension 
    if ext == "otf":
        fmt = "opentype"
    else:
        fmt = ext  

    if ext == "otf":
        mime = "font/otf"
    else:
        mime = f"font/{ext}"

    st.markdown(f"""
        <style>
        @font-face{{
            font-family : '{font_name}';
            src: url('data:{mime};base64,{encoded}') format('{fmt}');
            font-weight: 100 900;
            font-style:normal;
        }}
        </style>
    """,unsafe_allow_html=True)