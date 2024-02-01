import streamlit as st
from PIL import Image
from utils import st_dl_gif


def main() -> None:
    files = st.file_uploader(
        "Upload files", type=['png', 'jpg'], accept_multiple_files=True
    )
    if files is not None:
        ims = [Image.open(file) for file in files]
        if ims:
            st_duration = st.number_input("duration (ms)", value=200)
            st_dl_gif(ims, st_duration, "output", 'dl_tilegif')


if __name__ == "__main__":
    st.set_page_config(
        page_title="images2gif",
        page_icon="👾",
    )
    st.title("images2gif")
    st.caption("Create gif from images.")

    main()
