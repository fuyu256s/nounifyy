import base64
import random
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas


def main() -> None:
    file = st.file_uploader("Upload a file", type=['png', 'jpg'])
    im = Image.open(file) if file is not None else None
    canvas_result = _canvas(im)

    d_noggles = {
        x.stem.replace("glasses-", "").replace("square-", ""): x
        for x in Path("4-glasses").glob("*.png")
    }

    if canvas_result.image_data is not None:
        draw = Image.fromarray(canvas_result.image_data.astype('uint8'), mode='RGBA')
        if file is not None:
            newim = im.resize(draw.size)
        else:
            newim = Image.new('RGBA', draw.size)

        for i, obj in enumerate(canvas_result.json_data['objects']):
            st.sidebar.subheader(f"⌐◨-◨ {i + 1}")

            place, noggle = _get_noggle_place(i, obj, d_noggles)
            newim.paste(noggle, box=(place), mask=noggle)

        st.image(newim)

        st.sidebar.button(
            "Random ⌐◨-◨",
            on_click=_random,
            args=(len(canvas_result.image_data),),
            use_container_width=True,
        )


def _canvas(im: None | Image.Image) -> 'CanvasResult':
    w_canvas = st.sidebar.number_input("canvas width", value=512)
    h_canvas = int(w_canvas * im.size[1] / im.size[0]) if im else w_canvas // 2

    mode = st.sidebar.radio(
        "mode",
        ["line", "transform"],
        format_func=lambda x: {"line": "draw", "transform": "move"}.get(x),
        horizontal=True,
    )
    col1, col2 = st.sidebar.columns([5, 1])
    with col1:
        stroke_width = st.slider("stroke", 1, 25, 5)
    with col2:
        stroke_color = st.color_picker(
            "color", value="#ffe939", label_visibility='collapsed'
        )

    canvas_result = st_canvas(
        fill_color="#eee",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#0000",
        background_image=im if im else None,
        update_streamlit=True,
        height=h_canvas,
        width=w_canvas,
        drawing_mode=mode,
        display_toolbar=True,
        key="canvas1" if im else "canvas0",
    )
    return canvas_result


def _get_noggle_place(i: int, obj: dict, d_noggles: dict):
    d = {"random": random.choice(list(d_noggles.values()))} | d_noggles
    st_type = st.sidebar.selectbox("type", d.keys(), key=f"type_{i}")

    le, re = np.array((obj['x1'], obj['y1'])), np.array((obj['x2'], obj['y2']))
    v = le - re
    angle = np.degrees(np.arctan2(v[0], v[1])) + 90
    factor = np.linalg.norm(v) / 7
    center = np.array((16.5, 13.5)) * factor
    place = tuple((np.array((obj['left'], obj['top'])) - center).astype(int))

    noggle = Image.open(d[st_type])
    noggle = noggle.resize(
        (np.array(noggle.size) * factor).astype(int), Image.NEAREST
    ).rotate(angle, Image.BICUBIC, center=tuple(center))

    return place, noggle


def _random(n: int) -> None:
    for i in range(n):
        st.session_state[f"type_{i}"] = 'random'


if __name__ == "__main__":
    st.set_page_config(
        page_title="NounifyyDraw",
        page_icon="👾",
    )
    st.title("Draw and Nounifyy")
    with st.expander("Draw lines and place ⌐◨-◨."):
        with open('pages/demo.gif', 'rb') as f:
            data_url = base64.b64encode(f.read()).decode('utf-8')
            st.markdown(
                f"<img src='data:image/gif;base64,{data_url}' alt='gif'>",
                unsafe_allow_html=True,
            )

    main()