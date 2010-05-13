import operator
import random
import re
import sys

import yaml

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

def gen(grammar, symbols):
    # Empty symbol lists cannot be expanded
    if not symbols:
        return symbols

    productions = parse(grammar)

    print symbols
    changed = True
    while changed:
        symbolLsts, changedLst = zip(*[expand_symbol(sym, productions)
                                       for sym in symbols])
        # Concat expansion of each symbol into single list
        symbols = concat(symbolLsts)
        # Were any symbols expanded?
        changed = any(changedLst)
        if changed: print symbols

    print ''
    return symbols
    
def compose(init_syms, *grammars):
    """Use the output of each grammar as the input to the next grammar."""
    symbols = init_syms
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

    # sym+ -> sym | [sym sym*]
    if symbol.endswith("+"):
        if random.random() > .5:
            return ([symbol[:-1]], True)
        else:
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

    # raw_expansion = [{var:prob}, ...]
    for symbol, raw_expansion in raw_prods.items():
        # Coerce list of dictionaries into list of tuples
        varprobs = concat([d.items() for d in raw_expansion])
        # Split expansion string
        varprobs = [(expansion.split(), prob) for expansion, prob in varprobs]
        # Create Expansion using (choice, probability) tuples
        productions[symbol] = Expansion(varprobs)

    return productions
    
def main():
    with open(sys.argv[1]) as file:
        gen(file.read(), ["sound"])

def normalize(nums):
    """Normalize a list of numbers so they sum to one."""
    n = float(sum(nums))
    return [x/n for x in nums]

def concat(lsts):
    """Concat a list of lists into a single list."""
    return reduce(operator.add, lsts, [])

if __name__ == '__main__':
    main()



