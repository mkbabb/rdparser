from parser_main import parse
from parser_math import *
from symbols import Symbols, findSymbol, isSymbol


def product_rule(p1, p2):
    if p1 and p2:
        string = '({0}) + ({1})'.format(p1, p2)
    elif p1 and not p2:
        string = '{0}'.format(p1)
    elif p2 and not p1:
        string = '{0}'.format(p2)
    return string


def quotient_rule(p1, p2, y):
    if y == '1':
        denom = None
    else:
        denom = '({0})^2'.format(y)

    if p1 and p2:
        num = '(({0}) - ({1}))'.format(p2, p1)
    elif p1 and not p2:
        num = '-({0})'.format(p1)
    elif p2 and not p1:
        num = '({0})'.format(p2)

    if denom:
        string = num + '/' + denom
    else:
        string = num

    return string


def exponent_rule(x, y, vars):
    prod = parse('({0}) * log({1})'.format(y, x), vars)
    prod = derivative_internal(prod, vars).derivative
    string = '(({0}) * (({1}) ^ ({2})))'.format(prod, x, y)
    return string


def derivative_rules(x, y, dx, dy, func, vars):
    p1 = [str(x), str(dy)]
    p2 = [str(y), str(dx)]

    if '0' in p1:
        p1 = None
    else:
        if p1[0] == '1':
            p1.pop(0)
        elif p1[1] == '1':
            p1.pop(1)

    if '0' in p2:
        p2 = None
    else:
        if p2[0] == '1':
            p2.pop(0)
        elif p2[1] == '1':
            p2.pop(1)

    if p1:
        p1 = '*'.join(p1)
    if p2:
        p2 = '*'.join(p2)

    if func == '*':
        return product_rule(p1, p2)
    elif func == '/':
        return quotient_rule(p1, p2, y)
    elif func in ['**', '^']:
        return exponent_rule(x, y, vars)
    else:
        if dx == '0' and dy != '0':
            t = '{0}'.format(dy)
        elif dy == '0' and dx != '0':
            t = '{0}'.format(dx)
        elif dx == dy == '0':
            t = '0'
        else:
            t = '({0}){1}({2})'.format(dx, func, dy)
        return t


def _deriv(s, vars):
    try:
        s = derivative_internal(s, vars)
    except AttributeError:
        pass
    return s


def derivative_internal(s, vars):
    func = s.value
    _dict = s.__dict__

    if 'third' in _dict:
        pass
    elif 'second' in _dict:
        first = _deriv(s.first, vars)
        second = _deriv(s.second, vars)

        dfirst = dsecond = '0'

        if isinstance(first, Symbols):
            dfirst = '1'

        if isinstance(second, Symbols):
            dsecond = '1'

        if hasattr(first, 'derivative'):
            if first.derivative:
                dfirst = first.derivative

        if hasattr(second, 'derivative'):
            if second.derivative:
                dsecond = second.derivative

        isf = isSymbol(first)
        iss = isSymbol(second)

        if func in ['+', '-']:
            if not isf:
                first = '0'
            elif not iss:
                second = '0'

        if isf and iss or (isf or iss) and func == '^':
            t = derivative_rules(first, second, dfirst, dsecond, func, vars)

        elif iss:
            if (first or dsecond) == '0':
                t = '0'
            else:
                t = '({0}){1}({2})'.format(first, func, dsecond)

        elif isf:
            if (dfirst or second) == '0':
                t = '0'
            else:
                t = '({0}){1}({2})'.format(dfirst, func, second)
        else:
            return s

        s.derivative = t
        return s

    elif 'first' in _dict and func in math_functions.keys():
        first = _deriv(s.first, vars)
        isf = isSymbol(s.first)

        if not isf:
            return s

        if isinstance(first, Symbols):
            t = '{0}'.format(math_derivatives[func](s.first))
            s.derivative = t
            return s

        if hasattr(first, 'derivative'):
            if first.derivative:
                first = first.derivative

        t = '({0})*({1})'.format(math_derivatives[func](s.first), first)

        s.derivative = t
        return s

    else:
        first = _deriv(s.first, vars)
        return first
    return s


def Derivative(f, vars):
    if hasattr(f, 'lbp'):
        t = derivative_internal(f, vars)
    else:
        t = parse(f, vars=vars)
        t = derivative_internal(t, vars)

    d = t.derivative
    d = parse(d, vars)
    t.derivative = d

    return t
