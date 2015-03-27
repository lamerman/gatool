#!/usr/bin/env python

__author__ = 'Alexander Ponomarev'

from setuptools import setup, find_packages

REQUIRES = ['pyevolve', ]

setup(name='GATool',
      version='0.8',
      description='Utility for adjustment of parameters for console applications with genetic algorithm',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/gatool',
      scripts=['gatool.py'],
      packages=find_packages(),
      install_requires=REQUIRES,
     )