import base64
from io import BytesIO

import numpy as np
import cairosvg
import face_recognition
import streamlit as st
from PIL import Image, ImageDraw

st.title("Nounifyy ⌐◨-◨!")
st.markdown("For meme! Put ⌐◨-◨! Play with images easily!")
st.caption("in prototype, only works in anticipated situations.")

tab1, tab2, tab3 = st.tabs(["nounifyy", "svg2png", "images2gif"])

with tab1:
    upld = st.file_uploader("Choose a file", type=['png', 'jpg'])
    if upld is not None:
        im = face_recognition.load_image_file(upld)
        st.image(im, output_format='png')

        face_landmarks_list = face_recognition.face_landmarks(im)

        newim = Image.fromarray(im)
        for face_landmarks in face_landmarks_list:
            d = ImageDraw.Draw(newim, 'RGBA')

            le = np.average(np.array(face_landmarks['left_eye']), axis=0).astype(int)
            re = np.average(np.array(face_landmarks['right_eye']), axis=0).astype(int)
            # d.line([tuple(le), tuple(re)], width=10)

            noggle = Image.open('4-glasses/glasses-square-red.png')

            adjust = st.slider("⌐◨-◨ size adjustment", float(0), float(5), value=1.3)
            factor = np.linalg.norm(le - re) / 7 * adjust

            place = tuple(
                (np.mean([le, re], axis=0) - np.array((16, 13)) * factor).astype(int))
            # st.write(factor, place)
            noggle = noggle.resize(
                    (np.array(noggle.size) * factor).astype(int),
                    Image.NEAREST)
            newim.paste(noggle, box=(place), mask=noggle)

        st.image(newim)

        buf = BytesIO()
        newim.save(buf, format='png')
        byte_im = buf.getvalue()
        st.download_button(
            label="Download image",
            data=byte_im,
            file_name=f"out.png",
            mime='image/png',
            key='0',
        )


with tab2:
    upld = st.file_uploader("Choose a file", type=['svg'])
    if upld is not None:
        png = cairosvg.svg2png(file_obj=upld)
        im = Image.open(BytesIO(png))

        w = st.number_input("width", value=256)
        h = st.number_input("height", value=256)

        im = im.resize((w, h), Image.NEAREST)
        st.image(im, output_format='png')

        buf = BytesIO()
        im.save(buf, format='png')
        byte_im = buf.getvalue()

        st.download_button(
            label="Download image",
            data=byte_im,
            file_name=f"out.png",
            mime='image/png',
            key='1',
        )


with tab3:
    upld = st.file_uploader(
        "Choose file", type=['png', 'jpg'], accept_multiple_files=True
    )
    if upld is not None:
        ims = [Image.open(file) for file in upld]
        if ims:
            duration = st.number_input("duration", value=200)
            buf = BytesIO()
            ims[0].save(
                buf,
                format='gif',
                save_all=True,
                append_images=ims[1:],
                optimize=False,
                duration=duration,
                loop=0,
            )
            byte_im = buf.getvalue()

            data_url = base64.b64encode(byte_im).decode('utf-8')
            st.markdown(
                f"<img src='data:image/gif;base64,{data_url}' alt='gif'>",
                unsafe_allow_html=True,
            )

            st.download_button(
                label="Download image",
                data=byte_im,
                file_name=f"out.gif",
                mime='image/gif',
                key='2',
            )
