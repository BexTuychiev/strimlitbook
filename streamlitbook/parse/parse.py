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
    """Main class to represent Jupyter Notebooks as Streamlit-compatible components"""

    def __init__(self, cell_dicts):
        self._cells = [Code(cell) if cell['cell_type'] == 'code' else Markdown(cell) for cell in cell_dicts]
        self._cell_dict = cell_dicts
        self._n_cells = len(self._cells)

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
        raise AttributeError("Cannot delete n_cells attribute...")  # TODO implement this attribute as an operator

    def __repr__(self):
        custom_repr = f"StreamlitBook with {self.n_cells} cells."
        return custom_repr

    def __str__(self):
        custom_str = f"StreamlitBook with {self.n_cells} cells."
        return custom_str

    def display(self):
        """High-level function to display each cell as Streamlit component with outputs."""
        for cell in self.cells:
            cell.display()


class Cell:
    """Generic cell class to make Jupyter Notebook cells streamlit-compatible"""

    def __init__(self, cell_dict: dict):
        self._type = cell_dict['cell_type']
        self._metadata = cell_dict['metadata']
        self._source = "".join(cell_dict['source'])
        self._tags = self._metadata.get("tags", [])

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

    @staticmethod
    def _display_image(image_string: str):
        """
        Convert base64 encoded images to bytes and display as streamlit media.

        Parameters
        ----------
        image_string: str :
            base64 encoded string of an image.

        """
        bytes_image = base64.decodebytes(str.encode(image_string))
        st.image(bytes_image, use_column_width='always')


class Markdown(Cell):
    """Extension of the generic Cell class to represent Markdown cells with more features."""

    def __init__(self, cell_dict: dict):
        super().__init__(cell_dict)
        # Add an attribute for raw attachments
        self._raw_attachments = cell_dict.get('attachments', None)

    @property
    def _attachments(self):
        """Parse cell attachments into an attribute"""
        attach_list = list()
        if self._raw_attachments:
            for _, attachment in self._raw_attachments.items():
                for _, value in attachment.items():
                    attach_list.append(value)
        return attach_list

    def _display_parsing_attachments(self):
        """
        Lower-level display method of markdown cells that parses attachments (if any)
        and display in proper media format with streamlit.
        """

        if self._attachments:
            # Split the raw Markdown code at every line that has attachments
            splitted_source = re.split(r"!\[.+]\(attachment:.+\)", self.source)
            for index, source in enumerate(splitted_source):
                st.markdown(source)  # TODO check if HTML works inside cells with attachments
                try:
                    Markdown._display_image(self._attachments[index])
                except IndexError:
                    pass
        else:
            st.markdown(self.source, unsafe_allow_html=True)

    def display(self):
        """
        Higher-level function to display Markdown cells as streamlit components.
        Display is performed based on tags.
        """
        if 'skip' in self._tags:
            return None
        elif 'ci' in self._tags:
            with st.expander("See collapsed cell"):
                self._display_parsing_attachments()
        else:
            self._display_parsing_attachments()


class Code(Cell):
    """Extension of the generic Cell class to represent code cells with more features."""

    def __init__(self, cell_dict: dict):
        super().__init__(cell_dict)
        self._raw_data = cell_dict

    @property
    def _outputs(self):
        """Parse outputs of a cell as an attribute for ease of access."""

        # Check if there are any outputs
        if len(self._raw_data['outputs']) == 0:
            return None

        # Empty list to store each output of a cell as a dictionary
        outputs = []
        for output in self._raw_data['outputs']:
            output_dict = {}

            # if stream - then output is either from print function or for stdout
            if output['output_type'] == 'stream':
                output_dict['stdout'] = ''.join(output['text'])

            # if display_data or execute_result, there is output either as media or text
            elif output['output_type'] in ("display_data", "execute_result"):
                # If the below key exists, the output is a Plotly chart
                if "application/vnd.plotly.v1+json" in output['data'].keys():
                    plotly_data_dict = output['data']['application/vnd.plotly.v1+json']['data']
                    plotly_layout_dict = output['data']['application/vnd.plotly.v1+json']['layout']

                    # If config key exists in Plotly output dict, user passed custom config to the chart
                    if "config" in output['data']['application/vnd.plotly.v1+json'].keys():
                        plotly_config_dict = output['data']['application/vnd.plotly.v1+json']['config']
                    # Combine all parts for a Plotly output
                    output_dict["plotly_fig"] = {"data": plotly_data_dict,
                                                 "layout": plotly_layout_dict,
                                                 "config": plotly_config_dict}

                # Altair chart rendering is only possible through the 'altair' tag on the cell
                elif "altair" in self._tags:
                    # Get the altair chart specs as a dictionary
                    alt_spec = ''.join(output['data']['text/plain'])
                    output_dict['altair_fig'] = eval(alt_spec)

                # text/html mime type can mean many output types
                elif "text/html" in output['data'].keys():
                    # Check if it is not Plotly chart
                    if "Plotly" in ''.join(
                            output['data']['text/html']):  # TODO add a better condition to check for Plotly HTML
                        continue
                    # Otherwise, store the raw HTML code
                    output_dict["text/html"] = ''.join(output['data']['text/html'])

                # image/png mimetype stores base64 encoded image outputs from plots, HTML, etc.
                elif "image/png" in output['data'].keys():
                    # TODO check if there are other mime types for different image extensions
                    output_dict['image/png'] = output['data']['image/png'].strip()

                # Plain text from IPython cell execution, magic commands or print
                elif "text/plain" in output['data'].keys():
                    output_dict['text/plain'] = ''.join(output['data']['text/plain'])

            # If the cell contains any outputs with errors
            elif output['output_type'] == 'error':
                output_dict['error'] = output['ename']
            outputs.append(output_dict)

        return outputs

    @staticmethod
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

    @staticmethod
    def _display_plotly(fig_dict: dict):
        """
        Static, lower-level method to display Plotly figures from a figure
        dictionaries parsed inside _outputs.

        Parameters
        ----------
        fig_dict: dict :
            Plotly figure dictionary parsed from raw outputs inside _outputs.
        """

        fig = go.Figure(dict(data=fig_dict['data'], layout=fig_dict['layout']))

        if "config" in fig_dict.keys():
            st.plotly_chart(fig, config=fig_dict['config'])
        else:
            st.plotly_chart(fig)

    @staticmethod
    def _display_vega_lite(vega_lite_spec: dict):
        """
        Static, lower-level method to display Altair charts.

        Parameters
        ----------
        vega_lite_spec: dict :
            Altair chart dictionary spec parsed from raw outputs inside _outputs.

        """

        st.vega_lite_chart(spec=vega_lite_spec)

    def _display_source(self):
        """Lower-level method to display cell code with Streamlit"""
        if len(self.source) > 0:
            st.code(self.source)

    def _display_outputs(self):
        """A lower-level function to map different _display_* functions to their specific outputs."""

        if self._outputs is None:
            return None

        display_keys = {
            "plotly_fig": Code._display_plotly,
            "altair_fig": Code._display_vega_lite,
            "text/html": Code._display_dataframe,
            "image/png": Code._display_image,
            "text/plain": lambda x: st.code(x),
            "stdout": lambda x: st.code(x),
            "error": lambda x: st.error(x)  # TODO check if error messages work
        }

        for output in self._outputs:
            for key, value in output.items():
                display_keys[key](value)

    def display(self):
        """High-level display function to combine cell source and outputs using tags."""

        if 'skip' in self._tags:
            return None
        elif 'hi' in self._tags or 'hide_input' in self._tags:
            self._display_outputs()
        elif 'ho' in self._tags or 'hide_output' in self._tags:
            self._display_source()
        elif 'ci' in self._tags or 'collapsed_input' in self._tags:
            with st.expander("See hidden source code..."):
                self._display_source()
            self._display_outputs()
        elif 'co' in self._tags or 'collapsed_output' in self._tags:
            self._display_source()
            with st.expander("See hidden output..."):
                self._display_outputs()
        else:
            self._display_source()
            self._display_outputs()
