import keyword
import code

ILLEGAL = ("abs", "divmod", "input", "open", "staticmethod", "all", "enumerate",
           "int", "ord", "str", "any", "eval", "isinstance", "pow", "sum",
           "basestring", "execfile", "issubclass", "print", "super", "bin",
           "file", "iter", "property", "tuple", "bool", "filter", "len",
           "range", "type", "bytearray", "float", "list", "raw_input", "unichr",
           "callable", "format", "locals", "reduce", "unicode", "chr",
           "frozenset", "long", "reload", "vars", "classmethod", "getattr",
           "map", "repr", "xrange", "cmp", "globals", "max", "reversed", "zip",
           "compile", "hasattr", "memoryview", "round", "__import__", "complex",
           "hash", "min", "set", "delattr", "help", "next", "setattr", "dict",
           "hex", "object", "slice", "dir", "id", "oct", "sorted", "'", '"',
           "'''", '"""', '[', ']', '`', ',', "exec", "eval")
ILLEGAL += tuple(keyword.kwlist)

class IllegalExpressionError(Exception): pass

def filter(expression, illegal=ILLEGAL):
    for token in illegal:
        if token in expression:
            raise IllegalExpressionError("Found illegal '{}' in expression".format(token))
    else:
        return expression

def filtered_input(prompt):
    return filter(raw_input(prompt))

def eval_loop():
    while True:
        try:
            output = code.interact("", filtered_input)
        except IllegalExpressionError:
            print("Illegal expression not processed")


if __name__ == "__main__":
    eval_loop()

#x=(0,1);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x#,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x=(x,x);x
#
#...prints out 2^128 nested (0,1) values (aka forever)...
