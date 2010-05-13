from contextlib import nested
import operator
import re
import subprocess
import sys

from numpy import *
from scikits.audiolab import *

import gen

DEFAULT_GRAMMARS = ['sound.yaml']

SAMPLE_RATE = 44100
DURATION = 2

def main():
    wav_file = 'test.wav'

    init_syms = sys.argv[1].split()

    with nested(*[open(f) for f in sys.argv[2:]]) as fs:
        grammars = [f.read() for f in fs]

    symbols = gen.compose(init_syms, *grammars)
    data = process(symbols)
    write_wav(data, wav_file)

    subprocess.call('totem %s' % wav_file, shell=True)


def sinWave(freq=440, amp=1, dur=DURATION):
    # calculations adapted from http://codingmess.blogspot.com/2008/07/how-to-make-simple-wav-file-with-python.html
    samples = dur*SAMPLE_RATE
    period = SAMPLE_RATE / float(freq) # samples
    omega = 2*pi / period

    return amp*array([sin(omega*x) for x in xrange(samples)])

def sawtoothWave(freq=440, amp=1, dur=DURATION):
    samples = dur*SAMPLE_RATE
    period = SAMPLE_RATE / float(freq) # samples
    
    return array([amp*(2*(x % period)/period - 1) for x in xrange(samples)])

def squareWave(freq=440, amp=1, dur=DURATION):
    samples = dur*SAMPLE_RATE
    period = SAMPLE_RATE / float(freq) # samples

    return array([amp*sign(period/2 - x % period) for x in xrange(samples)])

ops = {'+': operator.add,
       '*': operator.mul,}
waves = {'sin': sinWave,
         'saw': sawtoothWave,
         'square': squareWave,}

def parse_symbol(symbol):
    """Parse a symbol of the form <op><wavetype>(<freq>).
    Returns a function that transforms a waveform."""

    def eat(string, prefixes):
        for prefix in prefixes:
            if string.startswith(prefix):
                return prefix, string[len(prefix):]
        # default to add
        return '+', string

    op_sym, remaining = eat(symbol, ops.keys())
    wave_sym, remaining = eat(remaining, waves.keys())

    match = re.match("\((\d*)\)", remaining)
    if match is None:
        raise Exception("frequency not recognized: "+remaining)
    freq = int(match.group(1))

    assert op_sym in ops
    op = ops[op_sym]

    assert wave_sym in waves
    wave = waves[wave_sym](freq=freq)

    return (lambda data: op(data, wave))

def process(symbols):
    samples = DURATION*SAMPLE_RATE

    # Start with empty (zero) waveform
    data = zeros(samples)

    # Apply transformation associated with each symbol
    for symbol in symbols:
        data = parse_symbol(symbol)(data)

    # Normalize data
    data = scale(data)
        
    return data

def write_wav(data, output_file='test.wav'):
    wavwrite(data, output_file, fs=SAMPLE_RATE)

def scale(data, max_val=1):
    scale_factor = float(max_val)/max(data)
    return array([scale_factor*i for i in data])

if __name__ == '__main__':
    main()
