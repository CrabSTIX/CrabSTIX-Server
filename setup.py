'''
CrabSTIX: Universal Syslog To STIX/TAXII Translator

Note that "python setup.py test" invokes pytest on the package.
With appropriately configured setup.cfg, this will check both
xxx_test modules and docstrings.

Copyright 2016, Adam Bradbury.
Licensed under APACHE 2.0.
'''

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


version = "0.1.0.1"

setup(
    name="CrabSTIX",
    version=version,
    description="Universal Syslog To STIX/TAXII Translator",
    long_description=open("README.rst").read(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python'
    ],
    keywords="STIX TAXII Threat Intelligence",
    author="Adam Bradbury",
    author_email="adamstevenbradbury@gmail.com",
    url="http://www.github.com/CrabSTIX",
    license="APACHE 2.0",
    packages=find_packages(exclude=['examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    # TODO: List of packages that this one depends upon:
    install_requires=[],
    # TODO: List executable scripts, provided by the package
    entry_points={
        'console_scripts': [
            'CrabSTIX=crabstix:main']
    }
)
