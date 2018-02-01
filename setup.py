#-*- coding: UTF-8 -*-

from setuptools import setup

setup(name="paclair",
      version="0.4",
      description="Push and Ask Clair",
      author="Gregoire UNBEKANDT",
      author_email="gregoire.unbekandt@gmail.com",
      url="https://github.com/yebinama/paclair",
      packages=["paclair"],
      install_requires=[
          'elasticsearch',
          'requests',
          'pyyaml'
      ],
      command_options={
               'build_sphinx': {
                   'project': ('setup.py', "paclair"),
                   'version': ('setup.py', "0.4"),
                   'release': ('setup.py', "0.4"),
                   'build_dir': ('setup.py', 'doc/sphinx/_build/')}},
     )
