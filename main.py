from contextlib import nested
import subprocess
import sys

import gen
import wavgen

wav_file = 'test.wav'

init_syms = sys.argv[1].split()

with nested(*[open(f) for f in sys.argv[2:]]) as fs:
    grammars = [f.read() for f in fs]

symbols = gen.compose(init_syms, *grammars)
    
wavgen.process(symbols, wav_file)

subprocess.call('totem %s' % wav_file, shell=True)
