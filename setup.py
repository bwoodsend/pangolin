# -*- coding: utf-8 -*-
"""
"""

from setuptools import setup, find_packages
from pathlib import Path

HERE = Path(__file__).resolve().parent

readme = (HERE / 'README.rst').read_text("utf-8")

setup(
    author="Brénainn Woodsend",
    author_email='bwoodsend@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description=
    "Tools for writing, parsing, manipulating and pretty printing Dental Palmer"
    "notation and normalising other Dental identifiers into machine-readable "
    "formats.",
    install_requires=[],
    extras_require={
        "test": [
            'pytest>=3', 'pytest-order', 'coverage', 'pytest-cov',
            'coverage-conditional-plugin'
        ]
    },
    license="MIT license",
    long_description=readme,
    package_data={"pangolin": []},
    keywords='pangolin',
    name='pangolin',
    packages=find_packages(include=['pangolin', 'pangolin.*']),
    url='https://github.com/bwoodsend/pangolin',
    version="0.1.0",
    zip_safe=False,
)
