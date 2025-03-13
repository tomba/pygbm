#!/usr/bin/env python3

import sys
import re

# Uses ctypesgen from pypdfium2

CTYPESGEN_PATH = '/home/tomba/work/ctypesgen/'

INCLUDE_PATH = '/usr/include'

INCLUDES = (
    f'{INCLUDE_PATH}/gbm.h',
)

OUT = 'gbm/capi/gbm.py'

CTYPESGEN_OPTS = (
    '-lgbm',
    '--no-symbol-guards',
    '--no-macro-guards',
    '--no-srcinfo',
)

sys.path.insert(0, CTYPESGEN_PATH)
sys.path.insert(0, CTYPESGEN_PATH + 'src')
from ctypesgen.__main__ import main  # pylint: disable=E,C # type: ignore  # noqa: E402

argv = [*CTYPESGEN_OPTS, f'-I{INCLUDE_PATH}', f'-o{OUT}', '-i', *INCLUDES]

main(argv)

def replace(filename, replaces):
    for r in replaces:
        pat = r[0]
        repl = r[1]

        with open(filename, encoding='utf-8') as f:
            content = f.read()

        content = re.sub(pat, repl, content, count=1, flags=re.MULTILINE)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

# Fix _IOC by using ord(type)

replace(OUT, [
        (re.escape('return (((uint32_t(a).value | (uint32_t(b).value << 8)) | (uint32_t(c).value << 16)) | (uint32_t(d).value << 24))'),
         'return (((uint32_t(ord(a)).value | (uint32_t(ord(b)).value << 8)) | (uint32_t(ord(c)).value << 16)) | (uint32_t(ord(d)).value << 24))'),
        ])
