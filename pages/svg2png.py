import re
from io import BytesIO

import cairosvg
import requests
import streamlit as st
from PIL import Image
from utils import st_dl_png


def main() -> None:
    file = st.file_uploader("Upload a file", type=['svg'])
    url = st.text_input("or enter a URL")

    if url:
        r = requests.get(url)
        file = BytesIO(r.content)
        name = re.search(r'(?<=").*(?=")', r.headers.get('ETag')).group()
        file.name = f"{name}.svg"

    if file is not None:
        png = cairosvg.svg2png(file_obj=file)
        im = Image.open(BytesIO(png))
        w, h = im.size

        st_w = st.sidebar.number_input("width", value=w)
        st_h = st.sidebar.number_input("height", value=h)

        im = im.resize((st_w, st_h), Image.NEAREST)
        st.image(im, output_format='png')

        stem = "".join(file.name.split(".")[:-1])
        st_dl_png(im, stem, "dl_svg2png")


if __name__ == "__main__":
    st.set_page_config(
        page_title="svg2png",
        page_icon="👾",
    )
    st.title("svg2png")
    st.caption("Convert svg to png.")

    main()
