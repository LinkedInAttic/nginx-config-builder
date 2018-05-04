import os
import setuptools
import subprocess
import sys


requirements = [
    'six>=1.10.0',
]

extras = {}

if int(setuptools.__version__.split(".", 1)[0]) < 18:
    if sys.version_info[0:2] < (3, 3):
        requirements.append("enum34==1.1.6")
else:
    extras[":python_version<'3.3'"] = ["enum34"]


class Venv(setuptools.Command):
    user_options = [('python=', None, 'Which interpreter to build your venv with')]

    def initialize_options(self):
        self.python = ''

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'nginx-config-builder')
        print('Creating virtual environment in {path}'.format(path=venv_path))
        if '3' in self.python or sys.version_info[0] >= 3:
            import venv
            venv.main(args=[venv_path])
        else:
            venv_cmd = ['virtualenv']
            if self.python:
                venv_cmd.extend(['-p', self.python])
            venv_cmd.append(venv_path)
            subprocess.check_call(venv_cmd)
        print('Linking `activate` to top level of project.\n')
        print('To activate, simply run `source activate`.')
        try:
            os.symlink(
                os.path.join(venv_path, 'bin', 'activate'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'activate')
            )
        except OSError:
            # symlink already exists
            pass


setuptools.setup(
    name='nginx-config-builder',
    version='1.0.1',
    description="A python library for generating nginx configs.",
    author="Loren M. Carvalho",
    author_email='loren@linkedin.com',
    url='https://github.com/linkedin/nginx-config-builder',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras,
    license="BSD license",
    keywords='nginx-config-builder',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass={'venv': Venv},
)
