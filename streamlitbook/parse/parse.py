"""
A module that contains classes to deal with Jupyter Notebooks
"""
import json


class Notebook:

    def __init__(self, path):
        with open(path, 'rb') as file:
            data_dict = json.load(file)
        self.cells = data_dict['cells']
        self.n_cells = len(data_dict['cells'])
        self.metadata = data_dict['metadata']


class Cell:

    def __init__(self, cell_dict: dict):
        self._type = cell_dict['cell_type']
        self._metadata = cell_dict['metadata']
        self.source = cell_dict['source']

    @property
    def type(self):
        return self._type

    @property
    def metadata(self):
        return self._metadata



class Code(Cell):
    pass


class Markdown(Cell):
    pass
