import random

import numpy as np
import streamlit as st
from PIL import Image
from utils import st_dl_gif, st_dl_png


def main() -> None:
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []
    files = st.file_uploader(
        "Upload files",
        type=['png', 'jpg'],
        accept_multiple_files=True,
        key=st.session_state["file_uploader_key"],
    )
    if files:
        st.session_state["uploaded_files"] = files
    if st.button("Clear"):
        st.session_state["file_uploader_key"] += 1
        st.rerun()

    st_sw = st.radio(
        "tile_or_tilegif",
        ["just tile", "tile to random gif"],
        horizontal=True,
        label_visibility='collapsed',
    )

    if files:
        # def init
        if st_sw == "just tile":
            st_tilemode = st.radio(
                "tilehow",
                ["in order", "shuffle", "random"],
                horizontal=True,
                label_visibility='collapsed',
            )

            ncols = np.sqrt(len(files)).astype(int) if len(files) > 1 else 1
            tileall = st_tilemode in ["in order", "shuffle"]

            col1, col2 = st.columns(2)
            with col1:
                st_ncols = st.number_input(
                    "number of columns",
                    value=ncols,
                    min_value=1,
                    max_value=len(files) if tileall else None,
                )
            with col2:
                n = ncols * (len(files) // ncols + np.sign(len(files) % ncols))
                st_nrows = n // st_ncols or 1

                st_nrows = st.number_input(
                    "number of rows",
                    value=st_nrows,
                    min_value=1,
                    disabled=True if tileall else False,
                )

        elif st_sw == "tile to random gif":
            col1, col2 = st.columns(2)
            with col1:
                st_ncols = st.number_input("number of columns", value=4, min_value=1)
            with col2:
                st_nrows = st.number_input("number of rows", value=4, min_value=1)
            st_nrepeat = st.number_input("repeat", value=10, min_value=1)
            st_duration = st.number_input("duration (ms)", value=200)

        w, h = Image.open(files[0]).size

        MAX_W = 160
        if w > MAX_W:
            h = MAX_W * h // w
            w = MAX_W

        TH = 4096
        ww = w * st_ncols
        hh = h * st_nrows
        if ww > TH and hh > TH:
            if ww > TH:
                _w = TH // st_ncols
                h = _w * h // w
                w = _w
            else:
                _h = TH // st_nrows
                w = _h * w // h
                h = _h
        elif ww > TH:
            _w = TH // st_ncols
            h = _w * h // w
            w = _w
        elif hh > TH:
            _h = TH // st_nrows
            w = _h * w // h
            h = _h

        st_cellw = st.sidebar.number_input("cell width", value=w, min_value=1)
        st_cellh = st.sidebar.number_input("cell height", value=h, min_value=1)

        if st_cellw * st_ncols >= TH:
            st.warning("reduce cell width or number of columns")
            return
        elif st_cellh * st_nrows >= TH:
            st.warning("reduce cell height or number of rows")
            return

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
        st_n = st_ncols * st_nrows

        if st_sw == "just tile":
            if st_tilemode == "in order":
                arr = np.stack(ims)
            elif st_tilemode == "shuffle":
                random.shuffle(ims)
                arr = np.stack(ims)
            elif st_tilemode == "random":
                arr = np.stack(random.choices(ims, k=st_n))
            im = Image.fromarray(_tile(arr, st_ncols))
            st.image(im)
            st_dl_png(im, "output", "dl_tilepng")

        elif st_sw == "tile to random gif":
            _ims = []
            for _ in range(st_nrepeat):
                arr = np.stack(random.choices(ims, k=st_n))
                im = Image.fromarray(_tile(arr, st_ncols))
                _ims.append(im)

            st_dl_gif(_ims, st_duration, "output", "dl_tilegif")


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
