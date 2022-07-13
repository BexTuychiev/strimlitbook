"""
A module that contains classes to deal with Jupyter Notebooks
"""
import re
from functools import partial
import streamlit as st
from ..utilities import _display_image, _display_dataframe, \
    _display_plotly, _display_vega_lite

from .outputs import _parse_error_output, _parse_stream_output, _parse_image_output, \
    _parse_html_output, _parse_plotly_output, _parse_plain_text_output


class StreamlitBook:
    """
    Main class to represent Jupyter Notebooks as Streamlit-compatible components

    Attributes
    ----------
    cells : list
        A list of Code or Markdown cells parsed from the notebook
    n_cells : int
        The total number of cells in the notebook. Only counts code and markdown cells.
        Raw cells are ignored.

    Methods
    -------
    display()
        High-level function to display each cell input and output with corresponding
         Streamlit functions.
    """

    def __init__(self, cells, metadata):
        """
        Parameters
        ----------
        cells : list
            A list of Code/Markdown cells parsed from the raw JSON notebook code.
        metadata : dict
            A dictionary containing the metadata of the notebook.
        """
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

    def __getitem__(self, idx: int):
        """
        Get the cell at the given index.
        Parameters
        ----------
        idx : int
            The index of the cell to get.

        Returns
        -------
            cell: Code, Markdown
                The extracted cell.
        """
        if isinstance(idx, slice):
            indices = range(*idx.indices(self._n_cells))
            return [self._cells[i] for i in indices]
        return self._cells[idx]

    def display(self):
        """
        High-level function to display each cell as a
        Streamlit component with outputs.

        Notes
        -----
            See the display function of Code and Markdown classes
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
            tuple: A tuple of two StreamlitBook instances.
        """
        book1 = self._cell_dict[:idx_to_split]
        book2 = self._cell_dict[idx_to_split:]

        return self.__class__(book1, self._metadata), self.__class__(book2,
                                                                     self._metadata)


class Cell:
    """
    Generic cell class to make Jupyter Notebook cells streamlit-compatible.

    Attributes
    ----------
    type : str
        The type of the cell - either code or markdown
    metadata : dict
        The metadata of the cell. Contains the cell's tags and attachments.
    source : str
        The source code of the cell. Either code or markdown.
    """

    def __init__(self, cell_dict: dict):
        """
        Parameters
        ----------
        cell_dict : dict
            A dictionary containing the cell's metadata, source and
            outputs if the cell is a code cell.
        """
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
    Subclass of the Cell class to represent Markdown cells with more features.
    """

    def __init__(self, cell_dict: dict):
        super().__init__(cell_dict)
        # Add an attribute for raw attachments
        self._raw_attachments = cell_dict.get('attachments', None)

    @property
    def _attachments(self):
        """
        Parse cell attachments into an attribute.

        Returns
        -------
        attach_list : list
            A list of strings of the attachment contents.
        """
        # An empty list to store parsed attachments
        attach_list = list()

        # If there are attachments
        if self._raw_attachments:
            # For each attachment
            for _, attachment in self._raw_attachments.items():
                # Get the contents of each attachment
                for _, value in attachment.items():
                    attach_list.append(value)
        return attach_list

    def _display_parsing_attachments(self):
        """
        Lower-level display method that parses attachments (if any)
        and displays them in proper media format with streamlit.
        """

        if self._attachments:
            # Split the raw Markdown code at every line that has attachments
            splitted_source = re.split(r"!\[.+]\(attachment:.+\)", self.source)

            for index, source in enumerate(splitted_source):
                st.markdown(
                    source)  # TODO check if HTML works inside cells with attachments
                try:
                    # TODO check if the below function works with GIFs
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
            # Skip the markdown cell
            return None
        elif 'ci' in self._tags:
            # Create a collapsed markdown cell in Streamlit
            with st.expander("See collapsed cell"):
                self._display_parsing_attachments()
        else:
            self._display_parsing_attachments()


class Code(Cell):
    """
    Subclass of the Cell class to represent code cells with more features.
    """

    def __init__(self, cell_dict: dict, code_language):
        super().__init__(cell_dict)
        self._raw_data = cell_dict
        self._language = code_language

    @property
    def _outputs(self):
        """
        Parse outputs of a cell as an attribute for ease of access.
        """

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
                # TODO check if this can be simplified
                outputs.append(func(output) if func(output) else None)

        return [o for o in outputs if o is not None]

    def _display_source(self):
        """
        Lower-level method to display cell code with Streamlit
        """
        if len(self.source) > 0:
            st.code(self.source)

    def _display_outputs(self):
        """
        A lower-level function to map different
        _display_* functions to their specific outputs.
        """

        if self._outputs is None:
            return None

        # First, create a function to display code output with always the same
        # language as the cell. Created mainly for Julia and R code cells.
        # Because the default is Python.
        _display_code = partial(st.code, language=self._language)

        # Now, map outputs to their _display_* functions
        display_keys = {
            "plotly_fig": _display_plotly,
            "altair_fig": _display_vega_lite,
            "text/html": _display_dataframe,
            "image/png": _display_image,
            "text/plain": lambda x: _display_code(x),
            "stdout": lambda x: _display_code(x),
            "error": lambda x: st.error(x)
        }

        for output in self._outputs:
            for key, value in output.items():
                display_keys[key](value)

    def display(self):
        """
        High-level display function to display cell source and outputs based on tags.
        """

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
