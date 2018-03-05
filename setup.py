import os, os.path
from setuptools import find_packages, setup

setup(name='pyxz',
      version = "0.1.0",
      description='Parallelize xz',
      url='https://github.com/matt-hayden/pyxz',
      maintainer="Matt Hayden (Valenceo, LTD.)",
      maintainer_email="github.com/matt-hayden",
      license='Unlicense',
      packages=find_packages(exclude='contrib docs examples tests'.split()),
      entry_points = {
          'console_scripts': [
              'pxz=pyxz.cli:main',
              ]
          },
      install_requires = [ 'docopt' ],
      zip_safe=True,
     )
