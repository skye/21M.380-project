import subprocess
import sys

import gen
import wavgen

wav_file = 'test.wav'

with open(sys.argv[1]) as f:
    symbols = gen.gen(f.read(), ['sound'])

wavgen.process(symbols, wav_file)

subprocess.call('totem %s' % wav_file, shell=True)
