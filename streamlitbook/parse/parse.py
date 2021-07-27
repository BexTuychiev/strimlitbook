"""
A module that contains classes to deal with Jupyter Notebooks
"""
import json
import base64
import re
from collections import OrderedDict

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


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

    def __init__(self, cell_dict: dict):
        super().__init__(cell_dict)
        self._raw_attachments = cell_dict.get('attachments', None)

    @property
    def _attachments(self):
        attach_list = list()
        if self._raw_attachments:
            for key, attachment in self._raw_attachments.items():
                for attach_name, value in attachment.items():
                    attach_list.append(value)
        return attach_list

    def display(self):
        if self._attachments:
            splitted_source = re.split(r"!\[.+]\(attachment:.+\)", self.source)
        st.markdown(self.source, unsafe_allow_html=True)


class Code(Cell):

    def __init__(self, cell_dict: dict):
        super().__init__(cell_dict)
        self._raw_data = cell_dict

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
                if "application/vnd.plotly.v1+json" in output['data'].keys():
                    plotly_data_dict = output['data']['application/vnd.plotly.v1+json']['data']
                    plotly_layout_dict = output['data']['application/vnd.plotly.v1+json']['layout']
                    if "config" in output['data']['application/vnd.plotly.v1+json'].keys():
                        plotly_config_dict = output['data']['application/vnd.plotly.v1+json']['config']
                    output_dict["plotly_fig"] = {"data": plotly_data_dict,
                                                 "layout": plotly_layout_dict,
                                                 "config": plotly_config_dict}
                elif "text/html" in output['data'].keys():
                    if "Plotly" in ''.join(output['data']['text/html']):
                        continue
                    output_dict["text/html"] = ''.join(output['data']['text/html'])
                elif "image/png" in output['data'].keys():
                    output_dict['image/png'] = output['data']['image/png'].strip()
                elif "text/plain" in output['data'].keys():
                    output_dict['text/plain'] = ''.join(output['data']['text/plain'])
            elif output['output_type'] == 'error':
                output_dict['error'] = output['ename']
            outputs.append(output_dict)

        return outputs

    @staticmethod
    def _display_dataframe(html_df: str):
        df = pd.read_html(html_df)[0]
        df.rename(lambda x: "" if "Unnamed:" in x else x, axis='columns', inplace=True)
        st.dataframe(df.set_index(df.columns[0]))

    @staticmethod
    def _display_image(image_string: str):
        bytes_image = base64.decodebytes(str.encode(image_string))
        st.image(bytes_image, use_column_width='always')

    @staticmethod
    def _display_plotly(fig_dict: dict):
        fig = go.Figure(dict(data=fig_dict['data'], layout=fig_dict['layout']))
        if "config" in fig_dict.keys():
            st.plotly_chart(fig, config=fig_dict['config'])
        else:
            st.plotly_chart(fig)

    def display(self):
        if len(self.source) > 0:
            st.code(self.source)
        if self._outputs is None:
            return None

        display_keys = {
            "plotly_fig": Code._display_plotly,
            "text/html": Code._display_dataframe,
            "image/png": Code._display_image,
            "text/plain": lambda x: st.code(x),
            "stdout": lambda x: st.code(x),
            "error": lambda x: st.error(x)
        }

        for output in self._outputs:
            for key, value in output.items():
                display_keys[key](value)
