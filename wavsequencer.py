from contextlib import nested
import subprocess
import sys

import numpy

import gen
import wavgen

def main():
    wav_file = 'test.wav'

    init_syms = sys.argv[1].split()

    with nested(*[open(f) for f in sys.argv[2:]]) as fs:
        grammars = [f.read() for f in fs]

    symbols = gen.compose(init_syms, *grammars)

    with nested(*[open(f) for f in wavgen.DEFAULT_GRAMMARS]) as fs:
        wavgen_grammars = [f.read() for f in fs]
    
    data = create_sequence(symbols, *wavgen_grammars)
    wavgen.write_wav(data, wav_file)

    subprocess.call('totem %s' % wav_file, shell=True)


def create_sequence(wavgen_syms, *grammars):
    # Expand each sym individually
    sym_lists = [gen.compose([sym], *grammars) for sym in wavgen_syms]
    
    print "Sequence:"
    for sym_list in sym_lists: print sym_list

    # Create wav data from each expanded symbol
    datas = [wavgen.process(syms) for syms in sym_lists]

    # Concat the sounds together
    return numpy.concatenate(datas) # datas are arrays

if __name__ == '__main__':
    main()
