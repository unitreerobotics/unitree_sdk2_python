from setuptools import setup, find_packages


def load_requirements(filename:str='requirements.txt') -> None:
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line and not line.startswith("#")]

requirements = load_requirements()

setup(
    name='unitree_sdk2py',
    version='1.0.0',
    author='Unitree',
    author_email='unitree@unitree.com',
    license="BSD-3-Clause",
    packages=find_packages(),
    description='Unitree robot sdk version 2 for python',
    python_requires='>=3.8,<3.11',
    install_requires=requirements
)