from setuptools import setup, find_packages

setup(
    author='Bekhruz Tuychiev',
    description='A package to convert Jupyter Notebooks to Streamlit web apps.',
    name='streamlitbook',
    version='0.1.0',
    packages=find_packages(include=['streamlitbook', 'streamlitbook.*']),
    install_requires=['streamlit>=0.80.0', 'numpy', 'pandas'],
    python_requires='>=3.7'
)
