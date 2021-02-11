""" setup for freedompp """
from setuptools import setup, find_packages
import os


is_travis = "TRAVIS" in os.environ

setup(
    name="freedompp",
    version="0.0.1",
    author="Raphael Dussin",
    author_email="raphael.dussin@gmail.com",
    description=("create pp from history"),
    license="GPLv3",
    keywords="",
    url="https://github.com/raphaeldussin/freedompp",
    packages=find_packages(),
    scripts=["scripts/freedompp"],
)
