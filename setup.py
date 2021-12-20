"""Setup script for unifr_api_epuck"""
import os.path
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the docs file
with open(os.path.join(HERE, "readme.rst")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="unifr_api_epuck",
    version="1.0.6",
    description="An API controller for the e-puck2 from GCtronic for Webots and Python3",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/davidfrisch/UNIFR_API_EPUCK",
    author="David Frischer",
    author_email="david.frischer@unifr.ch",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Pillow",
        "smbus2",
        "numpy"
    ],
)
