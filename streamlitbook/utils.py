"""
A module that contains utility functions.
"""

from . import StreamlitBook

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
