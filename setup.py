import os

from setuptools import setup

from amanuense.__init__ import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='amanuense',
    version=__version__,
    author='Rafael Alves Ribeiro',
    author_email='rafael.alves.ribeiro@gmail.com',
    description='Parser do Diário Oficial da União (DOU)',
    license='MIT',
    keywords = 'parser dou',
    url = 'https://github.com/rafpyprog/amanuense',
    packages=['amanuense'],
    install_requires=['lxml',],
      extras_require={
          'test': [
              'pytest',
              'coverage'
          ]},
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
)
