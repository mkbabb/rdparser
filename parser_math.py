import math
import operator

inf = float('inf')

sec = lambda x: 1 / math.cos(x)
csc = lambda x: 1 / math.sin(x)
cot = lambda x: 1 / math.tan(x)

asec = lambda x: 1 / math.acos(x)
acsc = lambda x: 1 / math.asin(x)
acot = lambda x: 1 / math.atan(x)

sech = lambda x: 1 / math.cosh(x)
csch = lambda x: 1 / math.sinh(x)
coth = lambda x: 1 / math.tanh(x)

asech = lambda x: 1 / math.acosh(x)
acsch = lambda x: 1 / math.asinh(x)
acoth = lambda x: 1 / math.atanh(x)

math_functions = {
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'sech': sech,
    'csch': csch,
    'coth': coth,
    'arcsinh': math.asinh,
    'arccosh': math.acosh,
    'arctanh': math.atanh,
    'arcsech': asech,
    'arccsch': acsch,
    'arccoth': acoth,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sec': sec,
    'csc': csc,
    'cot': cot,
    'arcsin': math.asinh,
    'arccos': math.acosh,
    'arctan': math.atanh,
    'arcsec': asec,
    'arccsc': acsc,
    'arccot': acot,
    'sqrt': math.sqrt,
    'log': math.log,
    'abs': abs,
    'ceil': math.ceil,
    'floor': math.floor,
    'round': round,
    'exp': math.exp,
    'D': None,
    'erf': None,
}

latex_math_functions = {'\\{0}'.format(i): j for i, j in math_functions.items()}

math_derivatives = {
    'sin': lambda x: 'cos({0})'.format(x),
    'cos': lambda x: '-sin({0})'.format(x),
    'tan': lambda x: '(sec({0}) ^ 2)'.format(x),
    'sec': lambda x: 'sec({0}) * tan({0})'.format(x),
    'csc': lambda x: '-csc({0}) * cot({0})'.format(x),
    'cot': lambda x: '-csc({0})'.format(x),
    'arcsin': lambda x: '1/sqrt(1 - ({0})^2)'.format(x),
    'arccos': lambda x: '-1/sqrt(1 - ({0})^2)'.format(x),
    'arctan': lambda x: '1/(1 + ({0})^2)'.format(x),
    'sinh': lambda x: 'cosh({0})'.format(x),
    'cosh': lambda x: '-sinh({0})'.format(x),
    'tanh': lambda x: '(sech({0}) ^ 2)'.format(x),
    'sech': lambda x: 'sech({0}) * tanh({0})'.format(x),
    'csch': lambda x: '-csch({0}) * coth({0})'.format(x),
    'coth': lambda x: '-(csch({0}) ^ 2)'.format(x),
    'log': lambda x: '1/({0})'.format(x),
    'e': lambda x: 'e^({0})'.format(x),
    'erf': lambda x: '-2 * e^(({0}) ^ 2) / sqrt(pi)'.format(x)
}

math_constants = {
    'e': math.exp(1),
    'pi': math.pi,
    'phi': (math.sqrt(5) + 1) / 2
}

latex_operators = {
    '\dfrac': operator.truediv
}

math_operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '^': operator.pow,
    '**': operator.pow,
    '(': None,
    ')': None,
}

# math_functions.update(math_operators)
