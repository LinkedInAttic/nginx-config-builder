import sys

if sys.version_info < (3, 6):
    print('\nnginx-config-builder requires at least Python 3.6!')
    sys.exit(1)

import os
import subprocess
import setuptools
import venv

from pathlib import Path

requirements = ["six"]

extras = {}

if int(setuptools.__version__.split(".", 1)[0]) < 18:
    if sys.version_info[0:2] < (3, 3):
        requirements.append("enum34")
else:
    extras[":python_version<'3.3'"] = ["enum34"]


class Venv(setuptools.Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        venv_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "venv", "nginx-config-builder"
        )
        print("Creating virtual environment in {}".format(venv_path))
        venv.main(args=[venv_path])
        print(
            "Linking `activate` to top level of project.\n"
            "To activate, simply run `source activate`."
        )
        try:
            os.symlink(
                Path(venv_path, "bin", "activate"),
                Path(Path(__file__).absolute().parent, "activate"),
            )
        except FileExistsError:
            pass


def readme():
    with open("README.md") as f:
        return f.read()


setuptools.setup(
    name="nginx-config-builder",
    version="2.0.0",
    description="A python library for generating nginx configs.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Loren M. Carvalho",
    author_email="loren@linkedin.com",
    url="https://github.com/linkedin/nginx-config-builder",
    packages=["nginx.config"],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras,
    license="BSD license",
    keywords="nginx-config-builder",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={"venv": Venv},
)
