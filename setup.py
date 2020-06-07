from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dahuffman',
    version='0.4.1-alpha',
    description='Pure Python Huffman encoder and decoder module',
    long_description=long_description,
    url='https://github.com/soxofaan/dahuffman',
    author='Stefaan Lippens',
    author_email='soxofaan@gmail.com',
    license='MIT',
    packages=['dahuffman'],
    include_package_data=True,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: System :: Archiving :: Compression',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='huffman compression encoding decoding',

)
