# modified from rosetta code http://rosettacode.org/wiki/Parsing/Shunting-yard_algorithm#Python
from collections import namedtuple
import operator
import StringIO
import tokenize as pytokenize

class EvalError(Exception): pass

def raise_error(symbol):
    raise EvalError("Attempted to call non-operator symbol '{}'".format(symbol))

OpInfo = namedtuple('OpInfo', 'prec assoc')
L, R = 'Left Right'.split()
FUNCTION_INFO = OpInfo(prec=5, assoc=L)

_OPS = {
 '^': (OpInfo(prec=4, assoc=R), (operator.pow, 2)),
 '*': (OpInfo(prec=3, assoc=L), (operator.mul, 2)),
 '/': (OpInfo(prec=3, assoc=L), (operator.div, 2)),
 '+': (OpInfo(prec=2, assoc=L), (operator.add, 2)),
 '-': (OpInfo(prec=2, assoc=L), (operator.sub, 2)),
 '(': (OpInfo(prec=9, assoc=L), (raise_error, 0)),
 ')': (OpInfo(prec=0, assoc=L), (raise_error, 0)),
"max" : (FUNCTION_INFO, (max, 2)),
"min" : (FUNCTION_INFO, (min, 2)),
"abs" : (FUNCTION_INFO, (abs, 1))
 }

NUM, LPAREN, RPAREN = 'NUMBER ( )'.split()

def tokenize(inp, operators=_OPS):
    'Inputs an expression and returns list of (TOKENTYPE, tokenvalue)'
    tokens = [item[1] for item in pytokenize.generate_tokens(StringIO.StringIO(inp).readline)]
    tokenvals = []
    for token in tokens:
        if token in operators:
            #print token, operators[token][0]
            #raw_input()
            tokenvals.append((token, operators[token][0]))
        #elif token in (LPAREN, RPAREN):
        #    tokenvals.append((token, token))
        else:
            tokenvals.append((NUM, token))
    return tokenvals

def shunting(tokenvals, operators=_OPS):
    outq, stack = [], []
    for token, val in tokenvals:
        if token is NUM:
            outq.append(val)
        elif token in operators:
            t1, (p1, a1) = token, val
            while stack:
                t2, (p2, a2) = stack[-1]
                if (a1 == L and p1 <= p2) or (a1 == R and p1 < p2):
                    if t1 != RPAREN:
                        if t2 != LPAREN:
                            stack.pop()
                            outq.append(t2)
                        else:
                            break
                    else:
                        if t2 != LPAREN:
                            stack.pop()
                            outq.append(t2)
                        else:
                            stack.pop()
                            break
                else:
                    break
            if t1 != RPAREN:
                stack.append((token, val))

    outq.extend(stack.pop()[0] for count in range(len(stack)))
    return ' '.join(outq)

def prepare(expression, operators=_OPS):
     # space facilitates replacing variables
    return ' ' + shunting(tokenize(expression, operators), operators).replace(',', ' ')

def evaluate_expression(expression, variables, functions, operators=_OPS):
    operators = operators.copy()
    operators.update(dict((key, (OpInfo(prec=5, assoc=L), value)) for key, value in functions.items()))
    rpe = prepare(expression, operators)
    return evaluate_rpe(rpe, variables, operators)

def evaluate_rpe(rpe, variables, operators=_OPS):
    stack = []
    for token in rpe.split():
        if token not in operators:
            if token in variables:
                stack.append(variables[token])
            else:
                stack.append(int(token))
        else:
            operation, arity = operators[token][1]
            #print("Evaluating: {}({}) (arity {})".format(operation, stack[-arity:], arity))
            stack.append(operation(*stack[-arity:]))
            del stack[-arity - 1:-1]
    return stack.pop()


class Expression(object):

    def __init__(self, expression, functions=None, operators=_OPS):
        self.operators = operators = operators.copy()
        if functions is not None:
            operators.update(dict((key, (OpInfo(prec=5, assoc=L), value)) for key, value in functions.items()))
        self.rpe = prepare(expression, operators)

    def __call__(self, **variables):
        return evaluate_rpe(self.rpe, variables, self.operators)


class Monovariate_Function(object):

    def __init__(self, expression, variable_name, functions=None, operators=_OPS):
        self.operators = operators = operators.copy()
        if functions is not None:
            operators.update(dict((key, (OpInfo(prec=5, assoc=L), value)) for key, value in functions.items()))
        self.rpe = prepare(expression, operators).replace(',', ' ')
        self.variable_name = variable_name

    def __call__(self, argument):
        return evaluate_rpe(self.rpe, {self.variable_name : argument}, self.operators)


if __name__ == '__main__':
    #infix = "x + y*z / (a - b ) ^z ^   x"
    #expression = 'x + (x ^ 2) + (x ^ 3)'
    #expression = '1 + 1 ^ 2 + 1'
    #expression = "2 ^ 8"
    #expression = "2 ^ 8 - 5"
    #expression = "3 - 3 - 2"
    #expression = "(identity(range) * add(identity(aoe), identity(NoT)) * effect_cost) - identity(grace)"
    #expression = "add(ternary(1, 2, 3), ternary(2, 3, 4))"
    #expression = "((1 * 2) + 3) + ((2 * 3) + 4)"
    #expression = "identity(square(2 * identity(x) + identity(x)) ^ (square(2) / 2))"
    #expression = "identity(square(2 * identity(x) + identity(x))) ^ (square(2) / 2)"
    expression = "identity(add(y, add(x, x)))"
    print("Evaluating: {}".format(expression))
    variables = {'x' : 2, 'y' : 3, 'z' : 4, 'a' : 5, 'b' : 6,
                 "range" : 10, "aoe" : 1, "NoT" : 1, "effect_cost" : 1, "grace" : 1}
    identity = lambda x: x
    square = lambda x: x ** 2
    add = lambda x, y: x + y
    ternary = lambda x, y, z: (x * y) + z
    functions = {"identity" : (identity, 1), "square" : (square, 1),
                 "add" : (add, 2), "ternary" : (ternary, 3)}
    #print evaluate_expression(expression, variables, functions)
    exp = Expression(expression, functions)
    print exp(**variables)
