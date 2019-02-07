from setuptools import setup, find_packages

PACKAGENAME='spp'

setup(name='spp',
      version='0.1.0',
      description='Simple Package Info Poller',
      author='Joshua Alexander',
      author_email='jalexander@stsci.edu',
      url='',
      install_requires = [
        'requests',
        'beautifultable'
      ],
      packages=find_packages(),
      entry_points = {
          'console_scripts': [
              'spp = spp.spp:main',
          ]
      },
      )
