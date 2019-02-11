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
        tokenize.ERRORTOKEN: '(ERRORTOKEN)',
        tokenize.NEWLINE: '(NEWLINE)'
    }

    tokens = tokenize.generate_tokens(StringIO(string).readline)

    for i in tokens:
        token_type = token_map[i[0]]
        token_value = i[1]

        if token_type == '(ENDMARKER)':
            _tokens += [(token_type, token_type)]
        elif token_type == '(ERRORTOKEN)':
            err_token = True
        elif token_type == '(NEWLINE)':
            pass
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


def _value(s):
    try:
        s = s.evaluate()
    except AttributeError:
        pass

    try:
        t = float(s)
    except ValueError:
        if s in math_constants.keys():
            t = float(symbol_table[s]())
        else:
            raise ValueError('Object {0} is not a float!'.format(s))
    return t


def _subs(s, values):
    try:
        subs(s, values)
    except AttributeError:
        pass

    if isinstance(s, Symbols) and s.id in values.keys():
        s.value = values[s.id]

    return s


class symbol_base(object):
    id = value = lbp = 0
    derivative = cluster = polycluster = None

    def nud(self):
        raise SyntaxError('nud not properly defined!')

    def led(self, left):
        raise SyntaxError('led not properly defined!')

    def __str__(self):
        func = self.value
        _dict = self.__dict__

        if 'third' in _dict:
            pass
        elif 'second' in _dict:
            first = str(self.first)
            second = str(self.second)
            return '({0} {1} {2})'.format(first, func, second)

        elif 'first' in _dict and func in math_functions.keys():
            first = str(self.first)
            return '{0}({1})'.format(func, first)
        else:
            return str(self.first)

    def evaluate(self):
        func = self.value
        v = []
        _dict = self.__dict__

        if 'second' in _dict:
            second = _value(self.second)
            v.insert(0, second)

        if 'first' in _dict and self.value in math_functions.keys():
            first = _value(self.first)
            v.insert(0, first)

        if self.value in ['(', ')']:
            first = _value(self.first)
            return first
        else:
            try:
                t = math_functions[self.value](*v)
            except TypeError:
                if func in ['+', '-']:
                    v.insert(0, float('{0}1'.format(func)))
                    t = math_operators['*'](*v)
                    return t

                return self

        return t

    def __eq__(self, other):
        try:
            if str(self) == str(other):
                return True
        except AttributeError:
            pass
        return False


def symbol(id, bp=0):
    try:
        s = symbol_table[id]
        return s
    except KeyError:
        class s(symbol_base):
            pass

        s.id = s.value = id
        s.lbp = bp

    symbol_table[id] = s
    return s


def create_symbol(id, value, traits):
    s = symbol_base()
    s.id = id
    s.value = value

    for i, j in traits.items():
        setattr(s, i, j)
    return s


def clone_symbol(s1, s2):
    for i, j in s1.__dict__.items():
        setattr(s2, i, j)
    return s2


def _to_latex(s, vars):
    try:
        s = to_latex(s, vars)
    except AttributeError:
        pass

    return s


def _pprint(s, vars):
    try:
        s = pprint(s, vars)
    except AttributeError:
        pass

    return s


def subs(s, values):
    func = s.value
    _dict = s.__dict__

    if 'third' in _dict:
        pass
    elif 'second' in _dict:
        s.first = _subs(s.first, values)
        s.second = _subs(s.second, values)
        return s

    elif 'first' in _dict and func in math_functions.keys() or func in [')', '(']:
        s.first = _subs(s.first, values)
        return s

    else:
        return s


def to_latex(s, vars):
    func = s.value
    _dict = s.__dict__

    if 'third' in _dict:
        pass
    elif 'second' in _dict:
        first = _to_latex(s.first, vars)
        second = _to_latex(s.second, vars)

        isf = isSymbol(first)
        iss = isSymbol(second)

        if func == '*':
            if iss or (isf and iss):
                t = '{{{0}}}{{{2}}}'.format(first, func, second)
            else:
                t = '{{{0}}}*{{{2}}}'.format(first, func, second)
            t = '{{{0}}}{{{2}}}'.format(first, func, second)
        elif func == '^':
            t = '{{{0}}}^{{{2}}}'.format(first, func, second)
        elif func == '/':
            t = '\\dfrac{{{0}}}{{{1}}}'.format(first, second)
        else:
            t = '{{{0}}} {1} {{{2}}}'.format(first, func, second)
        return t

    elif 'first' in _dict and func in math_functions.keys():
        first = _to_latex(s.first, vars)
        t = '\\{0}{{({1})}}'.format(func, first)
        return t

    elif func in ['(', ')']:
        first = _to_latex(s.first, vars)
        return first
    else:
        return s


def iter_cells(s, cells, level):
    N = len(cells)

    if level > (N - 1):
        cells += [[]]

    # cells[level]

    # for i in range(level+1, N):
    # 	cells[i] = ['']

    return cells


cells = np.asarray([[''] * 10] * 10, dtype=object)

level = 0
plevel = 0

rlevel = 0
prlevel = 0
row = 0


def pprint(s, vars):
    global level, cells, plevel, rlevel, prlevel, row
    func = s.value
    _dict = s.__dict__

    if 'third' in _dict:
        pass
    elif 'second' in _dict:
        first = _pprint(s.first, vars)
        second = _pprint(s.second, vars)
        print(first, second)

        isf = isSymbol(first)
        iss = isSymbol(second)

        if func == '*':
            if iss or (isf and iss):
                t = '{0}{1}'.format(first, second)
            else:
                t = '{0}*{1}'.format(first, second)
        elif func == '^':
            t = '{0}^{1}'.format(first, func, second)

        elif func == '/':
            rlevel = 0
            plevel = level

            first = str(first)
            second = str(second)

            level += 1

            len1 = len(first)
            len2 = len(second)

            if len1 > len2:
                bars = '-' * len1
                spaces = ' ' * (len1 // 2)

                t = '{0} / {1}'.format(first, second)

                sp = ''
                b = bars + spaces
            else:
                bars = '-' * len2
                spaces = ' ' * (len2 // 1)

                sp = spaces
                b = bars

                t = '{0} / {1}'.format(first, second)

            if level > 0:
                s = '{1}'.format(sp, first)
                cells[level][row] = s

            if plevel == 0:
                s = '{1}'.format(b, second)
                cells[0][row] = s

        else:
            level = 0
            t = '{0} {1} {2}'.format(first, func, second)
            row += 1

        prlevel = rlevel
        rlevel += 1

        if plevel == level == prlevel == 0:
            cells[0][row] = t
            row += 1
        return t

    elif 'first' in _dict and func in math_functions.keys():
        first = _pprint(s.first, vars)
        t = '{0}({1})'.format(func, first)
        return t
    elif func in ['(', ')']:
        return _pprint(s.first, vars)
    else:
        return s


def infix(id, bp):
    s = symbol(id, bp)

    def led(self, key, first):
        self.first = first
        self.second = expression(key, self.lbp)
        return self

    s.led = led


def infixr(id, bp):
    s = symbol(id, bp)

    def led(self, key, first):
        self.first = first
        self.second = expression(key, self.lbp - 1)
        return self

    s.led = led


def prefix(id, bp):
    s = symbol(id, bp)

    def nud(self, key):
        self.first = expression(key)
        return self

    s.nud = nud


def advance(key, string=None, type='value'):
    if getattr(token_table[key][0], type) != string and string != None:
        raise SyntaxError('Advance failed!\"{0}\" does not match \"{1}\"'.format(token_table[key][0].value, string))

    expr = token_table[key][1]
    t = next(expr)

    token_table[key][0] = t
    token_table[key][1] = expr


def method(s):
    assert issubclass(s, symbol_base)

    def _setattr(f):
        setattr(s, f.__name__, f)

    return _setattr


def argument_list(key, list, types=['(NAME)'], breaks=['']):
    while True:
        if token_table[key][0].id not in types:
            raise SyntaxError('Undefined argument type!')
        else:
            list += [expression(key)]
            if token_table[key][0].id != ',':
                break
            if token_table[key][0].id in breaks:
                break
            advance(key, ',')
    return list


def braces(lid, rid):
    symbol(rid)

    @method(symbol(lid))
    def nud(self, key):
        self.first = []
        types = ['(NAME)', '(LITERAL)', '(SYMBOL)', '(OP)',
                 '(FUNC)']  # Not sure why this is here. Mirrored for brackets; [].
        breaks = [rid]

        self.first = argument_list(key, self.first, types, breaks)

        if len(self.first) <= 1:
            self.first = self.first[0]

        advance(key, rid)

        return self

    @method(symbol(rid))
    def led(self, key, first):
        self.first = first
        self.second = []
        types = ['(NAME)', '(LITERAL)', '(SYMBOL)']

        self.second = argument_list(key, self.second, types)
        advance(key, rid)

        return self


braces('(', ')')
braces('[', ']')
braces('{', '}')

symbol(':')
symbol(',')


@method(symbol('lambda'))
def nud(self, key):
    self.first = []

    self.first = argument_list(key, self.first)
    advance(key, ':')
    self.second = expression(key)

    return self


def f_enclosed(f, lid='(', rid=')'):
    @method(symbol('{0}'.format(f)))
    def nud(self, key):
        try:
            advance(key, lid)
            self.first = expression(key)
            advance(key, rid)
        except SyntaxError:
            self.first = expression(key, inf)

        return self


def double_f_enclosed(f, lid='(', rid=')'):
    @method(symbol('{0}'.format(f)))
    def nud(self, key):
        try:
            advance(key, lid)
            self.first = expression(key)

            advance(key, rid)
            advance(key, lid)

            self.second = expression(key)
            advance(key, rid)

        except SyntaxError:
            self.first = expression(key, inf)
            self.second = expression(key, inf)

        return self


def constant(id):
    @method(symbol(id))
    def nud(self):
        self.id = '(LITERAL)'
        self.value = id
        self.first = id
        return self.value

    @method(symbol(id))
    def __float__(self):
        return float(math_constants[self.value])


constant('e')
constant('pi')
constant('phi')

infix('+', 10)
prefix('+', 0)
infix('-', 10)
prefix('-', 0)
infix('*', 20)
infix('/', 20)
infixr('**', 30)
infixr('^', 30)

symbol('(SYMBOL)').nud = lambda self: self.value
symbol('(LITERAL)').nud = lambda self: self.value
symbol('(NAME)').nud = lambda self: self.value
symbol('(ENDMARKER)').nud = lambda self: self.value

for i in math_functions.keys():
    f_enclosed(i)
for i in latex_math_functions.keys():
    f_enclosed(i, '{', '}')
f_enclosed('print')

f_enclosed('D')
symbol('\\dfrac')
double_f_enclosed('\\dfrac', '{', '}')
symbol_table['\\dfrac'].value = '/'

_t = iter(math_functions.keys())
for i in latex_math_functions:
    symbol_table[i].value = next(_t)

#
'''
End Symbols.
Begin Main:
'''


#


def chain_expr(token0, expr0, key):
    token1, expr1, vars = token_table[key]
    expr0 = iter(expr0)
    expr_t = itertools.chain(expr0, expr1)
    token_table[key] = [token0, expr_t, vars]


def expression(key, rbp=0):
    t = token_table[key][0]

    advance(key)
    token = token_table[key][0]

    try:
        left = t().nud(key)
    except TypeError:
        left = t().nud()

    if token.id == '(ENDMARKER)':
        return left

    ids = [t.id, token.id]
    if '(OP)' not in ids:
        mul = symbol_table['*']
        expr = [token]
        chain_expr(mul, expr, key)

    while rbp < token_table[key][0].lbp:
        t = token_table[key][0]
        advance(key)
        left = t().led(key, left)

    return left


def parse(string, vars=None, key=None):
    global token_table

    if key:
        vars = token_table[key][2]
        key = id(string)
    else:
        key = id(string)

    tokens = tokenizer(string, vars)
    expr = iter_tokens(tokens)

    token = next(expr)
    token_table[key] = [token, expr, vars]

    return expression(key)
