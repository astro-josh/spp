from setuptools import setup

PACKAGENAME='spp'

setup(name='spp',
      version='0.1.0',
      description='Simple Package Info Poller',
      author='Joshua Alexander',
      author_email='jalexander@stsci.edu',
      url='',
      install_requires = [
        'requests',
        'conda_api'
      ],
      packages=['spp'],
      entry_points = {
          'console_scripts': [
              'spp = src.spp:main'
          ]
      },
      )
