import os

from io import open
from setuptools import setup, find_packages


here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.rst'), 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='sphinxcontrib-redoc',
    description='ReDoc powered OpenAPI (fka Swagger) spec renderer for Sphinx',
    long_description=long_description,
    license='BSD',
    url='https://github.com/ikalnytskyi/sphinxcontrib-redoc',
    keywords='sphinx openapi swagger rest api renderer docs redoc',
    author='Ihor Kalnytskyi',
    author_email='ihor@kalnytskyi.com',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    zip_safe=False,
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'jinja2 >= 2.4',
        'sphinx >= 1.5',
        'six >= 1.5',
        'PyYAML >= 3.12',
    ],
    classifiers=[
        'Topic :: Documentation',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    namespace_packages=['sphinxcontrib'],
)
