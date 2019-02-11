import itertools
import math
import re
import time
import tokenize
from io import StringIO

import numpy as np

from parser_math import *
from symbols import Symbols, isSymbol

symbol_table = {}
token_table = {}


def tokenizer(string, vars=None):
    _tokens = []
    err_token = False
    token_map = {
        tokenize.NUMBER: '(LITERAL)',
        tokenize.STRING: '(LITERAL)',
        tokenize.NAME: '(NAME)',
        tokenize.OP: '(OP)',
        tokenize.ENDMARKER: '(ENDMARKER)',
        tokenize.ERRORTOKEN: '(ERRORTOKEN)'
    }

    tokens = tokenize.generate_tokens(StringIO(string).readline)

    for i in tokens:
        token_type = token_map[i[0]]
        token_value = i[1]

        if token_type == '(ENDMARKER)':
            _tokens += [(token_type, token_type)]
        elif token_type == '(ERRORTOKEN)':
            err_token = True
        else:
            if err_token:
                _tokens += [(token_type, '\\{0}'.format(token_value))]
                err_token = False
            else:
                _tokens += [(token_type, token_value)]

    lfuncs = [i for i in latex_math_functions.keys()]
    _tokens = get_symbols(_tokens, lfuncs, '(FUNC)', '(NAME)')

    funcs = [i for i in math_functions.keys()]
    _tokens = get_symbols(_tokens, funcs, '(FUNC)', '(NAME)')

    if vars:
        _tokens = get_symbols(_tokens, vars, '(SYMBOL)', '(NAME)')
    return _tokens


def get_symbols(tokens, vars, new_type='(SYMBOL)', match_type='(NAME)'):
    delims = '(' + '|'.join(map(re.escape, vars)) + ')'
    for n, (i, j) in enumerate(tokens):
        if i == match_type:
            l0 = [i for i in re.split(delims, j) if i != '']
            matched, not_matched = [], []

            for k in l0:
                if k in vars:
                    matched += [k]
                else:
                    not_matched += [k]

            if len(matched) > 0:
                l1 = list(map(lambda x: (new_type, x), matched))
                l2 = list(map(lambda x: (match_type, x), not_matched))
                l3 = l1 + l2
                tokens[n:n + 1] = l3

    return tokens


def _tokenize(string, vars=None):
    ops = (i for i in math_operators.keys())
    funcs = (i for i in math_functions.keys())

    OP_delim = '(?P<OP>' + '|'.join(
        map(re.escape, ops)
    ) + ')'
    FUNC_delim = '|(?P<FUNC>' + '|'.join(
        map(re.escape, funcs)
    ) + ')'

    NAME_delim = '|(?P<NAME>\w+)'
    LITERAL_delim = '|(?P<LITERAL>\d+)'
    SYMBOLS_delim = ''

    if vars:
        SYMBOLS_delim = '(?P<SYMBOLS>' + '|'.join(
                        map(re.escape, vars)
        ) + ')'

    new = re.finditer(OP_delim + FUNC_delim + SYMBOLS_delim + NAME_delim + LITERAL_delim, string)

    for i in new:
        print(i.span(), i.groupdict())


def iter_tokens(tokens):
    for i, j in tokens:
        try:
            s = symbol_table[j]

            class Token(s):
                pass

            t = Token
            t.id = i
            if not s.value:
                t.value = j

        except KeyError:
            if i in ['(NAME)', '(LITERAL)', '(SYMBOL)']:
                s = symbol_table[i]

                class Token(s):
                    pass

                t = Token

                if i == '(SYMBOL)':
                    t.value = Symbols(j)
                else:
                    t.value = j
                t.id = i
            else:
                raise SyntaxError('Undefined operator: {0}'.format(j))
        yield Token
    yield symbol_table['(ENDMARKER)']


st = 'xyz + tan(x+y) + tooxyz + tanxys'

_tokenize(st)
