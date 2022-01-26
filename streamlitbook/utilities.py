"""
A module that contains utility functions.
"""

import base64
import re
from PIL import Image
import io

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go


def _create_white_bg(image_string: str):
    """
    Take a base64 encoded image, convert it to bytes and
    create a white background image with the same shape as the image.

    Parameters
    ----------
    image_string: str
        base64 encoded string of an image

    Returns
    -------
        White background image with the same shape as input image.
    """
    # Convert to bytes code from the image base64 string
    bytes_image = base64.decodebytes(str.encode(image_string))

    # Create a temporary image from the bytes
    temp_image = Image.open(io.BytesIO(bytes_image))
    width, height = temp_image.width, temp_image.height

    white_image_array = 255 * np.ones((height, width, 3), np.uint8)
    white_pil_image = Image.fromarray(white_image_array)

    return white_pil_image


def _display_image(image_string: str):
    """
    Convert base64 encoded images to bytes and display as streamlit media.

    Parameters
    ----------
    image_string: str :
        base64 encoded string of an image.

    """
    # Convert to bytes code from the image base64 string
    bytes_image = base64.decodebytes(str.encode(image_string))

    # Generate a white background image
    pil_image_white = _create_white_bg(image_string)
    # Convert the original bytes image to PIL image
    pil_image_colored = Image.open(io.BytesIO(bytes_image))
    # Paste the original bytes image on the white background image
    pil_image_white.paste(pil_image_colored, (0, 0))

    # Display the final image with streamlit
    st.image(pil_image_white, use_column_width='always')


def _display_dataframe(html_df: str):
    """
    Static, lower-level method to retrieve a DataFrame from HTML code
    that gets rendered under the hood of a Jupyter Cell.

    Parameters
    ----------
    html_df: str :
        Raw HTML code that contains <table> tag.
    """

    df = pd.read_html(html_df)[0]
    df.rename(lambda x: "" if "Unnamed:" in x else x, axis='columns', inplace=True)
    st.dataframe(df.set_index(df.columns[0]))
