from contextlib import nested
import operator
import random
import re
import sys

import yaml

def main():
    init_syms = sys.argv[1].split()

    if len(sys.argv) < 1:
        print "USAGE python gen.py <initial_sequence> <grammar>..."

    with nested(*[open(f) for f in sys.argv[2:]]) as fs:
        grammars = [f.read() for f in fs]

    compose(init_syms, *grammars)


class Expansion(object):

    def __init__(self, choices):
        expansions, weights = zip(*choices)
        self.choices = zip(expansions, normalize(weights))

    def choose_expansion(self):
        # Algorithm from http://snippets.dzone.com/posts/show/732
        n = random.uniform(0, 1)
        for choice, weight in self.choices:
            if n < weight:
                break
            n = n - weight
	return choice

def gen(grammar, symbols, output=True):
    # Empty symbol lists cannot be expanded
    if not symbols:
        return symbols

    productions = parse(grammar)

    if output: print symbols
    changed = True
    while changed:
        symbolLsts, changedLst = zip(*[expand_symbol(sym, productions)
                                       for sym in symbols])
        # Concat expansion of each symbol into single list
        symbols = concat(symbolLsts)
        # Were any symbols expanded?
        changed = any(changedLst)
        if changed and output: print symbols

    if output: print ''
    return symbols
    
def compose(init_syms, *grammars):
    """Use the output of each grammar as the input to the next grammar."""
    symbols = init_syms
    symbols = gen("", symbols, output=False)
    for grammar in grammars:
        symbols = gen(grammar, symbols)
    return symbols

def expand_symbol(symbol, expansions):
    """Expand symbol once using expansions.

    Returns the possibly expanded symbol and whether the symbol was actually
    expanded.

    symbol (string)
    expansions -- symbol -> Expansion mapping

    """
    # sym* -> [] | [sym sym*]
    if symbol.endswith("*"):
        if random.random() > .5:
            return ([], True)
        else:
            return ([symbol[:-1], symbol], True)

    # sym+ -> [sym sym*]
    if symbol.endswith("+"):
        return ([symbol[:-1], symbol[:-1]+"*"], True)        

    # [lo - hi] -> integer in range [lo, hi]
    def rangerepl(match):
        lo = int(match.group(1))
        hi = int(match.group(2))
        return str(random.choice(xrange(lo,hi)))

    new_sym, sub_cnt = re.subn("\[(\d*)-(\d*)\]", rangerepl, symbol)
    # Check if subs were actually made
    if sub_cnt > 0: return ([new_sym], True)

    # Check for user-defined expansions
    if symbol not in expansions:
        # No expansions 
        return ([symbol], False)

    return (expansions[symbol].choose_expansion(), True)

def parse(grammar):
    """Returns a symbol->Expansion mapping.

    file -- file object of productions

    """
    productions = {}
    raw_prods = yaml.load(grammar)

    if raw_prods is None:
        # Empty grammar
        return productions

    # raw_expansion = [{var:prob}, ...]
    for symbol, raw_expansion in raw_prods.items():
        # Split expansion string
        varprobs = [(expansion.split(), prob) 
                    for expansion, prob in raw_expansion.items()]
        # Create Expansion using (choice, probability) tuples
        productions[symbol] = Expansion(varprobs)

    return productions
    
def normalize(nums):
    """Normalize a list of numbers so they sum to one."""
    n = float(sum(nums))
    return [x/n for x in nums]

def concat(lsts):
    """Concat a list of lists into a single list."""
    return reduce(operator.add, lsts, [])

if __name__ == '__main__':
    main()



