#-*- coding: UTF-8 -*-

from setuptools import setup
from codecs import open

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(name="paclair",
      version="1.0.0",
      description="Push and Analyse containers with Clair",
      long_description=readme,
      author="Grégoire UNBEKANDT",
      url="https://github.com/yebinama/paclair",
      packages=["paclair", "paclair/plugins", "paclair/docker"],
      install_requires=[
          'elasticsearch',
          'requests',
          'pyyaml'
      ],
      command_options={
               'build_sphinx': {
                   'project': ('setup.py', "paclair"),
                   'version': ('setup.py', "1.0.0"),
                   'release': ('setup.py', "1.0.0"),
                   'build_dir': ('setup.py', 'doc/sphinx/_build/')}},
     entry_points={
         'console_scripts': [
             'paclair = paclair.__main__:main'
         ]
     },
     )
