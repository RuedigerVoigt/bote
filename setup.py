#!/usr/bin/env python3

import setuptools

from bote import _version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bote",
    version=_version.__version__,
    author="Rüdiger Voigt",
    author_email="projects@ruediger-voigt.eu",
    description="Send email messages and enforce encryption.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RuedigerVoigt/bote",
    package_data={"bote": ["py.typed"]},
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    install_requires=["compatibility>=2.0.0",
                      "userprovided>=2.1.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "Topic :: Communications :: Email",
        "Topic :: Security :: Cryptography"
    ],
)
