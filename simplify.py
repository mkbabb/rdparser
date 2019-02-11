from parser_main import clone_symbol, create_symbol, parse
from parser_math import *
from symbols import Symbols, findSymbol, isSymbol


def _simplify(s, vars):
    try:
        s = simplify_internal(s, vars)
    except:
        pass
    return s


def implicit_power(s, sign='+'):
    if not hasattr(s, 'first'):
        traits = {
            'first': s,
            'second': '{0}1'.format(sign)
        }
        s = create_symbol(s, '^', traits)

    return s


def add_powers(self, other, symbol):
    added = False

    for n, i in enumerate(self.tlist):
        isf = isSymbol(i)

        if symbol != isf:
            isf = findSymbol(i, symbol)

        if symbol == isf:
            try:
                token = implicit_power(i, '+')

                if token.first == other.first:
                    tt = '({0} + {1})'.format(token.second, other.second)

                    try:
                        tt = parse(tt, self.vars).evaluate()
                    except:
                        pass

                    st = '{0}^{1}'.format(token.first, tt)
                    st = parse(st, self.vars)

                    self.tlist[n] = st
                    added = True
            except:
                pass
    if added:
        return self
    else:
        return False


def mul_powers(self, other, symbol):
    for n, i in enumerate(self.tlist):
        token = implicit_power(i, '+')

        tt = '({0} * {1})'.format(token.second, other.first)

        try:
            tt = parse(tt, self.vars).evaluate()
        except:
            pass

        st = '{0}^{1}'.format(token.first, tt)
        st = parse(st, self.vars)

        self.tlist[n] = st

    return self


class Cluster(object):
    def __init__(self, vars):
        self.vars = vars
        self.tlist = []
        self.slist = []
        self.token = None

    def add2(self, token, symbol=None):
        if token:
            self.token = token
            self.tlist += [token]

        if symbol:
            self.slist += [symbol]

        return self

    def eval_cluster(self):
        tv = []
        popped = []

        for n, i in enumerate(self.tlist):
            if hasattr(i, 'lbp'):
                try:
                    tv += ['{0}'.format(i.evaluate())]
                    popped += [n]
                except:
                    try:
                        if i.first.isdigit():
                            tv += [i.first]
                            self.tlist[n] = i.second
                    except:
                        pass
            elif not isinstance(i, Symbols):
                tv += [str(i)]
                popped += [n]

        if len(tv) > 1:
            tv = parse('*'.join(tv)).evaluate()
            for i in sorted(popped, reverse=True):
                del self.tlist[i]
            self.tlist.insert(0, tv)

    def Token(self):
        st = '*'.join(map(str, self.tlist))
        t = parse(st, self.vars)
        self.token = t

    def __mul__(self, other):
        token = implicit_power(other.token, '+')

        symbol = token.first
        t = add_powers(self, token, symbol)

        if not t:
            self.add2(other.token, symbol)
        else:
            self = t

        return self

    def __pow__(self, other, modulo=None):
        if not isinstance(other, Cluster):
            raise SyntaxError('Not another Cluster object!')

        token = implicit_power(other.token, '+')

        symbol = token.first
        t = mul_powers(self, token, symbol)

        if not t:
            self.add2(token.first, symbol)
        else:
            self = t

        return self

    def __str__(self):
        return ', '.join(map(str, self.tlist))

    def __eq__(self, other):
        if not isinstance(other, Cluster):
            raise TypeError('Not another Cluster object!')

        tsort = sorted(self.tlist)
        osort = sorted(other.tlist)
        if tsort == osort:
            return True
        return False

    def __len__(self):
        return len(self.tlist)

    def __iter__(self):
        return (self[i] for i in range(len(self)))

    def __getitem__(self, key):
        if isinstance(key, slice):
            indicies = key.indices(len(self))
            if key.step:
                return (self[i:i + key.step] for i in range(*indicies))
            else:
                start = indicies[0]
                end = indicies[1]
        else:
            return self.tlist[key]
        return self.tlist[start:end]


class PolyCluster(object):
    def __init__(self, vars):
        self.vars = vars
        self.tlist = []
        self.slist = []
        self.token = None

    def add2(self, token, symbol=None):
        mod = False

        if token and not mod:
            self.tlist += [token]
            mod = True

        if symbol:
            self.slist += [symbol]

        return self

    def __str__(self):
        return ', '.join(map(str, self.tlist))

    def __eq__(self, other):
        if not isinstance(other, Cluster):
            raise TypeError('Not another Cluster object!')

        tsort = sorted(self.tlist)
        osort = sorted(other.tlist)
        if tsort == osort:
            return True
        return False

    def __len__(self):
        return len(self.tlist)

    def __iter__(self):
        return (self[i] for i in range(len(self)))

    def __getitem__(self, key):
        if isinstance(key, slice):
            indicies = key.indices(len(self))
            if key.step:
                return (self[i:i + key.step] for i in range(*indicies))
            else:
                start = indicies[0]
                end = indicies[1]
        else:
            return self.tlist[key]
        return self.tlist[start:end]


def simplify_internal(s, vars):
    func = s.value
    _dict = s.__dict__
    cluster = None

    if 'third' in _dict:
        pass
    elif 'second' in _dict:
        first = _simplify(s.first, vars)
        second = _simplify(s.second, vars)

        s.first = first
        s.second = second

        isf = isSymbol(first)
        iss = isSymbol(second)

        if hasattr(first, 'cluster') and first.cluster:
            cluster1 = first.cluster
        else:
            cluster1 = Cluster(vars=vars).add2(first, isf)

        if hasattr(second, 'cluster') and second.cluster:
            cluster2 = second.cluster
        else:
            cluster2 = Cluster(vars=vars).add2(second, iss)

        if func == '*':
            cluster = cluster1 * cluster2

        elif func == '^':
            cluster = pow(cluster1, cluster2)

        try:
            cluster.eval_cluster()
        except:
            pass

        if cluster:
            cluster.Token()
            s = cluster.token
            s.cluster = cluster
            s.cluster.token = s

        return s

    elif 'first' in _dict and func in math_functions.keys():
        first = _simplify(s.first, vars)
        s.first = first
        return s

    else:
        first = _simplify(s.first, vars)
        return first
    return s
