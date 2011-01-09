#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.1'

setup(name='benchmarkr',
      version=version,
      description="Statistically rigourous benchmarking for Python snippets.",
      long_description="""\
Statistically rigourous benchmarking for Python snippets.""",
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Programming Language :: Python",
                   ], 
      keywords='profiling performance measurement',
      author='Sarah Mount',
      author_email='s.mount@wlv.ac.uk',
      url='https://github.com/snim2/benchmarkr',
      license='GPL',
      packages=find_packages(exclude=['rst']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      )
