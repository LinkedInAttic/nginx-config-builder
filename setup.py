#!/usr/bin/env python

import os
import setuptools
import subprocess
import sys


setup_requires = [
    'pytest-runner',
]

requirements = [
    'six==1.10.0',
]

test_requirements = [
    'pytest==3.0.6',
]

extras = {}

if int(setuptools.__version__.split(".", 1)[0]) < 18:
    if sys.version_info[0:2] < (3, 3):
        requirements.append("enum34==1.1.6")
else:
    extras[":python_version<'3.3'"] = ["enum34"]


class Venv(setuptools.Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'nginx-config-builder')
        venv_cmd = [
            'virtualenv',
            venv_path
        ]
        print('Creating virtual environment in {path}'.format(path=venv_path))
        subprocess.check_call(venv_cmd)
        print('Linking `activate` to top level of project.\n')
        print('To activate, simply run `source activate`.')
        try:
            os.symlink(
                os.path.join(venv_path, 'bin', 'activate'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'activate')
            )
        except OSError:
            print('Unable to create symlink, you may have a stale symlink from a previous invocation.')


setuptools.setup(
    name='nginx-config-builder',
    version='0.0.2',
    description="A python library for generating nginx configs.",
    author="Loren M. Carvalho",
    author_email='loren@linkedin.com',
    url='https://github.com/linkedin/nginx-config-builder',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    setup_requires=setup_requires,
    install_requires=requirements,
    extras_require=extras,
    license="BSD license",
    keywords='nginx-config-builder',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='test',
    tests_require=requirements + test_requirements,
    cmdclass={'venv': Venv},
)
