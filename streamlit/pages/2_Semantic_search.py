import streamlit as st
from functions import async_request, init_state_var
import time
from os import getenv
from dotenv import load_dotenv

st.set_page_config(
    page_title="Nymble AI Semantic Search",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
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

load_dotenv()
timeout = 2
url = getenv("url_semantic_search")


def show_results(r):
    st.session_state.results = r.get("descriptions")
    st.session_state.links = r.get("links")
    st.session_state.last_page = r.get("lastpage")


def request_data(page=1):
    st.session_state.results = []
    st.session_state.links = []
    if st.session_state.query:
        payload = {"query": st.session_state.query, "page": page}
        async_request(
            "get",
            url + "/search",
            json=payload,
            callback=lambda r: show_results(r.json()),
        )
        for seconds in range(timeout):
            with spinner.container():
                with st.spinner(text="please wait"):
                    time.sleep(1)
                    if len(st.session_state.results) > 0:
                        st.empty()
                        break
                if seconds == timeout - 1:
                    st.error("something went wrong :(")
    else:
        st.error("please enter prompt")


def nextpage():
    st.session_state.page += 1
    st.empty()
    request_data(st.session_state.page)


def prevpage():
    if st.session_state.page > 1:
        st.session_state.page -= 1
        st.empty()
    request_data(st.session_state.page)


st.markdown(
    '<div style="text-align: center;color:#A472FB;font-size:60px;vertical-align:top;">Nymble AI</div>',
    unsafe_allow_html=True,
)

init_state_var("results", [])
init_state_var("links", [])
init_state_var("page", 1)
init_state_var("last_page", True)


prompt_input = st.text_input(
    placeholder="Enter your search request in natural language here",
    label=" search request",
    key="query",
    label_visibility="hidden",
)

searchtbtn = st.button("Search", type="primary")

spinner = st.empty()
content = st.empty()
nav = st.empty()


if searchtbtn:
    st.session_state.page = 1
    request_data(page=1)

a, b, c = st.columns(3)
with a:
    if st.session_state.page > 1:
        pb = st.button("Previous")
        if pb:
            prevpage()
            st.experimental_rerun()
with b:
    if len(st.session_state.get("results")) > 0:
        if not st.session_state.last_page:
            st.text(f"Page{st.session_state.page}")
        else:
            st.text(f"Last Page")

with c:
    if not st.session_state.last_page:
        nb = st.button("Next")
        if nb:
            nextpage()
            st.experimental_rerun()
with content.container():
    if len(st.session_state.get("results")) > 0:
        for result, link in zip(st.session_state.results, st.session_state.links):
            loc = result.split("\n")[-1]
            result = result[: len(result) - len(loc)][:300]
            st.markdown(
                f'<div style="font-size:20px;vertical-align:top;">{result}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-size:20px;color:#5799BB;vertical-align:top;">{loc}</div>',
                unsafe_allow_html=True,
            )
            if link != " ":
                st.write(f"[{link[:50]}...]({link})")
            st.text(" ")
            st.text(" ")


    else:
        content.empty()
