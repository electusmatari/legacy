set PATH=%PATH%;C:\Python27;C:\Programme\NSIS

python setup.py py2exe
makensis gdu.nsi
copy con: nul:
