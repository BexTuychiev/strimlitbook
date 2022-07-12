"""
A module that contains a global Jupyter Notebook parser to read them from path
and return a StreamlitBook instance.

"""

from . import StreamlitBook
import json


def read_ipynb(path: str) -> StreamlitBook:
    """Global function to read raw Jupyter notebook JSON and pass them into
    an instance of StreamlitBook class

    Parameters
    ----------
    path: str :
        Path to the notebook

    Returns
    -------
    notebook: StreamlitBook
        An instance of StreamlitBook class.
    """
    with open(path, "rb") as file:
        raw_dict = json.load(file)

    return StreamlitBook(raw_dict['cells'], raw_dict['metadata'])
