from distutils.core import setup
import py2exe

import sys
sys.path.append("lib")
from gdulib import version

setup(
    name=version.APPLONGNAME,
    version=version.VERSIONSTRING,
    description=("Freedom Through Strength. "
                 "Strength Through Superior Datamining."),
    author="Jorgen Schaefer",
    author_email="arkady@arkady-sadik.de",
    url="http://gradient.electusmatari.com/",
    windows=[
        {'script': 'scripts/gdu.py',
         'icon_resources': [(0, 'data/grd.ico')]}
        ],
    package_dir={'': 'lib'},
    packages=['gdulib'],
    data_files=[("", ["data/grd.ico", "data/gdiplus.dll"])],
    options ={
        "py2exe": {
            "packages": ["reverence"]
            }
        }
    )
