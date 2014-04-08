from setuptools import setup, find_packages

setup(
    name='metrics',
    version='0.0.1',

    author='Nish',
    author_email='',
    description='Metrics logger for python',
    install_requires=['contextdecorator>=0.10.0'],
    packages=find_packages(),
)
