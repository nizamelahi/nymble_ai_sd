import streamlit as st
from functions import async_request,init_state_var
import time
from os import getenv
from dotenv import load_dotenv
st.set_page_config(layout="wide")

load_dotenv()
timeout = 2
url=getenv('url_semantic_search')

def show_results(r):
   st.session_state.results=r.get("descriptions")
   st.session_state.links=r.get("links")

st.markdown('<div style="text-align: center;color:#A472FB;font-size:60px;vertical-align:top;">Nymble AI</div>', unsafe_allow_html=True)

init_state_var("results", [])
init_state_var("links", [])

prompt_input = st.text_input(
    placeholder="Enter your search request in natural language here",
    label=" search request",
    key="query",
    label_visibility="hidden",
)

generatebutton = st.button("Search",type="primary")

placeholder = st.empty()

if generatebutton:
    st.session_state.results=[]
    st.session_state.links=[]
    if st.session_state.query:
        payload = {
            "query": st.session_state.query,
        }
        async_request(
            "get",
            url + "/search",
            json=payload,
            callback=lambda r: show_results(r.json()),
        )
        for seconds in range(timeout):
            with placeholder.container():
                with st.spinner(text="please wait"):
                    time.sleep(1)
                    if len(st.session_state.results) > 0:
                        break
    else:
        st.error("please enter prompt")

with placeholder.container():
    if len(st.session_state.get("results")) > 0:
        for result,link in zip(st.session_state.results,st.session_state.links):

            st.markdown(f'<div style="font-size:20px;vertical-align:top;">{result}</div>', unsafe_allow_html=True)
            st.write(f"[{link}]({link})")
            st.text(" ")
            st.text(" ")
            
    else:
        st.empty()