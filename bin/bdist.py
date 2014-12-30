#!/usr/bin/env python3

from zipfile import ZipFile
import os
import glob

tmpfile = 'bin/eubin.zip'
bdist = 'bin/eubin'

# chdir
filedir = os.path.dirname(__file__)
os.chdir(os.path.join(filedir, '..'))

# Bundling eubin
with ZipFile(tmpfile, mode='w') as zipfile:
    for path in glob.glob('eubin/*.py'):
        zipfile.write(path)

    # Define entry point
    script = b'''\
from eubin import main
if __name__ == "__main__":
    main.main()
'''
    zipfile.writestr('__main__.py', script)

    zipfile.close()

# Create executable
with open(bdist, 'wb') as fw:
    fw.write(b'#!/usr/bin/env python3\n\n')
    fw.write(open(tmpfile, 'rb').read())

os.remove(tmpfile)

os.chmod(bdist, 0o755)

print('Executable:', bdist)
