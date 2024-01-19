import random
from io import BytesIO
from pathlib import Path
from typing import IO, Union

import face_recognition
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw

st.set_page_config(
    page_title="Nounifyy",
    page_icon="👾",
)
st.title("Nounifyy ⌐◨-◨!")
st.markdown("For meme! Put ⌐◨-◨! Play with images easily!")
st.caption("Recognize faces and place ⌐◨-◨. prototype.")


def nounifyy(file: Union[IO, Path]) -> Image:
    p = [x for x in Path("4-glasses").glob("*.png")]
    im = face_recognition.load_image_file(file)
    # st.image(im, output_format='png')
    face_landmarks_list = face_recognition.face_landmarks(im)

    if face_landmarks_list:
        newim = Image.fromarray(im)
        for i, face_landmarks in enumerate(face_landmarks_list):
            le = np.average(np.array(face_landmarks['left_eye']), axis=0).astype(int)
            re = np.average(np.array(face_landmarks['right_eye']), axis=0).astype(int)
            # d = ImageDraw.Draw(newim, 'RGBA')
            # d.line([tuple(le), tuple(re)], width=10)

            st.sidebar.subheader(f"⌐◨-◨ {i + 1}")
            d = {x.stem.replace("glasses-", "").replace("square-", ""): x for x in p}
            d = {"random": random.choice(p)} | d

            st_type = st.sidebar.selectbox("type", d.keys(), key=f"type_{i}")
            st_size = st.sidebar.slider("size", 0.5, 5.0, value=1.25, key=f"size_{i}")

            factor = np.linalg.norm(le - re) / 7 * st_size
            center = np.array((16, 13)) * factor
            place = tuple((np.mean([le, re], axis=0) - center).astype(int))
            v = le - re
            angle = np.degrees(np.arctan2(v[0], v[1])) + 90
            st_angle = st.sidebar.slider(
                "angle", -180.0, 180.0, angle, key=f"angle_{i}"
            )

            noggle = Image.open(d[st_type])
            noggle = noggle.resize(
                (np.array(noggle.size) * factor).astype(int), Image.NEAREST
            ).rotate(st_angle, Image.BICUBIC, center=tuple(center.astype(int)))
            newim.paste(noggle, box=(place), mask=noggle)

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
