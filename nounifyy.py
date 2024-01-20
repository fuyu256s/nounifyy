import random
from io import BytesIO
from pathlib import Path
from typing import IO, Union

import face_recognition
import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Nounifyy",
    page_icon="👾",
)
st.title("Nounifyy ⌐◨-◨!")
st.markdown("For meme! Put ⌐◨-◨! Play with images easily!")
st.caption("Recognize faces and place ⌐◨-◨. prototype.")


def nounifyy(file: Union[IO, Path]) -> Image:
    p_noggles = list(Path("4-glasses").glob("*.png"))
    d_noggles = {
        x.stem.replace("glasses-", "").replace("square-", ""): x for x in p_noggles
    }

    im = face_recognition.load_image_file(file)
    face_landmarks_list = face_recognition.face_landmarks(im)
    n = len(face_landmarks_list)

    init = {
        'size': 1.25,
        'x': 0.0,
        'y': 0.0,
    }
    angles = {}

    if face_landmarks_list:
        newim = Image.fromarray(im)
        for i, face_landmarks in enumerate(face_landmarks_list):
            st.sidebar.subheader(f"⌐◨-◨ {i + 1}")

            d = {"random": random.choice(p_noggles)} | d_noggles
            st_type = st.sidebar.selectbox("type", d.keys(), key=f"type_{i}")

            le = np.mean(np.array(face_landmarks['left_eye']), axis=0).astype(int)
            re = np.mean(np.array(face_landmarks['right_eye']), axis=0).astype(int)
            v = le - re
            angles[i] = np.degrees(np.arctan2(v[0], v[1])) + 90
            st_angle = st.sidebar.slider(
                "angle", -180.0, 180.0, angles[i], key=f"angle_{i}"
            )
            st_size = st.sidebar.slider(
                "size", 0.5, 5.0, value=init['size'], key=f"size_{i}"
            )
            st_x = st.sidebar.slider("x", -1.0, 1.0, value=init['x'], key=f"x_{i}")
            st_y = st.sidebar.slider("y", -1.0, 1.0, value=init['y'], key=f"y_{i}")

            factor = np.linalg.norm(v) / 7 * st_size
            center = (np.array((16, 13)) - np.array((st_x, st_y)) * 2) * factor
            place = tuple((np.mean([le, re], axis=0) - center).astype(int))

            noggle = Image.open(d[st_type])
            noggle = noggle.resize(
                (np.array(noggle.size) * factor).astype(int), Image.NEAREST
            ).rotate(st_angle, Image.BICUBIC, center=tuple(center.astype(int)))

            newim.paste(noggle, box=(place), mask=noggle)

        def reset(n: int, size: float, x: float, y: float, angles: dict) -> None:
            for i in range(n):
                st.session_state[f"size_{i}"] = init['size']
                st.session_state[f"x_{i}"] = init['x']
                st.session_state[f"y_{i}"] = init['y']
                st.session_state[f"angle_{i}"] = angles[i]

        st.sidebar.button(
            "Reset",
            on_click=reset,
            args=(n, init['size'], init['x'], init['y'], angles),
            use_container_width=True,
        )

    else:
        st.write("Face not recognized")
        newim = Image.fromarray(im)

    return newim


def main():
    upld = st.file_uploader("Upload a file", type=['png', 'jpg'])
    if upld is not None:
        im = nounifyy(upld)
        st.image(im)

        buf = BytesIO()
        im.save(buf, format='png')
        byte_im = buf.getvalue()
        stem = "".join(upld.name.split(".")[:-1])
        st.download_button(
            label="Download",
            data=byte_im,
            file_name=f"{stem}.png",
            mime='image/png',
            key='dl0',
        )


main()
