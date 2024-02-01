import base64
from io import BytesIO

import streamlit as st
from PIL import Image


def st_dl_png(im: Image.Image, stem: str, key=str, label: str = "Download") -> None:
    buf = BytesIO()
    im.save(buf, format='png')
    byte_im = buf.getvalue()

    st.download_button(
        label=label,
        data=byte_im,
        file_name=f"{stem}.png",
        mime='image/png',
        key=key,
    )


def st_dl_gif(
    ims: list[Image.Image],
    duration: float,
    stem: str,
    key=str,
    label: str = "Download",
    show_gif: bool = True,
) -> None:
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

    if show_gif:
        data_url = base64.b64encode(byte_im).decode('utf-8')
        st.markdown(
            f"<img src='data:image/gif;base64,{data_url}' alt='gif'>",
            unsafe_allow_html=True,
        )

    st.download_button(
        label=label,
        data=byte_im,
        file_name=f"{stem}.gif",
        mime='image/gif',
        key=key,
    )
