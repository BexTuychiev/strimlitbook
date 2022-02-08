"""
A module that contains classes to deal with Jupyter Notebooks
"""
import re

import streamlit as st
from ..utilities import _display_image, _display_dataframe, \
    _display_plotly, _display_vega_lite

from .outputs import _parse_error_output, _parse_stream_output, _parse_image_output, \
    _parse_html_output, _parse_plotly_output, _parse_plain_text_output


class StreamlitBook:
    """Main class to represent Jupyter Notebooks as Streamlit-compatible components"""

    def __init__(self, cells, metadata):
        self._metadata = metadata
        self._code_language = self._metadata["kernelspec"]["language"]
        self._cells = [
            Code(cell, self._code_language) if cell['cell_type'] == 'code' else
            Markdown(cell) for cell in cells
        ]
        self._cell_dict = cells
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
        raise AttributeError(
            "Cannot delete n_cells attribute...")

    def __repr__(self):
        custom_repr = f"StreamlitBook()"
        return custom_repr

    def __str__(self):
        custom_str = f"<StreamlitBook with {self.n_cells} cells>"
        return custom_str

    def display(self):
        """
        High-level function to display each cell as a
        Streamlit component with outputs.
        """
        for cell in self.cells:
            cell.display()

    def split(self, idx_to_split):
        """
        Split the book into two at the given index.

        Parameters
        ----------
        idx_to_split: int:
            Index of the cell to perform the split.
            The second notebook will start from this index.

        Returns
        -------
        A tuple of two StreamlitBook instances.
        """
        book1 = self._cell_dict[:idx_to_split]
        book2 = self._cell_dict[idx_to_split:]

        return self.__class__(book1, self._metadata), self.__class__(book2,
                                                                     self._metadata)


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
        custom_repr = f"<StreamlitBook cell with type \"{self._type}\">"
        return custom_repr

    def __str__(self):
        custom_str = f"<StreamlitBook cell with type \"{self._type}\">"
        return custom_str


class Markdown(Cell):
    """
    Extension of the generic Cell class
    to represent Markdown cells with more features.
    """

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
                st.markdown(
                    source)  # TODO check if HTML works inside cells with attachments
                try:
                    _display_image(self._attachments[index])
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

    def __init__(self, cell_dict: dict, code_language):
        super().__init__(cell_dict)
        self._raw_data = cell_dict
        self._language = code_language

    @property
    def _outputs(self):
        """Parse outputs of a cell as an attribute for ease of access."""

        # Check if there are any outputs
        if len(self._raw_data['outputs']) == 0:
            return None

        # Store all parsing functions in the order of importance
        parsing_functions = [_parse_stream_output, _parse_plotly_output,
                             _parse_html_output, _parse_image_output,
                             _parse_plain_text_output, _parse_error_output]

        # Empty list to store parsed outputs
        outputs = list()

        # For each output of the cell
        for output in self._raw_data['outputs']:
            # Try to parse the output with each parsing function
            for func in parsing_functions:
                outputs.append(func(output) if func(output) else None)

        return [o for o in outputs if o is not None]

    def _display_source(self):
        """Lower-level method to display cell code with Streamlit"""
        if len(self.source) > 0:
            st.code(self.source)

    def _display_outputs(self):
        """
        A lower-level function to map different
        _display_* functions to their specific outputs.
        """

        if self._outputs is None:
            return None

        display_keys = {
            "plotly_fig": _display_plotly,
            "altair_fig": _display_vega_lite,
            "text/html": _display_dataframe,
            "image/png": _display_image,
            "text/plain": lambda x: st.code(x),
            "stdout": lambda x: st.code(x),
            "error": lambda x: st.error(x)
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
