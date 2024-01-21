from io import BytesIO

import cairosvg
import streamlit as st
from PIL import Image


def main() -> None:
    file = st.file_uploader("Upload a file", type=['svg'])
    if file is not None:
        png = cairosvg.svg2png(file_obj=file)
        im = Image.open(BytesIO(png))
        w, h = im.size

        st_w = st.sidebar.number_input("width", value=w)
        st_h = st.sidebar.number_input("height", value=h)

        im = im.resize((st_w, st_h), Image.NEAREST)
        st.image(im, output_format='png')

        buf = BytesIO()
        im.save(buf, format='png')
        byte_im = buf.getvalue()

        stem = "".join(file.name.split(".")[:-1])
        st.download_button(
            label="Download",
            data=byte_im,
            file_name=f"{stem}.png",
            mime='image/png',
            key='dl_sv2png',
        )


if __name__ == "__main__":
    st.set_page_config(
        page_title="svg2png",
        page_icon="👾",
    )
    st.title("svg2png")
    st.caption("Convert svg to png.")

    main()
