from setuptools import setup, find_packages

setup(name='unitree_sdk2py',
      version='1.0.0',
      author='Unitree',
      author_email='unitree@unitree.com',
      license="BSD-3-Clause",
      packages=find_packages(include=['unitree_sdk2py','unitree_sdk2py.*']),
      description='Unitree robot sdk version 2 for python',
      python_requires='>=3.8',
      install_requires=[
            "cyclonedds==0.10.2",
            "numpy",
            "opencv-python",
      ],
      )
