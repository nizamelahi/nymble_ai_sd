import requests
import io
import base64
from PIL import Image, PngImagePlugin
from threading import Thread
from requests import get, post, put, patch, delete, options, head
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import time

request_methods = {
    "get": get,
    "post": post,
    "put": put,
    "patch": patch,
    "delete": delete,
    "options": options,
    "head": head,
}

url = "http://127.0.0.1:7861"
timeout = 180


if "images" not in st.session_state:
    st.session_state["images"] = []


def init_state_var(var, val):
    if not st.session_state.get(var):
        st.session_state[var] = val


init_state_var("steps", 25)
init_state_var("seed", -1)
init_state_var("numimgs", 4)
init_state_var("images",[])
init_state_var("info",[])




def async_request(method, *args, callback=None, timeout=180, **kwargs):
    """Makes request on a different thread, and optionally passes response to a
    `callback` function when request returns.
    """
    method = request_methods[method.lower()]
    if callback:

        def callback_with_args(response, *args, **kwargs):
            callback(response)

        kwargs["hooks"] = {"response": callback_with_args}
    kwargs["timeout"] = timeout
    thread = Thread(target=method, args=args, kwargs=kwargs)
    add_script_run_ctx(thread)
    thread.start()


def show_images(r):
    if r.get("images"):
        for i in r["images"]:
            infopayload = {"image": "data:image/png;base64," + i}
            response2 = requests.post(url=f"{url}/sdapi/v1/png-info", json=infopayload)
            st.session_state.info.append(response2.json().get("info").split(",")[3])
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            st.session_state.images.append(image)

st.markdown('<div style="text-align: center;color:#DC901D;font-size:60px;vertical-align:top;">Nymble AI</div>', unsafe_allow_html=True)
st.sidebar.subheader("Enter a prompt to generate images")
prompt_input = st.sidebar.text_input(
    placeholder="describe your desired image here",
    label="Prompt",
    key="prompt_text",
    label_visibility="visible",
)
negative_prompt = st.sidebar.text_input(
    placeholder="stuff you dont want",
    label="Negative Prompt",
    key="negative_prompt",
    label_visibility="visible",
)
st.sidebar.text(" ")
st.sidebar.text(" ")

with st.sidebar.expander("advanced options"):
    steps = st.number_input(
        label="steps",
        key="steps",
        value=st.session_state.steps,
        help="higher steps mean a more detailed image but at the cost of generation time",
    )
    seed = st.number_input(
        label="seed",
        key="seed",
        value=st.session_state.seed,
        help="use the seed from a desired image to fine tune the results with the prompt and steps. Leave at -1 to generate random images",
    )
    if seed > -1:
        st.session_state.numimgs = 1
    numimgs = st.number_input(
        label="number of images", key="numimgs", value=st.session_state.numimgs
    )
    

    generatebutton = st.sidebar.button("Generate images",type="primary")
placeholder = st.empty()

if generatebutton:
    if st.session_state.prompt_text:
        st.session_state.images = []
        st.session_state.info = []
        payload = {
            "prompt": st.session_state.prompt_text,
            "negative_prompt": st.session_state.negative_prompt,
            "steps": st.session_state.steps,
            "batch_size": st.session_state.numimgs,
            "seed": st.session_state.seed,
        }
        busy = requests.get(url + "/sdapi/v1/progress", timeout=2).json()
        if int(busy.get("eta_relative")) > 0:
            requests.post(url + "/sdapi/v1/interrupt", timeout=2).json()
            with st.spinner(text="please wait"):
                time.sleep(3)
        async_request(
            "post",
            url + "/sdapi/v1/txt2img",
            json=payload,
            callback=lambda r: show_images(r.json()),
        )
        for seconds in range(timeout):
            time.sleep(1)
            with placeholder.container():
                if len(st.session_state.images) > 0:
                    break
                else:
                    try:
                        prog = requests.get(
                            url + "/sdapi/v1/progress", timeout=2
                        ).json()
                        if float(prog.get("progress")) > 0:
                            eta = f"about {int(prog.get('eta_relative'))} seconds remaining"
                            st.progress(float(prog.get("progress")), text=eta)

                    except:
                        break
    else:
        st.error("please enter prompt")

with placeholder.container():
    if len(st.session_state.get("images")) > 0:
        st.image(
            st.session_state.images,
            caption=st.session_state.info,
            use_column_width=False,
        )
        st.empty()
    else:
        st.markdown('<div style="text-align: center;font-size:18px;vertical-align:top;">Custom trained text to image generator</div>', unsafe_allow_html=True)
        

# # body={{
# #   "enable_hr": false,
# #   "denoising_strength": 0,
# #   "firstphase_width": 0,
# #   "firstphase_height": 0,
# #   "hr_scale": 2,
# #   "hr_upscaler": "string",
# #   "hr_second_pass_steps": 0,
# #   "hr_resize_x": 0,
# #   "hr_resize_y": 0,
# #   "hr_sampler_name": "string",
# #   "hr_prompt": "",
# #   "hr_negative_prompt": "",
# #   "prompt": "",
# #   "styles": [
# #     "string"
# #   ],
# #   "seed": -1,
# #   "subseed": -1,
# #   "subseed_strength": 0,
# #   "seed_resize_from_h": -1,
# #   "seed_resize_from_w": -1,
# #   "sampler_name": "string",
# #   "batch_size": 1,
# #   "n_iter": 1,
# #   "steps": 50,
# #   "cfg_scale": 7,
# #   "width": 512,
# #   "height": 512,
# #   "restore_faces": false,
# #   "tiling": false,
# #   "do_not_save_samples": false,
# #   "do_not_save_grid": false,
# #   "negative_prompt": "string",
# #   "eta": 0,
# #   "s_min_uncond": 0,
# #   "s_churn": 0,
# #   "s_tmax": 0,
# #   "s_tmin": 0,
# #   "s_noise": 1,
# #   "override_settings": {},
# #   "override_settings_restore_afterwards": true,
# #   "script_args": [],
# #   "sampler_index": "Euler",
# #   "script_name": "string",
# #   "send_images": true,
# #   "save_images": false,
# #   "alwayson_scripts": {}
# # }}
