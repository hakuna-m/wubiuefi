#!/usr/bin/env python

#~ from cx_Freeze import setup, Executable

import os
import re

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

def find_packages():
    packages = []
    for directory, subdirectories, files in os.walk("wubi"):
        if '__init__.py' in files:
            packages.append(directory.replace(os.sep, '.'))
    return packages

setup(
    name="wubi",
    version="8.10",
    description="Wubi is the Windows Ubuntu Installer.",
    author="Agostino Russo",
    author_email="agostino.russo@gmail.com",
    maintainer="Ubuntu Installer Team",
    maintainer_email="ubuntu-installer@lists.ubuntu.com",
    license="GPL",
    url="https://wubi-installer.org",
    download_url="https://launchpad.net/wubi/+download",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Installation/Setup",
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    package_data={},
    ext_modules=()

    #~ ## cx_freeze
    #~ executables = [Executable("src/wubi/wubi.py")])m

)
