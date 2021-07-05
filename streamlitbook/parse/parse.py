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
    pass


class Code(Cell):
    pass


class Markdown(Cell):
    pass
