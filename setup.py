#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

from bote import _version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bote",
    version=f"{_version.__version__}",
    author="Rüdiger Voigt",
    author_email="projects@ruediger-voigt.eu",
    description="Send email messages and enforce encryption.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RuedigerVoigt/bote",
    package_data={"bote": ["py.typed"]},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=["compatibility>=0.9.0",
                      "userprovided>=0.9.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "Topic :: Communications :: Email",
        "Topic :: Security :: Cryptography"
    ],
)
