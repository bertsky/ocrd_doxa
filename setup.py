"""
Installs:
    - ocrd-binarize-doxa
"""

import codecs
import json
from setuptools import setup
from setuptools import find_packages

with codecs.open('README.md', encoding='utf-8') as f:
    README = f.read()

with open('./ocrd-tool.json', 'r') as f:
    version = json.load(f)['version']
    
setup(
    name='ocrd_doxa',
    version=version,
    description='OCR-D wrapper for DoxaPy image binarization via locally adaptive thresholding',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Robert Sachunsky',
    author_email='sachunsky@informatik.uni-leipzig.de',
    url='https://github.com/bertsky/ocrd_doxa',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').read().split('\n'),
    package_data={
        '': ['*.json', '*.yml', '*.yaml', '*.csv.gz', '*.jar', '*.zip'],
    },
    entry_points={
        'console_scripts': [
            'ocrd-doxa-binarize=ocrd_doxa.cli:ocrd_doxa_binarize',
        ]
    }
)
