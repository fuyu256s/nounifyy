import base64
import random
from io import BytesIO

import numpy as np
import streamlit as st
from PIL import Image


def main() -> None:
    files = st.file_uploader(
        "Upload files", type=['png', 'jpg'], accept_multiple_files=True
    )
    sw = st.radio(
        "tile_or_tilegif",
        ["just tile", "tile to random gif"],
        horizontal=True,
        label_visibility='collapsed',
    )

    if files:
        # def init
        w, h = Image.open(files[0]).size
        W_ = 160
        if w > W_:
            h = W_ * h // w
            w = W_
        st_cellw = st.sidebar.number_input("cell width", value=w, min_value=1)
        st_cellh = st.sidebar.number_input("cell height", value=h, min_value=1)

        if sw == "just tile":
            ncols = np.sqrt(len(files)).astype(int) if len(files) > 1 else 1
            st_ncols = st.number_input("number of columns", value=ncols, min_value=1)
            st_rand = st.checkbox("Shuffle")
            if st_rand:
                random.shuffle(files)

        elif sw == "tile to random gif":
            col1, col2 = st.columns(2)
            with col1:
                st_ncols = st.number_input("number of columns", value=4, min_value=1)
            with col2:
                st_nrows = st.number_input("number of rows", value=4, min_value=1)
            st_nrepeat = st.number_input("repeat", value=10, min_value=1)
            st_duration = st.sidebar.number_input("duration", value=200)

    if st.button("Go", use_container_width=True):
        if not files:
            return

        ims = [
            np.array(
                Image.open(f)
                .resize((st_cellw, st_cellh), Image.NEAREST)
                .convert('RGBA')
            )
            for f in files
        ]

        if sw == "just tile":
            arr = np.stack(ims)
            im = Image.fromarray(_tile(arr, st_ncols))
            st.image(im)

        elif sw == "tile to random gif":
            _ims = []
            for i in range(st_nrepeat):
                arr = np.stack(random.choices(ims, k=st_ncols * st_nrows))
                im = Image.fromarray(_tile(arr, st_ncols))
                _ims.append(im)

            buf = BytesIO()
            _ims[0].save(
                buf,
                format='gif',
                save_all=True,
                append_images=_ims[1:],
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
                key='dl_tilegif',
            )


def _tile(ims_arr: np.ndarray, ncols: int):
    batch, h, w, ch = ims_arr.shape
    n = ncols * (batch // ncols + np.sign(batch % ncols))
    nrows = n // ncols

    pad_arr = np.zeros((n - batch, h, w, ch), ims_arr.dtype)
    a = np.concatenate([ims_arr, pad_arr], axis=0)
    a = a.reshape(nrows, ncols, h, w, ch).transpose([0, 2, 1, 3, 4])
    a = a.reshape(h * nrows, w * ncols, ch)
    return a


if __name__ == "__main__":
    st.set_page_config(
        page_title="tileimages",
        page_icon="👾",
    )
    st.title("tileimages")
    st.caption("tile images and make it a gif")

    main()
