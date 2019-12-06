# Lispy: Scheme Interpreter in Python
# (c) Peter Norvig, 2010-16; See http://norvig.com/lispy.html
# Updated by Brian Lutz (Dec. 5, 2019) for PicnicHealth
from __future__ import division
import operator as op

# Types
Symbol = str  # A Lisp Symbol is implemented as a Python str
List = list  # A Lisp List is implemented as a Python list
Number = (int, float)  # A Lisp Number is implemented as a Python int or float
AtomicTypes = (float, int, str)


# Parsing: parse, tokenize, and read_from_tokens
def parse(program):
    """
    Converts a string into a tokenized string, then converts into a scheme expression. The scheme expression is a
    list expression containing other list expressions and/or atomic expressions.
    :param program: "(1 (1 1 +) +)"
    :return: [[1, [1, 1, "+"], "+"]
    """
    return read_from_tokens(tokenize(program))


def tokenize(s):
    """
    Takes a string *s* and adds a space before and after each opening and closing parenthesis, then splits the string on
    spaces.
    :param s: "(1 2 +)"
    :return: ["(", "1", "2", "+", ")"]
    """
    return s.replace("(", " ( ").replace(")", " ) ").split()


def read_from_tokens(tokens):
    """
    Takes a token string and turns it into a scheme expression. Characters that represent integers or floats
    are converted to their types. Symbols like "a" or "b" are left as strings.
    :param tokens: ["(", "1", "(", "1", "1", "+", ")", "+", ")"]
    :return:[[1, [1, 1, "+"], "+"]
    """
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF while reading")
    token = tokens.pop(0)
    if "(" == token:
        res = []
        while tokens[0] != ")":
            res.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return res
    elif ")" == token:
        raise SyntaxError("unexpected )")
    else:
        return atom(token)


def atom(token):
    """
    Converts atomic expressions represented as raw strings to their actual type. Supported types are int, float, and
    if all else fails, str.
    :param token: "a" | "1" | "1.1"
    :return: "a" | 1 | 1.1
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)  # Equivalent to str(token)


# Environments
def standard_env():
    """
    Creates an environment object and adds the normal forms and some special forms to the environment. These forms
    just do I/O. That means no environment modification or control flow.
    :return: Functions for the forms [+, -, *, /, car, cdr, cons, eq?, atom?]
    """
    """An environment with some Scheme standard procedures."""
    env = Env()
    env.update(
        {
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "car": lambda x: x[0],
            "cdr": lambda x: x[1:] if len(x) > 2 else x[1],
            "cons": lambda x, y: [x] + y if isinstance(y, list) else [x, y],
            "eq?": op.eq,
            "atom?": lambda x: type(x) in AtomicTypes,
        }
    )
    return env


class Env(dict):
    """An environment: a dict of {'var':val} pairs, with an outer Env."""

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        """Find the innermost Env where var appears."""
        return self if (var in self) else self.outer.find(var)


# Interaction: A REPL
def repl(prompt="lis.py> ", env=None):
    """A prompt-read-eval-print loop."""
    env = env or standard_env()
    while True:
        val = eval(parse(input(prompt)), env)
        if val is not None:
            print(lispstr(val))


def lispstr(exp):
    """Convert a Python object back into a Lisp-readable string."""
    if isinstance(exp, List):
        return "(" + " ".join(map(lispstr, exp)) + ")"
    else:
        return str(exp)


# Procedures
class Procedure(object):
    """A user-defined Scheme procedure."""

    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))


# eval
def eval(x, env):
    """
    Takes in a scheme expression *x* and evaluates it using environment *env*. List expressions get a call to eval
    recursively.
    :param x: [[1, [1, 1, "+"], "+"]
    :param env: {}
    :return: 3
    """
    if isinstance(x, Symbol):  # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x
    keyword = x.pop()
    if keyword in {"quote", "'"}:  # (quote exp)
        return (
            x[0]
            if len(x) == 2
            else " ".join(str(exp) for exp in x)
            .replace("[", "(")
            .replace("]", ")")
            .replace("'", "")
            .replace(",", "")
        )
    elif keyword == "cond":  # (if test conseq alt)
        for cond_branch in x:
            branch, cond = cond_branch[:-1], cond_branch[-1]
            if cond == "else" or eval(cond, env):
                return eval(branch, env)
    elif keyword == "define":  # (define var exp)
        var, exp = x
        env[var] = eval(exp, env)
    elif keyword == "lambda":  # (lambda (var...) body)
        parms, body = x
        return Procedure(parms, body, env)
    else:  # (proc arg...)
        proc = eval(keyword, env)
        args = [eval(exp, env) for exp in x] if x[-1] != "'" else x[:-1]
        return proc(*args)


if __name__ == "__main__":
    repl()
