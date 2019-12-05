import operator
from typing import List, Union, Deque, Optional, Dict
from collections import deque
import argparse


AtomicType = Union[str, float, int]
AtomicTypes = (str, float, int)
NumberTypes = (float, int)
Symbol = str


def define(ast: Deque[str], environment: Dict) -> None:
    try:
        symbol = ast[0]
        value = evaluate_ast(ast[1], environment)
    except IndexError:
        raise SyntaxError("Define lists must be two elements long.")
    if symbol in environment:
        raise ValueError(f"Cannot redefine symbol {symbol}")
    else:
        environment[symbol] = value


def condition(ast: List[str], environment: Dict) -> AtomicType:
    for cond_branch in ast:
        branch, cond = cond_branch[:-1], cond_branch[-1]
        if cond == "else" or evaluate_ast(cond, environment):
            return evaluate_ast(branch, environment)


COMPLEX_FORMS = {
    "define": define,
    "cond": condition
}

NORMAL_FORMS = {
    "+": lambda x, y: operator.add(x, y),
    "-": lambda x, y: operator.sub(x, y),
    "/": lambda x, y: operator.truediv(x, y),
    "*": lambda x, y: operator.mul(x, y),
    "eq?": lambda x, y: operator.eq(x, y),
    "cons": lambda x, y: [x, y]
}


FORMS = {}
FORMS.update(NORMAL_FORMS)
FORMS.update(COMPLEX_FORMS)


def tokenize_string(string: str) -> Deque[str]:
    return deque(string.replace("(", " ( ").replace(")", " ) ").split())


def assemble_ast_from_tokens(tokens: Deque[str]) -> Union[Symbol, List]:
    if len(tokens) == 0:
        raise ValueError("Unexpected EOF")
    elif tokens[0] == "(":
        tokens.popleft()
        res = []
        while tokens[0] != ")":
            res.append(assemble_ast_from_tokens(tokens))
        tokens.popleft()
        return res
    elif tokens[0] == "(":
        raise ValueError("Unexpected closure")
    else:
        if tokens[0].isdigit():
            res = int(tokens[0])
        elif tokens[0].isdecimal():
            res = float(tokens[0])
        else:
            res = tokens[0]
        tokens.popleft()
        return res


def parse_lisp_from_string(string: str) -> Union[List, str]:
    return assemble_ast_from_tokens(tokenize_string(string))


def evaluate_ast(ast: Union[Symbol, List], environment: Dict) -> AtomicType:
    if type(ast) in NumberTypes:
        return ast
    elif isinstance(ast, Symbol):
        try:
            return environment[ast]
        except KeyError:
            raise ValueError(f"Undefined symbol {ast}")
    keyword = ast.pop()
    if keyword == "'":
        return ast[0]
    elif keyword == "atom?":
        return type(ast[0]) in AtomicTypes and not (isinstance(ast[0], str) and ast[0] == "'")
    elif keyword == "car":
        return evaluate_ast(ast, environment)[0]
    elif keyword == "cdr":
        res = evaluate_ast(ast, environment)
        return res[1] if len(res) < 3 else res[1:]
    elif keyword in NORMAL_FORMS:
        x, y = ast
        return FORMS[keyword](evaluate_ast(x, environment), evaluate_ast(y, environment))
    elif keyword in COMPLEX_FORMS:
        return FORMS[keyword](ast, environment)
    else:
        raise ValueError(f"Undefined symbol {keyword}")


def execute_statement(statement: str, environment: Dict = None) -> AtomicType:
    return evaluate_ast(parse_lisp_from_string(statement), environment or {})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a basic file into LISP statements and execute them.")
    parser.add_argument("--file", type=str)
    args = parser.parse_args()
    try:
        f = open(args.file)
    except FileNotFoundError:
        print("File not found.")
        quit()
    environment = {}
    for line in f.readlines():
        res = execute_statement(line, environment)
        if res:
            print(res)
