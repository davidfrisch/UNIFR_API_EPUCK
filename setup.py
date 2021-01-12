"""Setup script for unifr_api_epuck"""
import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the docs file
with open(os.path.join(HERE, "./docs/readme.rst")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="unifr_api_epuck",
    version="0.0.43",
    description="An API to control the EPUCK from GCtronic in Webots and Python3",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="",
    author="David Frischer",
    author_email="david.frischer@unifr.ch",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["unifr_api_epuck"],
    include_package_data=True,
    install_requires=[
        "Pillow",
    ],
)
