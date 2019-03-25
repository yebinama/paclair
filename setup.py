#-*- coding: UTF-8 -*-

from setuptools import setup
from codecs import open

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(name="paclair",
      version="3.2.0",
      description="Push and Analyse containers with Clair",
      long_description=readme,
      author="Grégoire UNBEKANDT",
      url="https://github.com/yebinama/paclair",
      packages=["paclair", "paclair/api", "paclair/plugins", "paclair/docker", "paclair/ancestries"],
      package_data={
        "paclair": ['api/template/report.tpl']
      },
      install_requires=[
          'elasticsearch',
          'requests>=2.4.2',
          'pyyaml',
          'bottle'
      ],
      command_options={
               'build_sphinx': {
                   'project': ('setup.py', "paclair"),
                   'version': ('setup.py', "3.1.1"),
                   'release': ('setup.py', "3.1.1"),
                   'build_dir': ('setup.py', 'doc/sphinx/_build/')}},
     entry_points={
         'console_scripts': [
             'paclair = paclair.__main__:main'
         ]
     },
     classifiers=[
         "Programming Language :: Python",
         "Programming Language :: Python :: 3",
         "Programming Language :: Python :: 3.2",
         "Programming Language :: Python :: 3.3",
         "Programming Language :: Python :: 3.4",
         "Programming Language :: Python :: 3.5",
         "Programming Language :: Python :: 3.6",
         "Programming Language :: Python :: 3.7",
     ],
)
