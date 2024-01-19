import base64
from io import BytesIO

import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="images2gif",
    page_icon="👾",
)
st.title("images2gif")
st.caption("Create gif from images.")

upld = st.file_uploader("Upload files", type=['png', 'jpg'], accept_multiple_files=True)
if upld is not None:
    ims = [Image.open(file) for file in upld]
    if ims:
        st_duration = st.sidebar.number_input("duration", value=200)
        buf = BytesIO()
        ims[0].save(
            buf,
            format='gif',
            save_all=True,
            append_images=ims[1:],
            optimize=False,
            duration=st_duration,
            loop=0,
        )
        byte_im = buf.getvalue()

        data_url = base64.b64encode(byte_im).decode('utf-8')
        st.markdown(
            f"<img src='data:image/gif;base64,{data_url}' alt='gif'>",
            unsafe_allow_html=True,
        )

        st.download_button(
            label="Download",
            data=byte_im,
            file_name=f"out.gif",
            mime='image/gif',
            key='dl2',
        )
