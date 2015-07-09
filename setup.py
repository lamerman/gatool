#!/usr/bin/env python

__author__ = 'Alexander Ponomarev'

from setuptools import setup, find_packages

REQUIRES = ['pyevolve', ]

setup(name='GATool',
      version='1.0.1',
      description='Utility for adjustment of parameters for console applications with genetic algorithm',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/gatool',
      scripts=['gatool.py'],
      packages=find_packages(),
      install_requires=REQUIRES,
      license="BSD",
      platforms=["Independent"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries",
      ],
     )