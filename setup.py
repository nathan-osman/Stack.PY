from distutils.core import setup
from stackpy import VERSION

setup(name='stackpy',
      version='.'.join(VERSION),
      description='Python library for accessing the Stack Exchange API.',
      author='Nathan Osman',
      author_email='admin@quickmediasolutions.com',
      url='https://github.com/nathan-osman/Stack.PY',
      license='MIT',
      packages=['stackpy'],)