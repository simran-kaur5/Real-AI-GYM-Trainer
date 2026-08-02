import streamlit as st
from streamlit_webrtc import webrtc_streamer

st.title("WebRTC Test")

webrtc_streamer(
    key="test",
    rtc_configuration={
        "iceServers": [
            {
                "urls": [
                    "stun:stun.l.google.com:19302"
                ]
            }
        ]
    }
)