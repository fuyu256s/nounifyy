import random
from io import BytesIO
from pathlib import Path
from typing import IO

import face_recognition
import numpy as np
import requests
import streamlit as st
from PIL import Image
from stqdm import stqdm
from utils import st_dl_gif, st_dl_png


def main() -> None:
    file = st.file_uploader("Upload a file", type=['png', 'jpg', 'gif'])
    url = st.text_input("or enter a URL")

    if url:
        r = requests.get(url)
        file = BytesIO(r.content)
        file.name = ""

    if file is not None:
        im = Image.open(file)
        if im.format == 'GIF':
            ims, durations = nounifyy_gif(im)
            st_dl_gif(ims, durations, "output", 'dl_nnfgif')
        else:
            im = nounifyy(im)
            st.image(im)
            stem = "" if url else "".join(file.name.split(".")[:-1])
            st_dl_png(im, "nounified_" + stem, 'dl_nnf')
    else:
        st.divider()
        st.write("Go to other tools:")
        pages = ['drawnounifyy', 'images2gif', 'svg2png', 'tileimages']
        cols = st.columns(len(pages))
        for col, page in zip(cols, pages):
            with col:
                if st.button(page, use_container_width=True):
                    st.switch_page(f"pages/{page}.py")
        st.write("<- check the sidebar for page switching and tool controls")


def nounifyy(im: Image) -> Image:
    d_noggles = {
        x.stem.replace("glasses-", "").replace("square-", ""): x
        for x in Path("4-glasses").glob("*.png")
    }

    arr = np.array(_reduce_im_size(im.convert('RGB')))
    face_landmarks_list = face_recognition.face_landmarks(arr)
    n = len(face_landmarks_list)

    init = {
        'size': 1.25,
        'x': 0.0,
        'y': 0.0,
    }
    angles = {}

    if face_landmarks_list:
        newim = Image.fromarray(arr)
        for i, face_landmarks in enumerate(face_landmarks_list):
            st.sidebar.subheader(f"⌐◨-◨ {i + 1}")

            place, noggle = _get_noggle_place(
                i,
                face_landmarks,
                d_noggles,
                init,
                angles,
            )
            if place:
                newim.paste(noggle, box=(place), mask=noggle)

        st.sidebar.button(
            "Random ⌐◨-◨",
            on_click=_random,
            args=(n,),
            use_container_width=True,
        )
        st.sidebar.button(
            "Reset",
            on_click=_reset,
            args=(n, init, angles),
            use_container_width=True,
        )

    else:
        st.warning("Face not recognized", icon="ℹ️")
        newim = Image.fromarray(arr)

    return newim


def _reduce_im_size(im: Image.Image) -> Image.Image:
    TH = 4096
    w, h = im.size
    if w > TH and h > TH:
        if w > h:
            new_w = TH
            new_h = int(new_w * h / w)
        elif h > w:
            new_h = TH
            new_w = int(new_h * w / h)
        else:
            new_w, new_h = TH, TH
    elif w > TH:
        new_w = TH
        new_h = int(new_w * h / w)
    elif h > TH:
        new_h = TH
        new_w = int(new_h * w / h)
    else:
        new_w, new_h = w, h
    return im.resize((new_w, new_h))


def _get_noggle_place(
    i: int, face_landmarks: dict, d_noggles: dict, init: dict, angles: dict
) -> (tuple[int, int], Image):
    d = {"random": random.choice(list(d_noggles.values()))} | d_noggles

    le = np.mean(np.array(face_landmarks['left_eye']), axis=0).astype(int)
    re = np.mean(np.array(face_landmarks['right_eye']), axis=0).astype(int)
    v = le - re
    angles[i] = np.degrees(np.arctan2(v[0], v[1])) + 90
    st_angle = st.sidebar.slider("angle", -180.0, 180.0, angles[i], key=f"angle_{i}")
    st_size = st.sidebar.slider("size", 0.5, 5.0, value=init['size'], key=f"size_{i}")
    st_x = st.sidebar.slider("x", -1.0, 1.0, value=init['x'], key=f"x_{i}")
    st_y = st.sidebar.slider("y", -1.0, 1.0, value=init['y'], key=f"y_{i}")

    factor = np.linalg.norm(v) / 7 * st_size
    if factor.astype(int) == 0:
        return None, None
    center = (np.array((16.5, 13.5)) - np.array((st_x, st_y)) * 3) * factor
    place = tuple((np.mean([le, re], axis=0) - center).astype(int))

    st_type = st.sidebar.selectbox("type", d.keys(), key=f"type_{i}")
    noggle = Image.open(d[st_type])
    noggle = noggle.resize(
        (np.array(noggle.size) * factor).astype(int), Image.NEAREST
    ).rotate(st_angle, Image.BICUBIC, center=tuple(center.astype(int)))

    return place, noggle


def nounifyy_gif(im: Image) -> Image:
    d_noggles = {
        x.stem.replace("glasses-", "").replace("square-", ""): x
        for x in Path("4-glasses").glob("*.png")
    }
    d = {"random": random.choice(list(d_noggles.values()))} | d_noggles
    st_type = st.sidebar.selectbox("type", d.keys(), key=f"type_gif")
    p_noggles = d[st_type]

    flag, durations, ims = [], [], []
    for i in stqdm(range(im.n_frames)):
        im.seek(i)
        durations.append(im.info['duration'])

        arr = np.array(_reduce_im_size(im.convert('RGB')))
        face_landmarks_list = face_recognition.face_landmarks(arr)

        init = {
            'size': 1.25,
            'x': 0.0,
            'y': 0.0,
        }

        if face_landmarks_list:
            newim = Image.fromarray(arr)
            for i, face_landmarks in enumerate(face_landmarks_list):
                place, noggle = _get_noggle_place_gif(
                    i, face_landmarks, p_noggles, init
                )
                if place:
                    newim.paste(noggle, box=(place), mask=noggle)
            flag.append(True)
        else:
            newim = Image.fromarray(arr)
            flag.append(False)
        ims.append(newim.convert('P'))

    st.warning(f"Face recognized: {sum(flag)}/{im.n_frames} frames")
    return ims, durations


def _get_noggle_place_gif(
    i: int, face_landmarks: dict, p_noggles: str, init: dict
) -> (tuple[int, int], Image):

    le = np.mean(np.array(face_landmarks['left_eye']), axis=0).astype(int)
    re = np.mean(np.array(face_landmarks['right_eye']), axis=0).astype(int)
    v = le - re
    angle = np.degrees(np.arctan2(v[0], v[1])) + 90
    x, y, size = init['x'], init['y'], init['size']

    factor = np.linalg.norm(v) / 7 * size
    if factor.astype(int) == 0:
        return None, None
    center = (np.array((16.5, 13.5)) - np.array((x, y)) * 3) * factor
    place = tuple((np.mean([le, re], axis=0) - center).astype(int))

    noggle = Image.open(p_noggles)
    noggle = noggle.resize(
        (np.array(noggle.size) * factor).astype(int), Image.NEAREST
    ).rotate(angle, Image.BICUBIC, center=tuple(center.astype(int)))

    return place, noggle


def _random(n: int) -> None:
    for i in range(n):
        st.session_state[f"type_{i}"] = 'random'


def _reset(n: int, init: dict, angles: dict) -> None:
    for i in range(n):
        st.session_state[f"size_{i}"] = init['size']
        st.session_state[f"x_{i}"] = init['x']
        st.session_state[f"y_{i}"] = init['y']
        st.session_state[f"angle_{i}"] = angles[i]


if __name__ == "__main__":
    st.set_page_config(
        page_title="Nounifyy",
        page_icon="👾",
    )
    st.title("Nounifyy ⌐◨-◨!")
    st.markdown("For meme! Put ⌐◨-◨! Play with images easily!")
    st.caption("Recognize faces and place ⌐◨-◨. prototype.")

    main()
