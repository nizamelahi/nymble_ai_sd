import streamlit as st
from functions import async_request, init_state_var
import time
from os import getenv
from dotenv import load_dotenv
import pandas as pd
import requests

st.set_page_config(
    page_title="Nymble AI Job Recommendation Engine",
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
timeout = 20
url = getenv("url_semantic_search")
def load_results():
    st.session_state.results = (
        st.session_state.all_data["description"]
        .head(num_results * st.session_state.page)
        .tail(num_results)
        .tolist()
    )
    st.session_state.links = (
        st.session_state.all_data["links"]
        .head(num_results * st.session_state.page)
        .tail(num_results)
        .tolist()
    )


def show_results(r):
    st.session_state.all_data = pd.DataFrame(
        r.get("output"), columns=["links", "description", "count"]
    )
    st.session_state.all_data = st.session_state.all_data.sort_values(
        "count", ascending=False
    )
    st.session_state.results = (
        st.session_state.all_data["description"].head(num_results).tolist()
    )
    st.session_state.links = (
        st.session_state.all_data["links"].head(num_results).tolist()
    )
    st.session_state.pages = len(st.session_state.all_data) / num_results
    if (len(st.session_state.all_data) % num_results) == 0:
        st.session_state.last_page_num = st.session_state.pages
    else:
        st.session_state.last_page_num = st.session_state.pages + 1


def get_recommendations():
    st.session_state.results = []
    st.session_state.all_data=[]
    if st.session_state.infile:
        async_request(
            "get",
            url + "/job_recommendations",
            files={"file":st.session_state.infile},
            callback=lambda r: show_results(r.json()),
        )
        for seconds in range(timeout):
            with content.container():
                time.sleep(1)
                if len(st.session_state.results) > 0:
                    break
                else:
                    try:
                        prog = requests.get(
                            url + "/progress", timeout=5
                        ).json()
                        st.progress(float(prog.get("progress")), text="Processing resume,please wait...")

                    except:
                        break
                if seconds == timeout - 1:
                    st.error("something went wrong :(")
    else:
        st.error("please upload a file")


def nextpage():
    st.session_state.page += 1
    st.empty()
    load_results()


def prevpage():
    if st.session_state.page > 1:
        st.session_state.page -= 1
        st.empty()
    load_results()
    


st.markdown(
    '<div style="text-align: center;color:#A472FB;font-size:60px;vertical-align:top;">Nymble AI</div>',
    unsafe_allow_html=True,
)

init_state_var("results", [])
init_state_var("links", [])
# init_state_var("all_data", [])
init_state_var("page", 1)
init_state_var("pages", 1)
init_state_var("last_page_num", 1)
num_results = 15

st.file_uploader(
    "Upload your resume here", type="pdf", accept_multiple_files=False, key="infile"
)

searchtbtn = st.button("Search", type="primary")

loader = st.empty()
content = st.empty()
nav = st.empty()


if searchtbtn:
    st.session_state.page = 1
    get_recommendations()

a, b, c = st.columns(3)
with a:
    if st.session_state.page > 1:
        pb = st.button("Previous")
        if pb:
            prevpage()
            st.experimental_rerun()
with b:
    if len(st.session_state.get("results")) > 0:
        if st.session_state.page != st.session_state.last_page_num:
            st.text(f"Page{st.session_state.page}")
        else:
            st.text(f"Last Page")

with c:
    if st.session_state.page != st.session_state.last_page_num:
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
