import math
import re
from parser import (Derivative, Symbols, cells, parse, pprint,
                    simplify_internal, subs, to_latex)

import numpy as np

sin = np.sin
cos = np.cos

# syms = Symbols('x, y, z, b')
# string = 'sin(tan(2*x))'
# string = '((sec(x))^2)'
# string = 'e^x'
# string = '3*x*y*4*z*x + 3*x'
# string = '3*(x^2^2)*y^1*z^3*x*x'
# string = '2^2^x * 2^2^x'
# string = '2*x^2*y^3*z^4*x^x*y^y*z^2^2'
# string = '2*x*2*y*10 + 3*x*2*4*y*7'
# string = '2*5*b^2*z^2*2*x*2*4*y*7*tan(x) + 2*3*4*5*x'
# string = '2*3*4*x'
# string = '2*x^2*4*x^10'
# string = 'x^2*x^x'
# string = '2*log(378)*log(sec(x))'
# string = 'sin(tan(x))'
# string = 'x + x + x'
# string = '-2 + 2'
# string = 'y*y*y*y*y^7 + x^2*x^88 + tan(x)^2*tan(x)^7'
# string = 'sin(3*x) + cos(10*x)'
# string = '(2 + x) / z + 3/(x/y) + 1/(3/(5/7)) + 22'
string = '1/(88*x + y + z/8)'
# string = 'tan(x)^2*tan(x)^7'

# string = 'x*y*z*x*x*x*y*x*z'

# string = '2*e + 2e'
# string = '(x+2)/(3^x-1)'
# string = '((ac + bd)/(c^2+d^2))*x + ((ad-bc)/(c^2+d^2))*log(c*cos(x) + d*sin(x))'
# string = 'x/((x + 3)/(y + 2)) + 2/x + sin(x/(y+2)) + x/(y+2)'
# string = 'x + 1'
# string = 'sin(3*x^2*y + e^(x*y^3))'
# string = 'sin(x)/cos(x)'
# string = 'x*tan(x)'
# string = 'sin(3*x^2*y + e^(x*y^3))'

symbs = Symbols('x, y, z')
vars = [i.id for i in symbs]
values = {'x': 1, 'y': 4}
print('\nString: {0}'.format(string))

t = parse(string, vars)
lt = pprint(t, vars)

max_len = len(str(max(cells, key=lambda x: len(x)))) // 2

N, M = cells.shape

for i in range(N):
    for j in range(M):
        current_cell = cells[i][j]
        current_len = len(str(current_cell))

        left_pad = ' ' * (math.ceil((max_len - current_len) / 2))
        right_pad = ' ' * (math.floor((max_len - current_len) / 2))

        cells[i][j] = '{0}{1}{2}'.format(left_pad, current_cell, right_pad)


s = ''
for i in cells[::-1]:
    s += '\n'
    for j in i:
        if '{}'.format(j) != "0":
            s += j


print(s)

# fn = lambda x: subs(t, {'x': x}).evaluate()
# print(fn(10))


# print('\nParsed String: {0}'.format(t))
# print('\n')
#
# t = simplify_internal(t, vars)
# print('\nSimplified String: {0}'.format(t))
