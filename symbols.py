import re


def isSymbol(s):
    if isinstance(s, Symbols):
        return s

    elif hasattr(s, '__dict__'):
        for i, j in s.__dict__.items():
            if isinstance(j, Symbols):
                return j
            elif not hasattr(j, 'lbp'):
                pass
            else:
                t = isSymbol(j)
                if t:
                    return t
    return False


def findSymbol(s, target):
    if str(s) == target:
        return target

    elif hasattr(s, '__dict__'):
        for i, j in s.__dict__.items():
            if str(j) == target:
                return target
            elif not hasattr(j, 'lbp'):
                pass
            else:
                t = findSymbol(j, target)
                if t:
                    return t
    return False


class Symbols(object):
    def __init__(self, string):
        l0 = []
        self.tokens = {}

        if isinstance(string, list):
            l0 = string

        elif isinstance(string, str):
            if ',' in string:
                string = re.sub('\s', '', string)
                l0 = re.split(',', string)
            else:
                self.string = string
                self.tokens.update({string: self})

        if len(l0) > 0:
            for n, i in enumerate(l0):
                self.tokens.update({i: Symbols(i)})

        self.value = None
        self.id = string

    def set_value(self, value):
        for i in self.tokens.keys():
            self.tokens[i].value = value[i]

    def __str__(self):
        if self.value:
            return str(self.value)
        return self.id

    def __repr__(self):
        if self.value:
            return str(self.value)
        return self.id

    def __iter__(self):
        for i, j in self.tokens.items():
            yield j

    def __float__(self):
        try:
            return float(self.value)
        except TypeError:
            return complex(self.value)

    def __complex__(self):
        return complex(self.value)

    def __eq__(self, other):
        if not isinstance(other, Symbols):
            return False

        if not self.value:
            if self.id == other.id:
                return True
        else:
            if self.value == other.value:
                return True

        return False
