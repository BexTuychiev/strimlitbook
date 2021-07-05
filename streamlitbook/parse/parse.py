"""
A module that contains classes to deal with Jupyter Notebooks
"""
import json


class StreamlitBook:

    def __init__(self, path):
        with open(path, 'rb') as file:
            data_dict = json.load(file)
        self._cells = [Code(cell) if cell['type'] == 'code' else Markdown(cell) for cell in data_dict['cells']]
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
        self._source = cell_dict['source']

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


class Code(Cell):
    pass


class Markdown(Cell):
    pass
