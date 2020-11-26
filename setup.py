# SPDX-License-Identifier: MIT
import setuptools

requires = [
    'setuptools',
    'z3c.sqlalchemy >1.5.1',
    'SQLAlchemy>=0.5.5',
    'zope.sqlalchemy>=1.2.0',
    'zope.component',
    'zope.interface',
    'zope.testing',
    'zope.schema'
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Environment :: Web Environment',
    'Framework :: Zope',
    'Framework :: Zope :: 4',
    'Framework :: Zope :: 5',
    "License :: OSI Approved :: MIT License",
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.7',
    'Topic :: Database',
    'Topic :: Database :: Front-Ends',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

with open("README.md", "r") as fh:
    long_description = fh.read()

long_description += "\n------\n"

with open("CHANGES.md", "r") as fh:
    long_description += fh.read()

setuptools.setup(
    name="Products.ZAlchemyConnector",
    version='1.0.4',
    author="Gabriel Diniz Gisoldo",
    author_email='gabrielgisoldi@gmail.com',
    description="Connector and Query object for zope & sqlalchemy",
    keywords='Zope Database adapter SQLAlchemy',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huine/Products.ZAlchemyConnector",
    packages=setuptools.find_packages(),
    classifiers=classifiers,
    install_requires=requires,
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['Products'],
)
