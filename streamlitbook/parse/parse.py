"""
A module that contains classes to deal with Jupyter Notebooks
"""
import json

import pandas as pd
import streamlit as st
import base64


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
        self._raw_data = cell_dict

    @staticmethod
    def _display_dataframe(html_df: str):
        df = pd.read_html(html_df)[0]
        df.rename(lambda x: "" if "Unnamed:" in x else x, axis='columns', inplace=True)
        st.dataframe(df.set_index(df.columns[0]))

    @property
    def _outputs(self):
        if len(self._raw_data['outputs']) == 0:
            return None

        outputs = []
        for output in self._raw_data['outputs']:
            output_dict = {}
            if output['output_type'] == 'stream':
                output_dict['stdout'] = ''.join(output['text'])
            elif output['output_type'] in ("display_data", "execute_result"):
                if "text/html" in output['data'].keys():
                    output_dict["text/html"] = ''.join(output['data']['text/html'])
                elif "image/png" in output['data'].keys():
                    output_dict['image/png'] = output['data']['image/png'].strip()
                elif "text/plain" in output['data'].keys():
                    output_dict['text/plain'] = ''.join(output['data']['text/plain'])
            elif output['output_type'] == 'error':
                output_dict['error'] = output['ename']
            outputs.append(output_dict)

        return outputs

    def display(self):
        # if not self._outputs:
        #     st.code(self._source)
        #
        # display_codes = {
        #     'text/html': Cell._display_dataframe
        # }
        pass
