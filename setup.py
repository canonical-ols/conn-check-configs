"""Installer for conn-check-configs
"""

import os
cwd = os.path.dirname(__file__)
__version__ = open(os.path.join(cwd, 'conn_check_configs/version.txt'),
                    'r').read().strip()

from setuptools import setup, find_packages


setup(
    name='conn-check-configs',
    description='Utilities for generating conn-check YAML configs from other'
                ' sources, such as Django settings',
    long_description=open('README.rst').read(),
    version=__version__,
    author='James Westby, Wes Mason',
    author_email='james.westby@canonical.com, wesley.mason@canonical.com',
    url='https://launchpad.net/conn-check',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=['pyyaml'],
    package_data={'conn_check_configs': ['version.txt']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'conn-check-django = conn_check_configs.django:run',
        ],
    },
    license='GPL3',
    classifiers=[
        "Topic :: System :: Networking",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ]
)
