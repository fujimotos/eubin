#!/usr/bin/env python3

from zipfile import ZipFile
import io
import sys
import glob
import getopt

HEADER = b'#!/usr/bin/env python3\n'
MAIN_SCRIPT = b"""\
import runpy
if __name__ == "__main__":
    runpy.run_module('eubin.main', run_name='__main__')
"""

if __name__ == '__main__':
    binfile = 'build/eubin'

    opts, args = getopt.getopt(sys.argv[1:], 'o:')
    for key, val in opts:
        if key == '-o':
            binfile = val

    binbuff = io.BytesIO()

    # Bundling modules
    with ZipFile(binbuff, mode='w') as zipfile:
        for path in glob.glob('eubin/*.py'):
            zipfile.write(path)

        # Define entry point
        zipfile.writestr('__main__.py', MAIN_SCRIPT)

    # Generate executable
    with open(binfile, 'wb') as binfile:
        binfile.write(HEADER)
        binfile.write(binbuff.getvalue())
