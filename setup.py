from setuptools import setup, find_packages
from pathlib import Path


HERE = Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    author='Bekhruz (Bex) Tuychiev',
    email='bex@ibexprogramming.com',
    license="MIT",
    description='A package to convert Jupyter Notebooks to Streamlit web apps.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/BexTuychiev/streamlitbook',
    name='strimlitbook',
    version='0.1.0',
    packages=find_packages(include=['strimlitbook', 'strimlitbook.*']),
    install_requires=['streamlit', 'numpy', 'pandas', 'plotly', 'Pillow'],
    python_requires='>=3.7'
)
