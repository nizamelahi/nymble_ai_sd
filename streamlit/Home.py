import streamlit as st

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown(
    '<div style="text-align: center;color:#A472FB;font-size:65px;vertical-align:top;">Welcome to NymbleApps AI Demo Suite </div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div style="text-align: center;font-size:20px  ;vertical-align:top;">Please select a demo from the sidebar to experience what Nymble AI can do for you</div>',
    unsafe_allow_html=True,
)
