from distutils.core import setup
import py2exe

import version

setup(
    name=version.APPLONGNAME,
    version="%.1f" % version.VERSION,
    description="",
    author="Jorgen Schaefer",
    author_email="arkady@arkady-sadik.de",
    url="",
    windows=[
        {'script': 'gdu.py',
         'icon_resources': [(0, 'grd.ico')]}
        ],
    py_modules=['api', 'cacheutils', 'control',
                'gdu', 'gui', 'handler', 'setup',
                'status', 'uploader', 'version',
                'watcher'],
    data_files=[(".", ["grd.ico"])],
    options ={
        "py2exe": {
            "packages": ["reverence"]
            }
        }
    )
