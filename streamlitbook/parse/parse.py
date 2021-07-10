"""
A module that contains classes to deal with Jupyter Notebooks
"""
import json
import streamlit as st
from bs4 import BeautifulSoup
import PIL
import io


class StreamlitBook:

    def __init__(self, path):
        with open(path, 'rb') as file:
            data_dict = json.load(file)
        self._cells = [Code(cell) if cell['cell_type'] == 'code' else Markdown(cell) for cell in data_dict['cells']]
        self._n_cells = len(self._cells)
        self._metadata = data_dict['metadata']

    @property
    def cells(self):
        return self._cells

    @cells.deleter
    def cells(self):
        raise AttributeError("Cannot delete cells attribute...")

    @property
    def n_cells(self):
        return self._n_cells

    @n_cells.deleter
    def n_cells(self):
        raise AttributeError("Cannot delete n_cells attribute...")

    @property
    def metadata(self):
        return self._metadata

    @metadata.deleter
    def metadata(self):
        raise AttributeError("Cannot delete metadata attribute...")

    def __repr__(self):
        custom_repr = f"StreamlitBook with {self.n_cells} cells."
        return custom_repr

    def __str__(self):
        custom_str = f"StreamlitBook with {self.n_cells} cells."
        return custom_str


class Cell:

    def __init__(self, cell_dict: dict):
        self._type = cell_dict['cell_type']
        self._metadata = cell_dict['metadata']
        self._source = "".join(cell_dict['source'])

    @property
    def type(self):
        return self._type

    @type.deleter
    def type(self):
        raise AttributeError("Cannot delete type attribute...")

    @property
    def metadata(self):
        return self._metadata

    @metadata.deleter
    def metadata(self):
        raise AttributeError("Cannot delete metadata attribute...")

    @property
    def source(self):
        return self._source

    @source.deleter
    def source(self):
        raise AttributeError("Cannot delete source attribute...")

    def __repr__(self):
        custom_repr = f"Jupyter Cell with type {self._type}"
        return custom_repr

    def __str__(self):
        custom_str = f"Jupyter Cell with type {self._type}"
        return custom_str


class Markdown(Cell):

    def display(self):
        st.markdown(self.source, unsafe_allow_html=True)


class Code(Cell):

    def __init__(self, cell_dict: dict):
        super().__init__(cell_dict)
        self._output = cell_dict['outputs']
        self.has_output = True if len(self._output) != 0 else False

    @staticmethod
    def _display_dataframe(html_df: list):
        soup = BeautifulSoup("".join(html_df))
        soup.style.clear()
        st.markdown(str(soup), unsafe_allow_html=True)

    def display(self):
        st.code(self.source)

        if not self.has_output:
            pass
        else:
            # Store the output to a variable for ease of use
            output = self._output[0]['data']

            if "text/html" in output.keys():
                Code._display_dataframe(output['text/html'])
                del output['text/plain']
                st.write("\n")
            elif "image/png" in output.keys():
                del output['image/png']
                pass
